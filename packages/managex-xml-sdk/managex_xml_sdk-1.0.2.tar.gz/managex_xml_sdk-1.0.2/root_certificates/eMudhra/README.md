# eMudhra Certificates

This folder contains root and intermediate certificates from eMudhra Limited.

## Required Certificates:

- `eMudhra Root CA.pem` - Root CA certificate
- `eMudhra Intermediate CA.pem` - Intermediate CA certificate
- Other eMudhra sub CA certificates as needed

## Download Location:

Download certificates from eMudhra website or your certificate provider.

## File Format:

All certificates should be in PEM format (.pem extension).

## Usage:

The ManageX XML SDK will automatically load all .pem files from this directory for certificate chain validation.