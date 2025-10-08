"""
ManageX XML Signing SDK Exceptions
"""

class ManageXError(Exception):
    """Base exception for all ManageX SDK operations"""
    pass

class CertificateValidationError(ManageXError):
    """Raised when certificate validation fails"""
    pass

class SigningError(ManageXError):
    """Raised when digital signing fails"""
    pass

class HSMError(ManageXError):
    """Raised when HSM operations fail"""
    pass

class PFXError(ManageXError):
    """Raised when PFX operations fail"""
    pass

class CertificateNotFoundError(ManageXError):
    """Raised when certificate is not found"""
    pass

class TrustedRootsNotFoundError(ManageXError):
    """Raised when trusted root certificates are not found"""
    pass

class InvalidCertificateChainError(ManageXError):
    """Raised when certificate chain is invalid"""
    pass

class XMLParsingError(ManageXError):
    """Raised when XML parsing fails"""
    pass

class InvalidConfigurationError(ManageXError):
    """Raised when configuration is invalid"""
    pass