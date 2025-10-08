"""
PFX File Signer
"""

from typing import Optional
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec

from ..core.validators import CertificateValidator
from ..core.xml_signing import sign_xml_document
from ..models.certificate_models import PFXConfig
from ..models.signature_models import SignatureAlgorithm
from ..exceptions import PFXError, CertificateNotFoundError, SigningError

class PFXSigner:
    """
    PFX file integration for signing
    """

    def __init__(self, config: PFXConfig):
        """
        Initialize PFX signer

        Args:
            config: PFX configuration
        """
        self.config = config
        self.validator = CertificateValidator(config.validation_config.trusted_roots_folder)
        self.private_key = None
        self.cert = None

    def get_certificate(self) -> tuple:
        """
        Get certificate from PFX file

        Returns:
            Tuple of (key_handle, cert_bytes, cert)
        """
        try:
            with open(self.config.pfx_file, "rb") as f:
                pfx_data = f.read()

            password = self.config.password.encode() if self.config.password else None

            # Load PFX
            private_key, cert, additional_certs = pkcs12.load_key_and_certificates(
                pfx_data,
                password,
                backend=default_backend()
            )

            if cert is None:
                raise PFXError("No certificate found in PFX file")

            # Check if certificate matches criteria
            if not self.validator.matches_certificate_criteria(cert, self.config.certificate_filter):
                raise CertificateNotFoundError("Certificate does not match the specified criteria")

            # Validate certificate for signing
            if not self.validator.validate_certificate_for_signing(cert, self.config.validation_config):
                raise CertificateNotFoundError("Certificate is not valid for signing")

            cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
            print(f"[+] Found valid signing certificate with CN = {cn}")

            self.private_key = private_key
            self.cert = cert

            from cryptography.hazmat.primitives import serialization
            cert_bytes = cert.public_bytes(serialization.Encoding.DER)

            return "pfx_key", cert_bytes, cert

        except Exception as e:
            raise PFXError(f"Error loading PFX file: {e}")

    def sign_xml_content(self, xml_content: bytes, signature_params) -> bytes:
        """
        Sign XML content using PFX file

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
        Sign data using PFX private key

        Args:
            data: Data to sign
            signature_algorithm: Signature algorithm to use

        Returns:
            Signature bytes
        """
        if not self.private_key:
            raise SigningError("Private key not loaded")

        # Hash algorithm mapping
        hash_algo_map = {
            SignatureAlgorithm.RSA_SHA1: hashes.SHA1(),
            SignatureAlgorithm.RSA_SHA256: hashes.SHA256(),
            SignatureAlgorithm.RSA_SHA384: hashes.SHA384(),
            SignatureAlgorithm.RSA_SHA512: hashes.SHA512(),
            SignatureAlgorithm.ECDSA_SHA1: hashes.SHA1(),
            SignatureAlgorithm.ECDSA_SHA256: hashes.SHA256(),
            SignatureAlgorithm.ECDSA_SHA384: hashes.SHA384(),
            SignatureAlgorithm.ECDSA_SHA512: hashes.SHA512(),
        }

        hash_algo = hash_algo_map.get(signature_algorithm)
        if not hash_algo:
            raise SigningError(f"Unsupported signature algorithm for PFX: {signature_algorithm}")

        try:
            # Determine signing based on key type and algorithm
            if signature_algorithm.value.startswith("http://www.w3.org/2000/09/xmldsig#rsa") or \
               signature_algorithm.value.startswith("http://www.w3.org/2001/04/xmldsig-more#rsa"):
                # RSA signing
                if isinstance(self.private_key, rsa.RSAPrivateKey):
                    signature = self.private_key.sign(
                        data,
                        padding.PKCS1v15(),
                        hash_algo
                    )
                else:
                    raise SigningError("RSA algorithm specified but key is not RSA")
            else:
                # ECDSA signing
                if isinstance(self.private_key, ec.EllipticCurvePrivateKey):
                    signature = self.private_key.sign(
                        data,
                        ec.ECDSA(hash_algo)
                    )
                else:
                    raise SigningError("ECDSA algorithm specified but key is not EC")

            return signature

        except Exception as e:
            raise SigningError(f"Error signing data with PFX: {e}")

    def cleanup(self):
        """Cleanup resources"""
        pass