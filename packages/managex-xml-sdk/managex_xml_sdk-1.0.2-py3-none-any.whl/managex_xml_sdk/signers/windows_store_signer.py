"""
Windows Certificate Store Signer
"""

import base64
import tempfile
import subprocess
import json
import sys
import os
from typing import List, Optional
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Windows-specific imports
try:
    from win32 import win32crypt
    from win32.lib import win32cryptcon
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

from ..core.validators import CertificateValidator
from ..core.xml_signing import sign_xml_document
from ..models.certificate_models import CertificateInfo, WindowsStoreConfig
from ..models.signature_models import SignatureAlgorithm
from ..exceptions import CertificateNotFoundError, SigningError

class WindowsStoreSigner:
    """
    Windows Certificate Store integration for signing
    """

    def __init__(self, config: WindowsStoreConfig):
        """
        Initialize Windows Store signer

        Args:
            config: Windows Store configuration
        """
        if not WINDOWS_AVAILABLE:
            raise ImportError("Windows-specific modules not available. This signer only works on Windows.")

        self.config = config
        self.validator = CertificateValidator(config.validation_config.trusted_roots_folder)
        self.cert_context = None
        self.cert = None
        self.cert_bytes = None

    def get_all_certificates_from_store(self, store_name: str = None) -> List[CertificateInfo]:
        """
        Get all certificates from Windows certificate store

        Args:
            store_name: Certificate store name (defaults to config.store)

        Returns:
            List of certificate information objects
        """
        if store_name is None:
            store_name = self.config.store

        certificates = []
        st = win32crypt.CertOpenSystemStore(store_name, None)

        try:
            certs = st.CertEnumCertificatesInStore()
            for cert_context in certs:
                try:
                    subject_name = win32crypt.CertNameToStr(cert_context.Subject)
                    issuer_name = win32crypt.CertNameToStr(cert_context.Issuer)

                    cert_der = cert_context.CertEncoded
                    cert = x509.load_der_x509_certificate(cert_der, backend=default_backend())

                    try:
                        valid_from = cert.not_valid_before_utc
                        valid_to = cert.not_valid_after_utc
                    except AttributeError:
                        valid_from = cert.not_valid_before
                        valid_to = cert.not_valid_after

                    cert_info = CertificateInfo(
                        cert_context=cert_context,
                        subject_name=subject_name,
                        issuer_name=issuer_name,
                        serial_number=cert.serial_number,
                        valid_from=valid_from,
                        valid_to=valid_to,
                        cert_bytes=cert_der,
                        cert=cert,
                        thumbprint=self._get_thumbprint(cert)
                    )

                    certificates.append(cert_info)

                except Exception:
                    continue

        except Exception:
            pass
        finally:
            try:
                st.CertCloseStore()
            except:
                pass

        return certificates

    def filter_valid_signing_certificates(self, certificates: List[CertificateInfo]) -> List[CertificateInfo]:
        """
        Filter certificates that are valid for signing and match criteria

        Args:
            certificates: List of all certificates

        Returns:
            List of valid signing certificates
        """
        valid_certs = []

        for cert_info in certificates:
            try:
                cert = cert_info.cert

                # Check if certificate matches the specified criteria
                if not self.validator.matches_certificate_criteria(cert, self.config.certificate_filter):
                    continue

                # Validate certificate for signing
                if self.validator.validate_certificate_for_signing(cert, self.config.validation_config):
                    valid_certs.append(cert_info)

            except Exception as e:
                print(f"[WARNING] Error validating certificate {cert_info.subject_name}: {e}")
                continue

        return valid_certs

    def get_certificate(self) -> tuple:
        """
        Get certificate for signing

        Returns:
            Tuple of (key_handle, cert_bytes, cert)
        """
        all_certificates = self.get_all_certificates_from_store()

        if not all_certificates:
            raise CertificateNotFoundError(f"No certificates found in {self.config.store} store")

        # Filter for valid signing certificates
        valid_certificates = self.filter_valid_signing_certificates(all_certificates)

        if not valid_certificates:
            raise CertificateNotFoundError("No valid signing certificates found that match the criteria")

        if len(valid_certificates) == 1:
            selected_cert = valid_certificates[0]
            print(f"[+] Using certificate: {self._extract_cn(selected_cert.subject_name)}")
        else:
            selected_cert = self._show_selection_dialog(valid_certificates)

        if selected_cert is None:
            raise CertificateNotFoundError("No certificate selected")

        self.cert_context = selected_cert.cert_context
        self.cert_bytes = selected_cert.cert_bytes
        self.cert = selected_cert.cert

        return "win_cert", self.cert_bytes, self.cert

    def _show_selection_dialog(self, certificates: List[CertificateInfo]) -> Optional[CertificateInfo]:
        """Show certificate selection dialog exactly like imb.py"""
        print(f"[+] Found {len(certificates)} valid signing certificates")

        try:
            selected_cert_data = self._show_powershell_cert_dialog(certificates)
            if selected_cert_data:
                # Find the matching certificate by thumbprint
                selected_thumbprint = selected_cert_data.get('Thumbprint', '').upper()
                for cert_info in certificates:
                    if cert_info.thumbprint.upper() == selected_thumbprint:
                        print(f"[+] Certificate selected: {self._extract_cn(cert_info.subject_name)}")
                        return cert_info

                print("[!] Error: Selected certificate not found in valid certificates list")
                return None
            else:
                print("[+] Certificate selection cancelled by user")
                return None

        except Exception as e:
            print(f"[!] Error showing certificate dialog: {e}")
            # Fallback to first certificate if dialog fails
            if certificates:
                selected_cert = certificates[0]
                print(f"[+] Fallback: Auto-selecting first certificate: {self._extract_cn(selected_cert.subject_name)}")
                return selected_cert
            return None

    def _show_powershell_cert_dialog(self, valid_certificates: List[CertificateInfo]) -> Optional[dict]:
        """Show PowerShell certificate selection dialog - exactly like imb.py"""
        try:
            # Create certificate array for PowerShell
            cert_array_script = ""
            for i, cert_info in enumerate(valid_certificates):
                # Convert certificate bytes to base64 for PowerShell
                cert_b64 = base64.b64encode(cert_info.cert_bytes).decode('utf-8')
                cert_array_script += f'$cert{i} = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new([System.Convert]::FromBase64String("{cert_b64}"))\n'
                cert_array_script += f'$certCollection.Add($cert{i})\n'

            ps_script = f'''
# Hide PowerShell console window
Add-Type -Name Window -Namespace Console -MemberDefinition '
[DllImport("Kernel32.dll")]
public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]
public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
'
$consolePtr = [Console.Window]::GetConsoleWindow()
[Console.Window]::ShowWindow($consolePtr, 0)

try {{
    Add-Type -AssemblyName System.Security
    Add-Type -AssemblyName System.Windows.Forms

    $certCollection = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2Collection

    {cert_array_script}

    if ($certCollection.Count -eq 0) {{
        Write-Host "No valid signing certificates found"
        exit 1
    }}

    $selectedCert = [System.Security.Cryptography.X509Certificates.X509Certificate2UI]::SelectFromCollection(
        $certCollection,
        "ManageX XML Signing SDK",
        "Please select a certificate to sign the XML (Only valid signing certificates are shown):",
        [System.Security.Cryptography.X509Certificates.X509SelectionFlag]::SingleSelection
    )

    if ($selectedCert.Count -gt 0) {{
        $cert = $selectedCert[0]

        $certInfo = @{{
            Subject = $cert.Subject
            Issuer = $cert.Issuer
            SerialNumber = $cert.SerialNumber
            Thumbprint = $cert.Thumbprint
            NotBefore = $cert.NotBefore.ToString("yyyy-MM-dd HH:mm:ss")
            NotAfter = $cert.NotAfter.ToString("yyyy-MM-dd HH:mm:ss")
        }}

        $json = $certInfo | ConvertTo-Json -Compress
        Write-Host "SELECTED_CERT:$json"
    }} else {{
        Write-Host "CANCELLED"
        exit 0
    }}
}} catch {{
    Write-Host "PowerShell Error: $($_.Exception.Message)"
    exit 1
}}
'''

            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
                f.write(ps_script)
                script_path = f.name

            try:
                print("[+] Opening certificate selection dialog...")

                # Use subprocess with hidden window flags
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                result = subprocess.run([
                    'powershell.exe',
                    '-WindowStyle', 'Hidden',
                    '-NoProfile',
                    '-NonInteractive',
                    '-ExecutionPolicy', 'Bypass',
                    '-File', script_path
                ], capture_output=True, text=True, timeout=120,
                   creationflags=subprocess.CREATE_NO_WINDOW,
                   startupinfo=startupinfo)

                if result.returncode == 0:
                    if 'SELECTED_CERT:' in result.stdout:
                        json_lines = [line for line in result.stdout.split('\n') if line.startswith('SELECTED_CERT:')]
                        if json_lines:
                            json_data = json_lines[0].replace('SELECTED_CERT:', '')
                            cert_data = json.loads(json_data)
                            return cert_data
                    elif 'CANCELLED' in result.stdout:
                        return None
                    else:
                        print(f"[!] Unexpected PowerShell output: {result.stdout}")
                        return None
                else:
                    print(f"[!] PowerShell script failed with return code {result.returncode}")
                    if result.stderr:
                        print(f"[!] PowerShell stderr: {result.stderr}")
                    return None

            finally:
                try:
                    os.unlink(script_path)
                except:
                    pass

        except Exception as e:
            print(f"[!] Error in PowerShell certificate dialog: {e}")
            return None

    def _extract_cn(self, subject_name: str) -> str:
        """Extract Common Name from subject"""
        try:
            if 'CN=' in subject_name:
                return subject_name.split('CN=')[1].split(',')[0].strip()
            else:
                parts = [p.strip() for p in subject_name.split(',')]
                for part in parts:
                    if len(part) > 5 and not part.isdigit():
                        return part
                return parts[-1] if parts else subject_name
        except:
            return subject_name

    def _get_thumbprint(self, cert: x509.Certificate) -> str:
        """Get certificate thumbprint"""
        from ..core.certificate_manager import CertificateManager
        return CertificateManager.get_certificate_thumbprint(cert)

    def sign_xml_content(self, xml_content: bytes, signature_params) -> bytes:
        """
        Sign XML content using Windows Certificate Store

        Args:
            xml_content: XML content to sign
            signature_params: Signature parameters

        Returns:
            Signed XML content as bytes
        """
        # Get certificate if not already loaded
        if self.cert is None:
            self.get_certificate()

        try:
            # Use the complete XML signing implementation
            signed_xml = sign_xml_document(xml_content, self.cert, self, signature_params)
            return signed_xml

        except Exception as e:
            raise SigningError(f"Failed to sign XML content: {e}")

    def sign_data(self, data: bytes, signature_algorithm: SignatureAlgorithm) -> bytes:
        """
        Sign data using Windows Certificate Store private key

        Args:
            data: Data to sign
            signature_algorithm: Signature algorithm to use

        Returns:
            Signature bytes
        """
        if not self.cert_context:
            raise SigningError("Certificate not loaded for signing")

        try:
            # Get hash algorithm
            hash_algo = self._get_hash_algorithm_from_signature_algo(signature_algorithm)

            # Open certificate store and find certificate
            st = win32crypt.CertOpenSystemStore(self.config.store, None)
            cert_context = None

            try:
                certs = st.CertEnumCertificatesInStore()
                for cert in certs:
                    if cert.CertEncoded == self.cert_bytes:
                        cert_context = cert
                        break

                if cert_context is None:
                    raise SigningError("Certificate not found for signing")

                # Acquire private key
                keyspec, cryptprov = cert_context.CryptAcquireCertificatePrivateKey(
                    win32cryptcon.CRYPT_ACQUIRE_COMPARE_KEY_FLAG
                )

                # Create hash and sign
                chash = cryptprov.CryptCreateHash(hash_algo, None, 0)
                chash.CryptHashData(data, 0)
                signature = chash.CryptSignHash(keyspec, 0)

                # Reverse byte order for proper signature format
                return signature[::-1]

            finally:
                try:
                    st.CertCloseStore()
                except:
                    pass

        except Exception as e:
            raise SigningError(f"Error signing data: {e}")

    def _get_hash_algorithm_from_signature_algo(self, signature_algorithm: SignatureAlgorithm):
        """Get Windows crypto hash algorithm constant"""
        try:
            from win32.lib import win32cryptcon

            if signature_algorithm in [SignatureAlgorithm.RSA_SHA1, SignatureAlgorithm.DSA_SHA1, SignatureAlgorithm.ECDSA_SHA1]:
                return win32cryptcon.CALG_SHA1
            elif signature_algorithm in [SignatureAlgorithm.RSA_SHA256, SignatureAlgorithm.DSA_SHA256, SignatureAlgorithm.ECDSA_SHA256]:
                return win32cryptcon.CALG_SHA_256
            elif signature_algorithm in [SignatureAlgorithm.RSA_SHA384, SignatureAlgorithm.ECDSA_SHA384]:
                return win32cryptcon.CALG_SHA_384
            elif signature_algorithm in [SignatureAlgorithm.RSA_SHA512, SignatureAlgorithm.ECDSA_SHA512]:
                return win32cryptcon.CALG_SHA_512
            else:
                return win32cryptcon.CALG_SHA_256
        except ImportError:
            raise SigningError("Windows cryptographic constants not available")

    def cleanup(self):
        """Cleanup resources"""
        pass