# Sify Certificates

This folder contains root and intermediate certificates from Sify Technologies Limited.

## Required Certificates:

- `Sify Root CA.pem` - Root CA certificate
- `Sify Intermediate CA.pem` - Intermediate CA certificate
- Other Sify sub CA certificates as needed

## Download Location:

Download certificates from Sify website or your certificate provider.

## File Format:

All certificates should be in PEM format (.pem extension).

## Usage:

The ManageX XML SDK will automatically load all .pem files from this directory for certificate chain validation.