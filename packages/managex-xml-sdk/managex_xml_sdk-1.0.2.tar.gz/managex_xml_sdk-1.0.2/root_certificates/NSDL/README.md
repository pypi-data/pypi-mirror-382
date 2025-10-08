# NSDL Certificates

This folder contains root and intermediate certificates from NSDL e-Governance Infrastructure Limited.

## Required Certificates:

- `NSDL Root CA.pem` - Root CA certificate
- `NSDL Intermediate CA.pem` - Intermediate CA certificate
- Other NSDL sub CA certificates as needed

## Download Location:

Download certificates from NSDL e-Gov website or your certificate provider.

## File Format:

All certificates should be in PEM format (.pem extension).

## Usage:

The ManageX XML SDK will automatically load all .pem files from this directory for certificate chain validation.