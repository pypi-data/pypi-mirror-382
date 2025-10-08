# ManageX XML Signing SDK
# A complete Python SDK for digital certificate management and XML signing

__version__ = "1.0.2"
__author__ = "ManageX Development Team"
__description__ = "Complete XML Digital Signing SDK with PKI certificate validation"

# Core imports for easy access
from .core.certificate_manager import CertificateManager
from .core.xml_signer import XMLSigner
from .core.validators import CertificateValidator
from .signers.windows_store_signer import WindowsStoreSigner
from .signers.pfx_signer import PFXSigner
from .signers.hsm_signer import HSMSigner
from .models.signature_models import (
    SignatureInfo,
    ReferenceInfo,
    KeyInfo,
    SignatureEnvelopeParameters,
    SignatureAlgorithm,
    DigestAlgorithm,
    CanonicalizationAlgorithm,
    TransformAlgorithm
)
from .models.certificate_models import CertificateInfo, CertificateFilter, ValidationConfig
from .exceptions import (
    ManageXError,
    CertificateValidationError,
    SigningError,
    HSMError,
    PFXError
)

# Quick access functions
def create_xml_signer(method="store", **kwargs):
    """
    Quick function to create XML signer

    Args:
        method: "store", "pfx", or "hsm"
        **kwargs: Additional arguments for specific signer

    Returns:
        XMLSigner instance

    Example:
        # Windows Store signer
        signer = create_xml_signer("store", store="MY")

        # PFX signer
        signer = create_xml_signer("pfx", pfx_file="cert.pfx", password="pass")

        # HSM signer
        signer = create_xml_signer("hsm", dll_path="token.dll", pin="1234")
    """
    return XMLSigner.create(method, **kwargs)

def validate_certificate(cert_path, trusted_roots_folder="root_certificates"):
    """
    Quick function to validate certificate

    Args:
        cert_path: Path to certificate file
        trusted_roots_folder: Path to trusted roots folder

    Returns:
        bool: True if valid

    Example:
        is_valid = validate_certificate("mycert.pem", "root_certificates")
    """
    validator = CertificateValidator(trusted_roots_folder)
    return validator.validate_from_file(cert_path)

def sign_xml_file(xml_file, output_file, signer_config):
    """
    Quick function to sign XML file

    Args:
        xml_file: Input XML file path
        output_file: Output signed XML file path
        signer_config: Signer configuration dict

    Returns:
        bool: True if successful

    Example:
        config = {
            "method": "store",
            "store": "MY",
            "cn": "John Doe"
        }
        success = sign_xml_file("doc.xml", "signed_doc.xml", config)
    """
    signer = create_xml_signer(**signer_config)
    return signer.sign_file(xml_file, output_file)

def get_available_certificates(method="store", **kwargs):
    """
    Quick function to get available certificates

    Args:
        method: "store", "hsm"
        **kwargs: Additional arguments

    Returns:
        List of available certificates

    Example:
        # Get Windows Store certificates
        certs = get_available_certificates("store", store="MY")

        # Get HSM certificates
        certs = get_available_certificates("hsm", dll_path="token.dll", pin="1234")
    """
    if method == "store":
        from .signers.windows_store_signer import WindowsStoreSigner
        signer = WindowsStoreSigner(**kwargs)
        return signer.get_all_certificates_from_store()
    elif method == "hsm":
        from .signers.hsm_signer import HSMSigner
        return HSMSigner.get_all_available_tokens()
    else:
        raise ValueError(f"Unsupported method: {method}")

__all__ = [
    'CertificateManager',
    'XMLSigner',
    'CertificateValidator',
    'WindowsStoreSigner',
    'PFXSigner',
    'HSMSigner',
    'SignatureInfo',
    'ReferenceInfo',
    'KeyInfo',
    'SignatureEnvelopeParameters',
    'SignatureAlgorithm',
    'DigestAlgorithm',
    'CanonicalizationAlgorithm',
    'TransformAlgorithm',
    'CertificateInfo',
    'CertificateFilter',
    'ValidationConfig',
    'ManageXError',
    'CertificateValidationError',
    'SigningError',
    'HSMError',
    'PFXError',
    'create_xml_signer',
    'validate_certificate',
    'sign_xml_file',
    'get_available_certificates'
]