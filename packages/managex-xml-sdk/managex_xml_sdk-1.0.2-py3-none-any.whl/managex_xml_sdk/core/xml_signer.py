"""
XML Signer - Main XML signing functionality
"""

import os
from typing import Optional
from ..models.signature_models import SignatureEnvelopeParameters
from ..models.certificate_models import SignerConfig
from ..exceptions import SigningError, InvalidConfigurationError

class XMLSigner:
    """
    Main XML signing class that coordinates certificate management and signing
    """

    def __init__(self, signer_config: SignerConfig, signature_params: Optional[SignatureEnvelopeParameters] = None):
        """
        Initialize XML signer

        Args:
            signer_config: Signer configuration (WindowsStoreConfig, PFXConfig, HSMConfig)
            signature_params: Signature envelope parameters (optional)
        """
        self.signer_config = signer_config
        self.signature_params = signature_params or SignatureEnvelopeParameters.create_default()
        self._signer_instance = None

    def _get_signer_instance(self):
        """Get the appropriate signer instance based on configuration"""
        if self._signer_instance is None:
            if self.signer_config.method == "store":
                from ..signers.windows_store_signer import WindowsStoreSigner
                self._signer_instance = WindowsStoreSigner(self.signer_config)
            elif self.signer_config.method == "pfx":
                from ..signers.pfx_signer import PFXSigner
                self._signer_instance = PFXSigner(self.signer_config)
            elif self.signer_config.method == "hsm":
                from ..signers.hsm_signer import HSMSigner
                self._signer_instance = HSMSigner(self.signer_config)
            else:
                raise InvalidConfigurationError(f"Unsupported signer method: {self.signer_config.method}")

        return self._signer_instance

    def sign_file(self, xml_file: str, output_file: str) -> bool:
        """
        Sign XML file

        Args:
            xml_file: Input XML file path
            output_file: Output signed XML file path

        Returns:
            bool: True if successful

        Raises:
            SigningError: If signing fails
        """
        if not os.path.exists(xml_file):
            raise SigningError(f"XML file not found: {xml_file}")

        try:
            # Get signer instance
            signer = self._get_signer_instance()

            # Read XML content
            with open(xml_file, 'rb') as f:
                xml_content = f.read()

            # Sign XML content
            signed_xml = signer.sign_xml_content(xml_content, self.signature_params)

            # Write signed XML
            with open(output_file, 'wb') as f:
                f.write(signed_xml)

            return True

        except Exception as e:
            raise SigningError(f"Failed to sign XML file: {e}")

    def sign_content(self, xml_content: bytes) -> bytes:
        """
        Sign XML content

        Args:
            xml_content: XML content as bytes

        Returns:
            Signed XML content as bytes

        Raises:
            SigningError: If signing fails
        """
        try:
            signer = self._get_signer_instance()
            return signer.sign_xml_content(xml_content, self.signature_params)
        except Exception as e:
            raise SigningError(f"Failed to sign XML content: {e}")

    @classmethod
    def create(cls, method: str, **kwargs):
        """
        Create XML signer with method and parameters

        Args:
            method: "store", "pfx", or "hsm"
            **kwargs: Additional configuration parameters

        Returns:
            XMLSigner instance
        """
        if method == "store":
            from ..models.certificate_models import WindowsStoreConfig, CertificateFilter, ValidationConfig

            cert_filter = CertificateFilter(
                cn=kwargs.get('cn'),
                o=kwargs.get('o'),
                ou=kwargs.get('ou'),
                email=kwargs.get('email'),
                serial=kwargs.get('serial'),
                ca=kwargs.get('ca')
            )

            validation_config = kwargs.get('validation_config')
            if validation_config is None:
                validation_config = ValidationConfig(
                    check_validity=kwargs.get('check_validity', False),
                    check_revocation_crl=kwargs.get('check_crl', False),
                    check_revocation_ocsp=kwargs.get('check_ocsp', False),
                    trusted_roots_folder=kwargs.get('trusted_roots_folder', 'root_certificates')
                )

            config = WindowsStoreConfig(
                store=kwargs.get('store', 'MY'),
                certificate_filter=cert_filter,
                validation_config=validation_config
            )

        elif method == "pfx":
            from ..models.certificate_models import PFXConfig, CertificateFilter, ValidationConfig

            cert_filter = CertificateFilter(
                cn=kwargs.get('cn'),
                o=kwargs.get('o'),
                ou=kwargs.get('ou'),
                email=kwargs.get('email'),
                serial=kwargs.get('serial'),
                ca=kwargs.get('ca')
            )

            validation_config = kwargs.get('validation_config')
            if validation_config is None:
                validation_config = ValidationConfig(
                    check_validity=kwargs.get('check_validity', False),
                    check_revocation_crl=kwargs.get('check_crl', False),
                    check_revocation_ocsp=kwargs.get('check_ocsp', False),
                    trusted_roots_folder=kwargs.get('trusted_roots_folder', 'root_certificates')
                )

            config = PFXConfig(
                pfx_file=kwargs.get('pfx_file', ''),
                password=kwargs.get('password', ''),
                certificate_filter=cert_filter,
                validation_config=validation_config
            )

        elif method == "hsm":
            from ..models.certificate_models import HSMConfig, CertificateFilter, ValidationConfig

            cert_filter = CertificateFilter(
                cn=kwargs.get('cn'),
                o=kwargs.get('o'),
                ou=kwargs.get('ou'),
                email=kwargs.get('email'),
                serial=kwargs.get('serial'),
                ca=kwargs.get('ca')
            )

            validation_config = kwargs.get('validation_config')
            if validation_config is None:
                validation_config = ValidationConfig(
                    check_validity=kwargs.get('check_validity', False),
                    check_revocation_crl=kwargs.get('check_crl', False),
                    check_revocation_ocsp=kwargs.get('check_ocsp', False),
                    trusted_roots_folder=kwargs.get('trusted_roots_folder', 'root_certificates')
                )

            config = HSMConfig(
                dll_path=kwargs.get('dll_path'),
                pin=kwargs.get('pin'),
                token_label=kwargs.get('token_label'),
                certificate_filter=cert_filter,
                validation_config=validation_config
            )

        else:
            raise InvalidConfigurationError(f"Unsupported method: {method}")

        signature_params = kwargs.get('signature_params')
        return cls(config, signature_params)