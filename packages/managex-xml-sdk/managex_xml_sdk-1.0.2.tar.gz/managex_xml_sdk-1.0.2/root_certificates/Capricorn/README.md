# Capricorn CA Certificates

This folder contains root and intermediate certificates from Capricorn Identity Services Pvt. Ltd.

## Required Certificates:

- `Capricorn CA 2022.pem` - Intermediate CA certificate
- `Capricorn Sub CA for Individual DSC 2022.pem` - Sub CA for Individual certificates
- `Capricorn Sub CA for Organization DSC 2022.pem` - Sub CA for Organization certificates
- `Capricorn Sub CA for Document Signer DSC 2022.pem` - Sub CA for Document Signer certificates

## Certificate Chain:

```
CCA India 2022 (Root)
    ↓
Capricorn CA 2022 (Intermediate)
    ↓
Capricorn Sub CA for [Type] DSC 2022 (Sub CA)
    ↓
User Certificate
```

## Download Location:

Download certificates from Capricorn Identity Services website or your certificate provider.

## File Format:

All certificates should be in PEM format (.pem extension).

## Usage:

The ManageX XML SDK will automatically load all .pem files from this directory for certificate chain validation.