# ManageX XML Signing SDK

A comprehensive Python SDK for digital certificate management and XML digital signing with support for Windows Certificate Store, PFX files, and HSM tokens.

## Features

- ✅ **Multi-platform Support**: Windows, Linux, macOS
- ✅ **Multiple Certificate Sources**: Windows Store, PFX files, HSM tokens
- ✅ **Secure Certificate Validation**: Cryptographic verification against trusted roots
- ✅ **XML Digital Signing**: Full XML-DSig standard support
- ✅ **Certificate Chain Validation**: Authority Key Identifier (AKI) / Subject Key Identifier (SKI) matching
- ✅ **Flexible Certificate Filtering**: By CN, Organization, Email, Serial, etc.
- ✅ **Revocation Checking**: CRL and OCSP support
- ✅ **HSM Token Support**: PKCS#11 compatible hardware tokens

## Quick Start

### Installation

```bash
pip install managex-xml-sdk
```

### Basic Usage

```python
from managex_xml_sdk import create_xml_signer, sign_xml_file

# Quick XML signing
config = {
    "method": "store",  # Use Windows Certificate Store
    "store": "MY",
    "cn": "John Doe"    # Filter by Common Name
}

success = sign_xml_file("document.xml", "signed_document.xml", config)
print(f"Signing successful: {success}")
```

### Advanced Usage

```python
from managex_xml_sdk import (
    XMLSigner,
    WindowsStoreConfig,
    CertificateFilter,
    ValidationConfig,
    SignatureEnvelopeParameters
)

# Create certificate filter
cert_filter = CertificateFilter(
    cn="John Doe",
    o="My Organization",
    email="john@company.com"
)

# Create validation config with strict checking
validation = ValidationConfig.strict_validation("root_certificates")

# Create signer configuration
config = WindowsStoreConfig(
    store="MY",
    certificate_filter=cert_filter,
    validation_config=validation
)

# Create XML signer
signer = XMLSigner(config)

# Sign XML file
success = signer.sign_file("document.xml", "signed_document.xml")
```

## Certificate Sources

### Windows Certificate Store
```python
from managex_xml_sdk import WindowsStoreSigner, WindowsStoreConfig

config = WindowsStoreConfig(store="MY")
signer = WindowsStoreSigner(config)
certificates = signer.get_available_certificates()
```

### PFX Files
```python
from managex_xml_sdk import PFXSigner, PFXConfig

config = PFXConfig(
    pfx_file="certificate.pfx",
    password="password123"
)
signer = PFXSigner(config)
```

### HSM Tokens
```python
from managex_xml_sdk import HSMSigner, HSMConfig

config = HSMConfig(
    dll_path="C:\\Windows\\System32\\eToken.dll",
    pin="123456"
)
signer = HSMSigner(config)
tokens = signer.get_available_tokens()
```

## Certificate Validation

### Trusted Root Certificates Structure
```
root_certificates/
├── CCA_India/
│   └── CCA India 2022.pem
├── eMudhra/
│   └── eMudhra Root CA.pem
├── NSDL/
│   └── NSDL Root CA.pem
└── CustomCA/
    ├── Root CA.pem
    └── Intermediate CA.pem
```

### Validation Configuration
```python
from managex_xml_sdk import ValidationConfig

# Basic validation
basic_config = ValidationConfig.basic_validation()

# Strict validation with all checks
strict_config = ValidationConfig.strict_validation()

# Custom validation
custom_config = ValidationConfig(
    check_validity=True,
    check_revocation_crl=True,
    check_revocation_ocsp=False,
    trusted_roots_folder="my_roots"
)
```

## CLI Usage

If you have the original `imb.py` script, you can use it alongside the SDK:

```bash
# Windows Store signing
python imb.py --use-store --cn "John Doe" --file "document.xml"

# PFX signing
python imb.py --use-pfx "cert.pfx" --pfx-password "pass" --file "document.xml"

# HSM signing
python imb.py --use-hsm --token-pin "123456" --cn "John Doe" --file "document.xml"

# With validation
python imb.py --use-store --check-validity yes --check-crl yes --file "document.xml"
```

## Examples

### Complete Signing Example
```python
from managex_xml_sdk import (
    XMLSigner,
    WindowsStoreConfig,
    CertificateFilter,
    ValidationConfig,
    SignatureEnvelopeParameters,
    SignatureInfo,
    ReferenceInfo,
    KeyInfo
)

# Configure certificate filtering
cert_filter = CertificateFilter(
    cn="Digital Signature Certificate",
    o="My Company"
)

# Configure validation
validation = ValidationConfig(
    check_validity=True,
    check_revocation_crl=True,
    trusted_roots_folder="root_certificates"
)

# Configure signer
signer_config = WindowsStoreConfig(
    store="MY",
    certificate_filter=cert_filter,
    validation_config=validation
)

# Configure signature parameters
signature_params = SignatureEnvelopeParameters(
    signature_info=SignatureInfo(signature_id="MySignature-2024"),
    reference_info=ReferenceInfo(),
    key_info=KeyInfo(
        include_certificate=True,
        include_subject_name=True,
        include_issuer_serial=True
    )
)

# Create signer and sign
signer = XMLSigner(signer_config, signature_params)
success = signer.sign_file("document.xml", "signed_document.xml")

if success:
    print("XML signed successfully!")
else:
    print("Signing failed!")
```

### Batch Signing Example
```python
from managex_xml_sdk import create_xml_signer
import os

# Configuration
config = {
    "method": "store",
    "store": "MY",
    "cn": "Batch Signer",
    "check_validity": True
}

# Create signer once
signer = create_xml_signer(**config)

# Sign multiple files
xml_files = ["doc1.xml", "doc2.xml", "doc3.xml"]

for xml_file in xml_files:
    output_file = f"signed_{xml_file}"
    success = signer.sign_file(xml_file, output_file)
    print(f"{xml_file} -> {output_file}: {'✓' if success else '✗'}")
```

## Error Handling

```python
from managex_xml_sdk import (
    create_xml_signer,
    CertificateValidationError,
    SigningError,
    HSMError,
    PFXError
)

try:
    signer = create_xml_signer("store", cn="NonExistent")
    signer.sign_file("doc.xml", "signed.xml")
except CertificateValidationError as e:
    print(f"Certificate validation failed: {e}")
except SigningError as e:
    print(f"Signing failed: {e}")
except HSMError as e:
    print(f"HSM error: {e}")
except PFXError as e:
    print(f"PFX error: {e}")
```

## API Reference

### Core Classes
- `XMLSigner`: Main XML signing class
- `CertificateManager`: Certificate loading and management
- `CertificateValidator`: Certificate validation logic

### Signer Classes
- `WindowsStoreSigner`: Windows Certificate Store integration
- `PFXSigner`: PFX file handling
- `HSMSigner`: HSM token integration

### Configuration Classes
- `WindowsStoreConfig`: Windows Store configuration
- `PFXConfig`: PFX file configuration
- `HSMConfig`: HSM configuration
- `ValidationConfig`: Certificate validation settings
- `CertificateFilter`: Certificate filtering criteria

### Signature Classes
- `SignatureEnvelopeParameters`: Complete signature configuration
- `SignatureInfo`: Signature algorithm settings
- `ReferenceInfo`: Reference and digest settings
- `KeyInfo`: Key information inclusion settings

## Requirements

```
cryptography>=3.4.8
lxml>=4.6.0
requests>=2.25.0
PyKCS11>=1.5.0  # For HSM support
pywin32>=227    # For Windows Store support
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: [ManageX XML SDK Issues](https://github.com/managex/xml-sdk/issues)
- Documentation: [Full Documentation](https://docs.managex.com/xml-sdk)
- Email: support@managex.com