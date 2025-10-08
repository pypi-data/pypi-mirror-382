"""
Certificate validation functionality
"""

import requests
from datetime import datetime, timezone
from typing import List, Optional
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509.ocsp import OCSPRequestBuilder, OCSPCertStatus
import base64

from .certificate_manager import CertificateManager
from ..models.certificate_models import ValidationConfig, CertificateFilter
from ..exceptions import CertificateValidationError

class CertificateValidator:
    """
    Handles certificate validation against trusted roots and various checks
    """

    def __init__(self, trusted_roots_folder: str = "root_certificates"):
        """
        Initialize certificate validator

        Args:
            trusted_roots_folder: Path to trusted root certificates folder
        """
        self.cert_manager = CertificateManager(trusted_roots_folder)

    def validate_certificate_chain(self, cert: x509.Certificate, trusted_roots: List[x509.Certificate] = None) -> bool:
        """
        Check if certificate chain is valid against trusted roots using secure methods

        Args:
            cert: Certificate to validate
            trusted_roots: List of trusted root certificates (optional)

        Returns:
            True if valid, False otherwise
        """
        if trusted_roots is None:
            trusted_roots = self.cert_manager.get_trusted_roots()

        if not trusted_roots:
            print(f"[!] ERROR: No trusted root certificates loaded")
            return False

        print(f"[+] Verifying certificate against {len(trusted_roots)} trusted root certificates...")

        # Get certificate identifiers
        cert_thumbprint = self.cert_manager.get_certificate_thumbprint(cert)
        cert_aki = self.cert_manager.get_authority_key_identifier(cert)

        print(f"[+] User certificate thumbprint: {cert_thumbprint}")
        if cert_aki:
            print(f"[+] User certificate Authority Key Identifier: {cert_aki}")

        # Build trusted root database with all identifiers
        trusted_data = {}
        for root_cert in trusted_roots:
            root_thumbprint = self.cert_manager.get_certificate_thumbprint(root_cert)
            root_ski = self.cert_manager.get_subject_key_identifier(root_cert)
            root_cn = root_cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value

            trusted_data[root_thumbprint] = {
                'cert': root_cert,
                'cn': root_cn,
                'ski': root_ski,
                'thumbprint': root_thumbprint
            }

            print(f"[+] Trusted root: {root_cn}")
            print(f"    Thumbprint: {root_thumbprint}")
            if root_ski:
                print(f"    Subject Key Identifier: {root_ski}")

        # Method 1: Check if certificate is directly a trusted root
        if cert_thumbprint in trusted_data:
            print(f"[+] Certificate is directly a trusted root: {trusted_data[cert_thumbprint]['cn']}")
            return True

        # Method 2: Secure Authority/Subject Key Identifier matching
        if cert_aki:
            print(f"[+] Checking Authority Key Identifier matching...")
            for root_data in trusted_data.values():
                if root_data['ski'] and cert_aki == root_data['ski']:
                    print(f"[+] Authority Key Identifier matches trusted root: {root_data['cn']}")
                    print(f"    User cert AKI: {cert_aki}")
                    print(f"    Root cert SKI: {root_data['ski']}")

                    # Additional verification: Cryptographic signature check
                    try:
                        root_public_key = root_data['cert'].public_key()
                        root_public_key.verify(
                            cert.signature,
                            cert.tbs_certificate_bytes,
                            padding.PKCS1v15(),
                            cert.signature_hash_algorithm
                        )
                        print(f"[+] Cryptographic verification successful against: {root_data['cn']}")
                        return True
                    except Exception as e:
                        print(f"[!] Cryptographic verification failed: {e}")
                        continue

        # Method 3: Direct cryptographic verification
        print(f"[+] Attempting direct cryptographic verification...")
        for root_data in trusted_data.values():
            try:
                root_public_key = root_data['cert'].public_key()
                root_public_key.verify(
                    cert.signature,
                    cert.tbs_certificate_bytes,
                    padding.PKCS1v15(),
                    cert.signature_hash_algorithm
                )
                print(f"[+] Certificate cryptographically verified against root: {root_data['cn']}")
                return True
            except Exception:
                continue

        print(f"[!] ERROR: Certificate chain validation failed - no cryptographic proof found")
        return False

    def check_certificate_validity(self, cert: x509.Certificate) -> bool:
        """Check if certificate is currently valid (not expired)"""
        now = datetime.now(timezone.utc)
        try:
            not_before = cert.not_valid_before_utc
            not_after = cert.not_valid_after_utc
        except AttributeError:
            not_before = cert.not_valid_before.replace(tzinfo=timezone.utc)
            not_after = cert.not_valid_after.replace(tzinfo=timezone.utc)

        return not_before <= now <= not_after

    def check_key_usage_for_signing(self, cert: x509.Certificate) -> bool:
        """Check if certificate has required key usage for signing"""
        try:
            key_usage_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.KEY_USAGE)
            key_usage = key_usage_ext.value
            has_digital_signature = key_usage.digital_signature
            has_non_repudiation = key_usage.content_commitment
            return has_digital_signature and has_non_repudiation
        except x509.ExtensionNotFound:
            return True
        except Exception:
            return True

    def matches_certificate_criteria(self, cert: x509.Certificate, filter_criteria: CertificateFilter) -> bool:
        """Check if certificate matches the specified criteria"""
        try:
            subject = cert.subject

            # Check CN (Common Name)
            if filter_criteria.cn:
                try:
                    cert_cn = subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                    if filter_criteria.cn.lower() not in cert_cn.lower():
                        return False
                except IndexError:
                    return False

            # Check O (Organization)
            if filter_criteria.o:
                try:
                    cert_o = subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value
                    if filter_criteria.o.lower() not in cert_o.lower():
                        return False
                except IndexError:
                    return False

            # Check OU (Organizational Unit)
            if filter_criteria.ou:
                try:
                    cert_ou = subject.get_attributes_for_oid(x509.NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value
                    if filter_criteria.ou.lower() not in cert_ou.lower():
                        return False
                except IndexError:
                    return False

            # Check Email from SAN
            if filter_criteria.email:
                try:
                    san_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                    email_found = False
                    for name in san_ext.value:
                        if isinstance(name, x509.RFC822Name):
                            if filter_criteria.email.lower() == name.value.lower():
                                email_found = True
                                break
                    if not email_found:
                        return False
                except x509.ExtensionNotFound:
                    return False

            # Check Serial Number
            if filter_criteria.serial:
                cert_sn_hex = format(cert.serial_number, 'x').upper()
                target_sn_hex = filter_criteria.serial.replace(':', '').upper()
                if cert_sn_hex != target_sn_hex:
                    return False

            # Check Certifying Authority
            if filter_criteria.ca:
                try:
                    issuer_cn = cert.issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                    if filter_criteria.ca.lower() not in issuer_cn.lower():
                        return False
                except IndexError:
                    return False

            return True

        except Exception:
            return False

    def validate_certificate_for_signing(self, cert: x509.Certificate, config: ValidationConfig = None) -> bool:
        """Comprehensive certificate validation for signing"""
        if config is None:
            config = ValidationConfig()

        try:
            cert_cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        except IndexError:
            cert_cn = "Unknown"

        print(f"[+] Validating certificate: {cert_cn}")

        # Check certificate chain - MANDATORY
        if not self.validate_certificate_chain(cert):
            print(f"[!] CRITICAL ERROR: Certificate chain validation failed")
            return False

        # Check key usage for signing
        if config.require_key_usage_for_signing and not self.check_key_usage_for_signing(cert):
            print(f"[!] Certificate does not have required key usage for signing")
            return False

        # Check validity period
        if config.check_validity and not self.check_certificate_validity(cert):
            print(f"[!] Certificate is expired or not yet valid")
            return False

        # Check CRL revocation
        if config.check_revocation_crl and not self.check_certificate_revocation_crl(cert):
            print(f"[!] Certificate is revoked (CRL check)")
            return False

        # Check OCSP revocation
        if config.check_revocation_ocsp and not self.check_certificate_revocation_ocsp(cert):
            print(f"[!] Certificate is revoked (OCSP check)")
            return False

        print(f"[+] Certificate validation passed")
        return True

    def get_crl_distribution_points(self, cert: x509.Certificate) -> List[str]:
        """Get CRL Distribution Points from certificate"""
        try:
            crl_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.CRL_DISTRIBUTION_POINTS)
            crl_urls = []
            for dp in crl_ext.value:
                if dp.full_name:
                    for name in dp.full_name:
                        if isinstance(name, x509.UniformResourceIdentifier):
                            crl_urls.append(name.value)
            return crl_urls
        except x509.ExtensionNotFound:
            return []

    def check_certificate_revocation_crl(self, cert: x509.Certificate) -> bool:
        """Check certificate revocation status via CRL"""
        crl_urls = self.get_crl_distribution_points(cert)
        if not crl_urls:
            print("[WARNING] No CRL distribution points found in certificate")
            return True  # Assume not revoked if no CRL available

        for crl_url in crl_urls:
            try:
                print(f"[+] Checking CRL: {crl_url}")
                response = requests.get(crl_url, timeout=10)
                if response.status_code == 200:
                    crl = x509.load_der_x509_crl(response.content, default_backend())

                    # Check if certificate serial number is in revoked list
                    for revoked_cert in crl:
                        if revoked_cert.serial_number == cert.serial_number:
                            print(f"[!] Certificate is revoked (found in CRL)")
                            return False

                    print(f"[+] Certificate not found in CRL - not revoked")
                    return True
            except Exception as e:
                print(f"[WARNING] Failed to check CRL {crl_url}: {e}")
                continue

        return True  # Assume not revoked if CRL check fails

    def get_ocsp_responder_url(self, cert: x509.Certificate) -> str:
        """Get OCSP responder URL from certificate"""
        try:
            aia_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
            for access_description in aia_ext.value:
                if access_description.access_method == x509.AuthorityInformationAccessOID.OCSP:
                    return access_description.access_location.value
        except x509.ExtensionNotFound:
            pass
        return None

    def find_issuer_certificate(self, cert: x509.Certificate) -> Optional[x509.Certificate]:
        """Find the issuer certificate for the given certificate"""
        cert_aki = self.cert_manager.get_authority_key_identifier(cert)
        trusted_roots = self.cert_manager.get_trusted_roots()

        if not cert_aki:
            return None

        for root_cert in trusted_roots:
            root_ski = self.cert_manager.get_subject_key_identifier(root_cert)
            if root_ski and cert_aki == root_ski:
                return root_cert

        return None

    def check_certificate_revocation_ocsp(self, cert: x509.Certificate, issuer_cert: x509.Certificate = None) -> bool:
        """Check certificate revocation status via OCSP"""
        ocsp_url = self.get_ocsp_responder_url(cert)
        if not ocsp_url:
            print("[WARNING] No OCSP responder URL found in certificate")
            return True  # Assume not revoked if no OCSP available

        try:
            print(f"[+] Checking OCSP: {ocsp_url}")

            # Find issuer certificate if not provided
            if issuer_cert is None:
                issuer_cert = self.find_issuer_certificate(cert)
                if issuer_cert is None:
                    print("[WARNING] Could not find issuer certificate for OCSP request")
                    return True

            # Build OCSP request
            builder = OCSPRequestBuilder()
            builder = builder.add_certificate(cert, issuer_cert, hashes.SHA1())
            ocsp_request = builder.build()

            # Prepare request data
            request_data = ocsp_request.public_bytes(serialization.Encoding.DER)
            headers = {
                'Content-Type': 'application/ocsp-request',
                'Content-Length': str(len(request_data))
            }

            # Send OCSP request
            response = requests.post(
                ocsp_url,
                data=request_data,
                headers=headers,
                timeout=15
            )

            if response.status_code != 200:
                print(f"[WARNING] OCSP responder returned status: {response.status_code}")
                return True

            # Parse OCSP response
            try:
                from cryptography.x509.ocsp import load_der_ocsp_response
                ocsp_response = load_der_ocsp_response(response.content)

                # Check response status
                if ocsp_response.response_status != x509.ocsp.OCSPResponseStatus.SUCCESSFUL:
                    print(f"[WARNING] OCSP response status: {ocsp_response.response_status}")
                    return True

                # Check certificate status
                single_response = ocsp_response.single_extensions
                cert_status = ocsp_response.certificate_status

                if cert_status == OCSPCertStatus.GOOD:
                    print("[+] OCSP status: Certificate is valid (GOOD)")
                    return True
                elif cert_status == OCSPCertStatus.REVOKED:
                    print("[!] OCSP status: Certificate is REVOKED")
                    return False
                else:  # UNKNOWN
                    print("[WARNING] OCSP status: Certificate status UNKNOWN")
                    return True  # Assume valid if status is unknown

            except Exception as parse_error:
                print(f"[WARNING] Failed to parse OCSP response: {parse_error}")
                return True

        except Exception as e:
            print(f"[WARNING] OCSP check failed: {e}")
            return True