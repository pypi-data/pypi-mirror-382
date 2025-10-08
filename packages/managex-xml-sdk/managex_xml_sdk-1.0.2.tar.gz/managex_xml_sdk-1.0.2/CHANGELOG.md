# Changelog

All notable changes to the ManageX XML Signing SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-27

### Added
- 🎉 **Initial Release** - Complete XML Digital Signing SDK
- ✅ **Multi-Platform Support** - Windows, Linux, macOS compatibility
- ✅ **Windows Certificate Store Integration** - Native Windows certificate selection dialog
- ✅ **PFX File Support** - PKCS#12 certificate and private key handling
- ✅ **HSM Token Support** - PKCS#11 hardware security module integration
- ✅ **Enterprise Security Features**:
  - AKI/SKI certificate chain validation
  - Cryptographic verification against trusted root CAs
  - CRL and OCSP revocation checking
  - Certificate filtering by CN, Organization, Email, Serial, CA
- ✅ **XML Digital Signature Compliance** - Full XML-DSig (RFC 3275) standard support
- ✅ **HSM Token Protection** - PIN retry limits to prevent token locking
- ✅ **Comprehensive Certificate Validation** - Key usage validation, expiration checking
- ✅ **User-Friendly Certificate Selection** - Windows GUI dialog integration
- ✅ **Command-Line Interface** - Full CLI tool for automation and scripting
- ✅ **Production-Ready Architecture** - Robust error handling and logging

### Security
- 🔒 **Secure Certificate Chain Validation** - Uses cryptographic proof instead of string matching
- 🔒 **Authority Key Identifier (AKI) Matching** - Prevents certificate spoofing attacks
- 🔒 **Trusted Root Certificate Verification** - Validates against configurable root CA folder
- 🔒 **HSM PIN Protection** - Prevents accidental token locking with retry limits

### Features
- 📦 **Multiple Certificate Sources**:
  - Windows Certificate Store (MY, CA, ROOT stores)
  - PFX/P12 files with password protection
  - PKCS#11 HSM tokens (eToken, Watchdata, etc.)
- 🎛️ **Flexible Certificate Filtering**:
  - Common Name (CN) matching
  - Organization (O) and Organizational Unit (OU)
  - Email address from Subject Alternative Name
  - Certificate serial number
  - Issuing Certificate Authority
- 🔧 **XML Signature Customization**:
  - Configurable signature algorithms (RSA-SHA1/256/384/512, ECDSA)
  - Custom digest algorithms (SHA1/256/384/512)
  - Canonicalization options
  - KeyInfo element customization
- 📊 **Certificate Discovery Tools**:
  - List all certificates in Windows stores
  - HSM token detection and enumeration
  - Certificate validation reporting

### Documentation
- 📖 **Comprehensive README** - Complete usage guide and examples
- 📚 **API Documentation** - Full class and method documentation
- 🔧 **Setup Instructions** - Installation and configuration guide
- 💡 **Examples** - Multiple usage examples and integration patterns

### Testing
- ✅ **Integration Tests** - Complete SDK functionality testing
- ✅ **Certificate Discovery Tests** - Windows Store and HSM enumeration
- ✅ **Root Certificate Loading Tests** - Trusted CA validation
- ✅ **XML Processing Tests** - Digital signature creation and validation

### Architecture
- 🏗️ **Modular Design** - Separate signers for different certificate sources
- 🎯 **Clean API** - Intuitive class hierarchy and method organization
- 🔌 **Extensible** - Easy to add new certificate sources and signature methods
- 🛡️ **Error Handling** - Comprehensive exception handling and user feedback

## [Unreleased]

### Planned Features
- 📱 **Mobile Platform Support** - iOS and Android compatibility
- 🌐 **Web Service Integration** - REST API for remote signing
- 📊 **Advanced Reporting** - Detailed signing audit logs
- 🔄 **Batch Processing** - Multiple file signing automation
- 🎨 **GUI Application** - Desktop application for non-technical users

---

## Version History Summary

| Version | Release Date | Major Features |
|---------|-------------|----------------|
| 1.0.0   | 2025-01-27  | Initial release with full XML signing capabilities |

---

**Note**: This project follows [Semantic Versioning](https://semver.org/). Version numbers follow the MAJOR.MINOR.PATCH format where:
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backwards-compatible manner
- **PATCH**: Backwards-compatible bug fixes

For questions about releases or to request features, please:
- 📧 Email: [chaturvedianiket007@gmail.com](mailto:chaturvedianiket007@gmail.com)
- 🐛 Report Issues: [GitHub Issues](https://github.com/Aniketc068/managex_xml_sdk/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Aniketc068/managex_xml_sdk/discussions)