"""
HSM Token Signer
"""

from typing import List, Optional, Dict, Any
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# HSM support (optional import)
try:
    import PyKCS11 as PK11
    HSM_AVAILABLE = True
except ImportError:
    HSM_AVAILABLE = False

from ..core.validators import CertificateValidator
from ..core.xml_signing import sign_xml_document
from ..models.certificate_models import HSMConfig, HSMTokenInfo
from ..models.signature_models import SignatureAlgorithm
from ..exceptions import HSMError, CertificateNotFoundError, SigningError

class HSMSigner:
    """
    HSM token integration for signing
    """

    def __init__(self, config: HSMConfig):
        """
        Initialize HSM signer

        Args:
            config: HSM configuration
        """
        if not HSM_AVAILABLE:
            raise HSMError("PyKCS11 not available - install with: pip install PyKCS11")

        self.config = config
        self.validator = CertificateValidator(config.validation_config.trusted_roots_folder)
        self.dll_path = config.dll_path or self._find_hsm_dll()

        if not self.dll_path:
            raise HSMError("No HSM DLL found")

        self.pkcs11 = PK11.PyKCS11Lib()
        self.pkcs11.load(self.dll_path)
        self.session = None
        self.keyid = None
        self.token_info = None

    def _find_hsm_dll(self) -> Optional[str]:
        """Find available HSM DLL"""
        import os

        # Default HSM DLL paths
        hsm_dll_paths = [
            r"C:\Windows\System32\SignatureP11.dll",
            r"C:\Windows\System32\eToken.dll",
            r"C:\Windows\System32\eps2003csp11v2",
            r"C:\Windows\System32\CryptoIDA_pkcs11.dll"
        ]

        for dll_path in hsm_dll_paths:
            if os.path.exists(dll_path):
                try:
                    # Test if this DLL has any connected tokens
                    test_pkcs11 = PK11.PyKCS11Lib()
                    test_pkcs11.load(dll_path)
                    slots = test_pkcs11.getSlotList(tokenPresent=True)

                    if slots:
                        print(f"[+] Found HSM DLL with connected tokens: {dll_path}")
                        print(f"[+] Found {len(slots)} token(s) connected")
                        return dll_path
                    else:
                        print(f"[+] Found HSM DLL but no tokens connected: {dll_path}")

                except Exception as e:
                    print(f"[+] HSM DLL found but failed to load: {dll_path} - {e}")
                    continue

        print(f"[!] No HSM DLL found with connected tokens")
        return None

    @staticmethod
    def get_all_available_tokens() -> List[Dict[str, Any]]:
        """Get tokens from all available HSM DLLs"""
        if not HSM_AVAILABLE:
            print("PyKCS11 not available - install with: pip install PyKCS11")
            return []

        import os

        hsm_dll_paths = [
            r"C:\Windows\System32\SignatureP11.dll",
            r"C:\Windows\System32\eToken.dll",
            r"C:\Windows\System32\eps2003csp11v2",
            r"C:\Windows\System32\CryptoIDA_pkcs11.dll"
        ]

        all_tokens = []

        for dll_path in hsm_dll_paths:
            if os.path.exists(dll_path):
                try:
                    test_pkcs11 = PK11.PyKCS11Lib()
                    test_pkcs11.load(dll_path)
                    slots = test_pkcs11.getSlotList(tokenPresent=True)

                    if slots:
                        print(f"[+] Checking tokens in DLL: {dll_path}")
                        for slot in slots:
                            try:
                                token = test_pkcs11.getTokenInfo(slot)
                                actual_label = token.label.rstrip('\x00 ')
                                all_tokens.append({
                                    'slot': slot,
                                    'label': actual_label,
                                    'manufacturer': token.manufacturerID.rstrip('\x00 '),
                                    'model': token.model.rstrip('\x00 '),
                                    'serial': token.serialNumber.rstrip('\x00 '),
                                    'dll_path': dll_path
                                })
                            except PK11.PyKCS11Error:
                                continue
                    else:
                        print(f"[+] No tokens found in DLL: {dll_path}")

                except Exception as e:
                    print(f"[+] Failed to check DLL: {dll_path} - {e}")
                    continue

        return all_tokens

    def auto_login(self, pin: str, max_retries: int = 3) -> bool:
        """
        Login to HSM token with protection against locking

        Args:
            pin: HSM token PIN
            max_retries: Maximum number of PIN retries before stopping (default: 3)

        Returns:
            True if login successful

        Raises:
            HSMError: If login fails
        """
        try:
            slots = self.pkcs11.getSlotList(tokenPresent=True)
            if not slots:
                raise HSMError("No HSM tokens found")

            # Use first available token
            slot = slots[0]
            token = self.pkcs11.getTokenInfo(slot)
            actual_label = token.label.rstrip('\x00 ')
            print(f"[+] Using token: {actual_label}")

            # Check token status before attempting login
            print(f"[+] Token status - PIN count left: {getattr(token, 'ulPinCountLeft', 'Unknown')}")

            # Warning if PIN attempts are low
            pin_count_left = getattr(token, 'ulPinCountLeft', None)
            if pin_count_left is not None and pin_count_left <= 2:
                print(f"[!] WARNING: Only {pin_count_left} PIN attempts remaining before token locks!")
                print(f"[!] Please ensure PIN is correct before proceeding")

                # Give user chance to abort
                import time
                print("[!] Proceeding in 3 seconds... Press Ctrl+C to abort")
                try:
                    time.sleep(3)
                except KeyboardInterrupt:
                    raise HSMError("Login aborted by user to prevent token locking")

            self.session = self.pkcs11.openSession(slot, PK11.CKF_SERIAL_SESSION | PK11.CKF_RW_SESSION)

            # Attempt login with retry protection
            retry_count = 0
            while retry_count < max_retries:
                try:
                    self.session.login(pin)
                    print(f"[+] Successfully logged into HSM token")
                    return True

                except PK11.PyKCS11Error as e:
                    retry_count += 1
                    error_msg = str(e).lower()

                    if "pin incorrect" in error_msg or "authentication failed" in error_msg:
                        if retry_count < max_retries:
                            print(f"[!] PIN incorrect. Attempt {retry_count}/{max_retries}")
                            print(f"[!] Warning: {max_retries - retry_count} attempts remaining before stopping")

                            # Get new PIN for retry
                            import getpass
                            pin = getpass.getpass(f"Enter HSM token PIN (attempt {retry_count + 1}/{max_retries}): ")
                        else:
                            print(f"[!] Maximum PIN attempts ({max_retries}) reached - stopping to prevent token lock")
                            raise HSMError(f"Failed to login after {max_retries} attempts - stopped to prevent token locking")
                    else:
                        # Non-PIN related error, don't retry
                        raise HSMError(f"HSM login error: {e}")

            return False

        except PK11.PyKCS11Error as e:
            raise HSMError(f"PKCS#11 error during login: {e}")
        except Exception as e:
            raise HSMError(f"Failed to login to HSM token: {e}")

    def get_certificate(self) -> tuple:
        """
        Get certificate from HSM token

        Returns:
            Tuple of (key_handle, cert_bytes, cert)
        """
        if not self.session:
            if self.config.pin:
                self.auto_login(self.config.pin)
            else:
                raise HSMError("Not logged into HSM session and no PIN provided")

        try:
            pk11objects = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_CERTIFICATE)]
            )
            all_attributes = [PK11.CKA_VALUE, PK11.CKA_ID]

            valid_certs = []

            for obj in pk11objects:
                try:
                    attrs = self.session.getAttributeValue(obj, all_attributes)
                    attr_dict = dict(zip(all_attributes, attrs))
                    cert_bytes = bytes(attr_dict[PK11.CKA_VALUE])
                    keyid = bytes(attr_dict[PK11.CKA_ID])

                    cert = x509.load_der_x509_certificate(cert_bytes, backend=default_backend())

                    # Check if private key exists for this certificate
                    if not self._has_private_key(keyid):
                        cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                        print(f"[+] Skipping certificate (no private key): {cn}")
                        continue

                    # Check if certificate matches criteria
                    if not self.validator.matches_certificate_criteria(cert, self.config.certificate_filter):
                        continue

                    # Validate certificate for signing
                    if self.validator.validate_certificate_for_signing(cert, self.config.validation_config):
                        valid_certs.append((keyid, cert_bytes, cert))

                except PK11.PyKCS11Error:
                    continue

            if not valid_certs:
                raise CertificateNotFoundError("No valid signing certificates found that match the criteria")

            # Use first valid certificate
            keyid, cert_bytes, cert = valid_certs[0]
            cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
            print(f"[+] Found valid signing certificate with private key: {cn}")

            self.keyid = keyid
            self.cert = cert
            return keyid, cert_bytes, cert

        except Exception as e:
            raise HSMError(f"Error finding certificate: {e}")

    def _has_private_key(self, keyid: bytes) -> bool:
        """Check if private key exists for given key ID"""
        try:
            private_keys = self.session.findObjects([
                (PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY),
                (PK11.CKA_ID, keyid)
            ])
            return len(private_keys) > 0
        except PK11.PyKCS11Error:
            return False

    def sign_xml_content(self, xml_content: bytes, signature_params) -> bytes:
        """
        Sign XML content using HSM token

        Args:
            xml_content: XML content to sign
            signature_params: Signature parameters

        Returns:
            Signed XML content as bytes
        """
        # Get certificate if not already loaded
        if not hasattr(self, 'cert') or self.cert is None:
            self.get_certificate()

        try:
            # Use the complete XML signing implementation
            signed_xml = sign_xml_document(xml_content, self.cert, self, signature_params)
            return signed_xml

        except Exception as e:
            raise SigningError(f"Failed to sign XML content: {e}")

    def sign_data(self, data: bytes, signature_algorithm: SignatureAlgorithm) -> bytes:
        """
        Sign data using HSM token private key

        Args:
            data: Data to sign
            signature_algorithm: Signature algorithm to use

        Returns:
            Signature bytes
        """
        if not self.session or not self.keyid:
            raise SigningError("HSM not properly initialized")

        try:
            # Find private key object
            privKey = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY), (PK11.CKA_ID, self.keyid)]
            )

            if not privKey:
                raise SigningError("Private key not found in HSM token")

            privKey = privKey[0]

            # Get PKCS#11 mechanism for signing
            mechanism = self._get_pkcs11_mechanism(signature_algorithm)

            # Sign the data
            signature = self.session.sign(privKey, data, mechanism)
            return bytes(signature)

        except PK11.PyKCS11Error as e:
            raise SigningError(f"PKCS#11 error during signing: {e}")
        except Exception as e:
            raise SigningError(f"Error signing data with HSM: {e}")

    def _get_pkcs11_mechanism(self, signature_algorithm: SignatureAlgorithm):
        """Get PKCS#11 mechanism for signature algorithm"""
        mechanism_map = {
            SignatureAlgorithm.RSA_SHA1: PK11.Mechanism(PK11.CKM_SHA1_RSA_PKCS, None),
            SignatureAlgorithm.RSA_SHA256: PK11.Mechanism(PK11.CKM_SHA256_RSA_PKCS, None),
            SignatureAlgorithm.RSA_SHA384: PK11.Mechanism(PK11.CKM_SHA384_RSA_PKCS, None),
            SignatureAlgorithm.RSA_SHA512: PK11.Mechanism(PK11.CKM_SHA512_RSA_PKCS, None),
            SignatureAlgorithm.ECDSA_SHA1: PK11.Mechanism(PK11.CKM_ECDSA_SHA1, None),
            SignatureAlgorithm.ECDSA_SHA256: PK11.Mechanism(PK11.CKM_ECDSA_SHA256, None),
            SignatureAlgorithm.ECDSA_SHA384: PK11.Mechanism(PK11.CKM_ECDSA_SHA384, None),
            SignatureAlgorithm.ECDSA_SHA512: PK11.Mechanism(PK11.CKM_ECDSA_SHA512, None),
        }

        mechanism = mechanism_map.get(signature_algorithm)
        if not mechanism:
            raise SigningError(f"Unsupported signature algorithm: {signature_algorithm}")

        return mechanism

    def cleanup(self):
        """Cleanup HSM resources"""
        if self.session:
            try:
                self.session.logout()
                self.session.closeSession()
            except:
                pass