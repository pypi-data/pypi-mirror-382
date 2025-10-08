#!/usr/bin/env python3
"""
ManageX XML Signing SDK Example
Complete demonstration of ManageX XML Digital Signature SDK functionality
Equivalent to imb.py features but using the structured SDK
"""

import sys
import os
import argparse

# Add SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'managex_xml_sdk'))

def sign_xml_with_windows_store(xml_file, output_file=None, **kwargs):
    """Sign XML using Windows Certificate Store"""
    from managex_xml_sdk.core.xml_signer import XMLSigner
    from managex_xml_sdk.models.signature_models import SignatureEnvelopeParameters, SignatureInfo, ReferenceInfo, KeyInfo
    from managex_xml_sdk.models.signature_models import SignatureAlgorithm, DigestAlgorithm

    print("[+] Using Windows Certificate Store for signing")

    try:
        # Create XML signer
        xml_signer = XMLSigner.create(
            method="store",
            store=kwargs.get('store', 'MY'),
            cn=kwargs.get('cn'),
            o=kwargs.get('o'),
            ou=kwargs.get('ou'),
            email=kwargs.get('email'),
            serial=kwargs.get('serial'),
            ca=kwargs.get('ca'),
            trusted_roots_folder=kwargs.get('trusted_roots_folder', 'root_certificates'),
            check_validity=kwargs.get('check_validity', False),
            check_crl=kwargs.get('check_crl', False),
            check_ocsp=kwargs.get('check_ocsp', False)
        )

        # Configure signature parameters
        sig_algo_map = {
            'rsa-sha1': SignatureAlgorithm.RSA_SHA1,
            'rsa-sha256': SignatureAlgorithm.RSA_SHA256,
            'rsa-sha384': SignatureAlgorithm.RSA_SHA384,
            'rsa-sha512': SignatureAlgorithm.RSA_SHA512,
            'ecdsa-sha256': SignatureAlgorithm.ECDSA_SHA256,
        }

        digest_algo_map = {
            'sha1': DigestAlgorithm.SHA1,
            'sha256': DigestAlgorithm.SHA256,
            'sha384': DigestAlgorithm.SHA384,
            'sha512': DigestAlgorithm.SHA512,
        }

        signature_info = SignatureInfo(
            signature_algorithm=sig_algo_map.get(kwargs.get('sig_algo', 'rsa-sha256'), SignatureAlgorithm.RSA_SHA256)
        )

        reference_info = ReferenceInfo(
            digest_algorithm=digest_algo_map.get(kwargs.get('digest_algo', 'sha256'), DigestAlgorithm.SHA256),
            reference_id=kwargs.get('ref_id')
        )

        key_info = KeyInfo(
            include_subject_name=not kwargs.get('exclude_subject', False),
            include_certificate=not kwargs.get('exclude_cert', False),
            include_public_key=kwargs.get('include_public_key', False),
            include_issuer_serial=kwargs.get('include_issuer_serial', False),
            include_subject_key_id=kwargs.get('include_subject_key_id', False)
        )

        signature_params = SignatureEnvelopeParameters(
            signature_info=signature_info,
            reference_info=reference_info,
            key_info=key_info
        )

        # Set default output file if not specified
        if output_file is None:
            base_name = os.path.splitext(xml_file)[0]
            output_file = f"{base_name}_signed.xml"

        # Sign the file
        print(f"[+] Signing XML file: {xml_file}")
        xml_signer.sign_file(xml_file, output_file)

        print(f"[+] Successfully signed XML file: {output_file}")
        return True

    except Exception as e:
        print(f"[!] Error signing with Windows Store: {e}")
        return False

def sign_xml_with_pfx(xml_file, pfx_file, password=None, output_file=None, **kwargs):
    """Sign XML using PFX file"""
    from managex_xml_sdk.core.xml_signer import XMLSigner
    from managex_xml_sdk.models.signature_models import SignatureEnvelopeParameters

    print(f"[+] Using PFX file for signing: {pfx_file}")

    try:
        # Get PFX password if not provided
        if password is None:
            import getpass
            password = getpass.getpass("Enter PFX password: ")

        # Create XML signer
        xml_signer = XMLSigner.create(
            method="pfx",
            pfx_file=pfx_file,
            password=password,
            cn=kwargs.get('cn'),
            o=kwargs.get('o'),
            ou=kwargs.get('ou'),
            email=kwargs.get('email'),
            serial=kwargs.get('serial'),
            ca=kwargs.get('ca'),
            trusted_roots_folder=kwargs.get('trusted_roots_folder', 'root_certificates'),
            check_validity=kwargs.get('check_validity', False),
            check_crl=kwargs.get('check_crl', False),
            check_ocsp=kwargs.get('check_ocsp', False)
        )

        # Use default signature parameters with fixed ManageX-Signature ID
        signature_params = SignatureEnvelopeParameters.create_default()

        # Set default output file if not specified
        if output_file is None:
            base_name = os.path.splitext(xml_file)[0]
            output_file = f"{base_name}_signed.xml"

        # Sign the file
        print(f"[+] Signing XML file: {xml_file}")
        xml_signer.sign_file(xml_file, output_file)

        print(f"[+] Successfully signed XML file: {output_file}")
        return True

    except Exception as e:
        print(f"[!] Error signing with PFX: {e}")
        return False

def sign_xml_with_hsm(xml_file, pin=None, dll_path=None, output_file=None, **kwargs):
    """Sign XML using HSM token"""
    from managex_xml_sdk.core.xml_signer import XMLSigner
    from managex_xml_sdk.models.signature_models import SignatureEnvelopeParameters

    print("[+] Using HSM token for signing")

    try:
        # Get HSM PIN if not provided
        if pin is None:
            import getpass
            pin = getpass.getpass("Enter HSM token PIN: ")

        # Create XML signer
        xml_signer = XMLSigner.create(
            method="hsm",
            dll_path=dll_path,
            pin=pin,
            cn=kwargs.get('cn'),
            o=kwargs.get('o'),
            ou=kwargs.get('ou'),
            email=kwargs.get('email'),
            serial=kwargs.get('serial'),
            ca=kwargs.get('ca'),
            trusted_roots_folder=kwargs.get('trusted_roots_folder', 'root_certificates'),
            check_validity=kwargs.get('check_validity', False),
            check_crl=kwargs.get('check_crl', False),
            check_ocsp=kwargs.get('check_ocsp', False)
        )

        # Use default signature parameters with fixed ManageX-Signature ID
        signature_params = SignatureEnvelopeParameters.create_default()

        # Set default output file if not specified
        if output_file is None:
            base_name = os.path.splitext(xml_file)[0]
            output_file = f"{base_name}_signed.xml"

        # Sign the file
        print(f"[+] Signing XML file: {xml_file}")
        xml_signer.sign_file(xml_file, output_file)

        print(f"[+] Successfully signed XML file: {output_file}")
        return True

    except Exception as e:
        print(f"[!] Error signing with HSM: {e}")
        return False

def list_certificates(store='MY'):
    """List certificates in Windows store"""
    from managex_xml_sdk.signers.windows_store_signer import WindowsStoreSigner
    from managex_xml_sdk.models.certificate_models import WindowsStoreConfig, CertificateFilter, ValidationConfig

    print(f"\\n[+] Listing certificates in '{store}' store:")
    print("-" * 60)

    try:
        config = WindowsStoreConfig(
            store=store,
            certificate_filter=CertificateFilter(),
            validation_config=ValidationConfig.basic_validation("root_certificates")
        )

        signer = WindowsStoreSigner(config)
        certificates = signer.get_all_certificates_from_store()

        if not certificates:
            print("No certificates found in the store.")
            return

        # Filter for valid signing certificates
        valid_certificates = signer.filter_valid_signing_certificates(certificates)

        print(f"Total certificates: {len(certificates)}")
        print(f"Valid signing certificates: {len(valid_certificates)}")
        print()

        for i, cert_info in enumerate(valid_certificates, 1):
            print(f"{i}. Subject: {cert_info.subject_name}")
            print(f"   Issuer:  {cert_info.issuer_name}")
            print(f"   Serial:  {cert_info.serial_number}")
            print(f"   Valid:   {cert_info.valid_from} to {cert_info.valid_to}")
            print()

        print("-" * 60)

    except Exception as e:
        print(f"Error listing certificates: {e}")

def list_hsm_tokens():
    """List available HSM tokens"""
    from managex_xml_sdk.signers.hsm_signer import HSMSigner

    print("\\n[+] Scanning for HSM tokens...")
    print("-" * 60)

    try:
        tokens = HSMSigner.get_all_available_tokens()

        if tokens:
            print(f"Found {len(tokens)} HSM token(s):")
            for i, token in enumerate(tokens, 1):
                print(f"\\n{i}. Token Details:")
                print(f"   Label: {token['label']}")
                print(f"   Manufacturer: {token['manufacturer']}")
                print(f"   Model: {token['model']}")
                print(f"   Serial: {token['serial']}")
                print(f"   DLL: {token['dll_path']}")
        else:
            print("No HSM tokens found")

        print("-" * 60)

    except Exception as e:
        print(f"Error listing HSM tokens: {e}")

def main():
    """Main function with argument parsing equivalent to imb.py"""
    parser = argparse.ArgumentParser(
        description='ManageX XML Signing SDK - Digital signature tool with PKI validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic signing with Windows Store
  python managex_xml_signing_example.py --file document.xml

  # Sign with specific organization
  python managex_xml_signing_example.py --o "Capricorn" --file document.xml

  # Use HSM with custom DLL and specific criteria
  python managex_xml_signing_example.py --use-hsm --hsm-dll "C:\\custom\\hsm.dll" --cn "John Doe" --ca "My CA"

  # Use PFX with validation checks
  python managex_xml_signing_example.py --use-pfx mycert.pfx --check-validity yes --check-crl yes

  # List valid signing certificates
  python managex_xml_signing_example.py --list-certs

  # Sign with multiple criteria matching
  python managex_xml_signing_example.py --o "Company" --email "user@company.com" --serial "1A2B3C4D"
        '''
    )

    # File Options
    file_group = parser.add_argument_group('File Options')
    file_group.add_argument('--file', '-f', default='new.xml',
                           help='XML file to sign (default: new.xml)')
    file_group.add_argument('--output', '-o',
                           help='Output file name (default: <input_file>_signed.xml)')

    # Certificate Matching Criteria
    criteria_group = parser.add_argument_group('Certificate Matching Criteria')
    criteria_group.add_argument('--cn', help='Certificate Common Name to match')
    criteria_group.add_argument('--o', help='Organization name to match')
    criteria_group.add_argument('--ou', help='Organizational Unit to match')
    criteria_group.add_argument('--email', help='Email from SAN to match')
    criteria_group.add_argument('--serial', help='Certificate serial number (hex)')
    criteria_group.add_argument('--ca', help='Certifying Authority to match')

    # Certificate Source Methods
    method_group = parser.add_argument_group('Certificate Source Methods')
    cert_group = method_group.add_mutually_exclusive_group()
    cert_group.add_argument('--use-store', action='store_true', default=True,
                           help='Use Windows Certificate Store (default)')
    cert_group.add_argument('--use-hsm', action='store_true',
                           help='Use HSM token for signing')
    cert_group.add_argument('--use-pfx', metavar='PFX_FILE',
                           help='Use PFX file for signing')

    # Method-Specific Options
    store_group = parser.add_argument_group('Windows Certificate Store Options')
    store_group.add_argument('--store', default='MY',
                            help='Certificate store name (default: MY)')

    hsm_group = parser.add_argument_group('HSM Token Options')
    hsm_group.add_argument('--hsm-dll', help='HSM DLL path (auto-detected if not specified)')
    hsm_group.add_argument('--token-pin', help='HSM token PIN (will prompt if not provided)')

    pfx_group = parser.add_argument_group('PFX File Options')
    pfx_group.add_argument('--pfx-password', help='PFX file password (will prompt if not provided)')

    # Certificate Validation Options
    validation_group = parser.add_argument_group('Certificate Validation Options')
    validation_group.add_argument('--root-certs-folder', default='root_certificates',
                                 help='Folder containing trusted root certificates (.pem files)')
    validation_group.add_argument('--check-validity', choices=['yes', 'no'], default='no',
                                 help='Check if certificate is valid (not expired)')
    validation_group.add_argument('--check-crl', choices=['yes', 'no'], default='no',
                                 help='Check certificate revocation via CRL')
    validation_group.add_argument('--check-ocsp', choices=['yes', 'no'], default='no',
                                 help='Check certificate revocation via OCSP')

    # Information Commands
    info_group = parser.add_argument_group('Information Commands')
    info_group.add_argument('--list-certs', action='store_true',
                           help='List all valid signing certificates in Windows store')
    info_group.add_argument('--list-tokens', action='store_true',
                           help='List available HSM tokens')

    # Signature Algorithm Options
    sig_group = parser.add_argument_group('Signature Algorithm Options')
    sig_group.add_argument('--sig-algo', choices=['rsa-sha1', 'rsa-sha256', 'rsa-sha384', 'rsa-sha512',
                                                  'ecdsa-sha256'],
                          default='rsa-sha256', help='Signature algorithm (default: rsa-sha256)')
    sig_group.add_argument('--digest-algo', choices=['sha1', 'sha256', 'sha384', 'sha512'], default='sha256',
                          help='Digest algorithm (default: sha256)')

    # XML Signature Options
    xml_group = parser.add_argument_group('XML Signature Options')
    xml_group.add_argument('--ref-id', help='Optional reference ID')

    # KeyInfo Options
    keyinfo_group = parser.add_argument_group('KeyInfo Element Options')
    keyinfo_group.add_argument('--include-public-key', action='store_true',
                              help='Include public key in KeyInfo')
    keyinfo_group.add_argument('--include-issuer-serial', action='store_true',
                              help='Include X509IssuerSerial in KeyInfo')
    keyinfo_group.add_argument('--include-subject-key-id', action='store_true',
                              help='Include X509SKI in KeyInfo')
    keyinfo_group.add_argument('--exclude-cert', action='store_true',
                              help='Exclude certificate from KeyInfo')
    keyinfo_group.add_argument('--exclude-subject', action='store_true',
                              help='Exclude subject name from KeyInfo')

    args = parser.parse_args()

    # Handle information commands
    if args.list_certs:
        list_certificates(args.store)
        return

    if args.list_tokens:
        list_hsm_tokens()
        return

    # Validate input file
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found!")
        sys.exit(1)

    # Prepare signing parameters
    signing_params = {
        'cn': args.cn,
        'o': args.o,
        'ou': args.ou,
        'email': args.email,
        'serial': args.serial,
        'ca': args.ca,
        'store': args.store,
        'trusted_roots_folder': args.root_certs_folder,
        'check_validity': args.check_validity == 'yes',
        'check_crl': args.check_crl == 'yes',
        'check_ocsp': args.check_ocsp == 'yes',
        'sig_algo': args.sig_algo,
        'digest_algo': args.digest_algo,
        'ref_id': args.ref_id,
        'include_public_key': args.include_public_key,
        'include_issuer_serial': args.include_issuer_serial,
        'include_subject_key_id': args.include_subject_key_id,
        'exclude_cert': args.exclude_cert,
        'exclude_subject': args.exclude_subject,
    }

    # Display configuration
    print("ManageX XML Signing SDK")
    print("=" * 40)
    print(f"Input file: {args.file}")
    print(f"Output file: {args.output or 'auto-generated'}")

    # Display certificate criteria
    criteria = []
    if args.cn: criteria.append(f"CN='{args.cn}'")
    if args.o: criteria.append(f"O='{args.o}'")
    if args.ou: criteria.append(f"OU='{args.ou}'")
    if args.email: criteria.append(f"Email='{args.email}'")
    if args.serial: criteria.append(f"Serial='{args.serial}'")
    if args.ca: criteria.append(f"CA='{args.ca}'")

    if criteria:
        print(f"Certificate criteria: {', '.join(criteria)}")

    # Perform signing based on method
    success = False

    try:
        if args.use_pfx:
            success = sign_xml_with_pfx(
                args.file, args.use_pfx, args.pfx_password, args.output, **signing_params
            )
        elif args.use_hsm:
            success = sign_xml_with_hsm(
                args.file, args.token_pin, args.hsm_dll, args.output, **signing_params
            )
        else:  # Default to Windows Store
            success = sign_xml_with_windows_store(
                args.file, args.output, **signing_params
            )

        if success:
            print("\\n[+] XML signing completed successfully!")
        else:
            print("\\n[!] XML signing failed!")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\\n[!] Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n[!] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()