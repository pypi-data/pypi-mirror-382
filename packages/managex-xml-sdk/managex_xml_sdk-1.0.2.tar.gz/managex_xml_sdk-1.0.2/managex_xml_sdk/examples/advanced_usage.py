"""
Advanced usage examples for ManageX XML Signing SDK
"""

import os
from pathlib import Path
from managex_xml_sdk import (
    XMLSigner,
    WindowsStoreConfig,
    PFXConfig,
    HSMConfig,
    CertificateFilter,
    ValidationConfig,
    SignatureEnvelopeParameters,
    SignatureInfo,
    ReferenceInfo,
    KeyInfo,
    SignatureAlgorithm,
    DigestAlgorithm,
    CanonicalizationAlgorithm
)

def example_custom_signature_parameters():
    """Example: Custom signature parameters"""
    print("=== Custom Signature Parameters ===")

    try:
        # Create custom signature info
        signature_info = SignatureInfo(
            signature_id="CustomSignature-2024",
            signature_algorithm=SignatureAlgorithm.RSA_SHA384,
            canonicalization_algorithm=CanonicalizationAlgorithm.EXCLUSIVE_C14N
        )

        # Create custom reference info
        reference_info = ReferenceInfo(
            digest_algorithm=DigestAlgorithm.SHA384,
            reference_id="CustomReference"
        )

        # Create custom key info
        key_info = KeyInfo(
            include_certificate=True,
            include_subject_name=True,
            include_issuer_serial=True,
            include_subject_key_id=True,
            include_public_key=False,
            key_name="CustomKey"
        )

        # Create signature envelope parameters
        signature_params = SignatureEnvelopeParameters(
            signature_info=signature_info,
            reference_info=reference_info,
            key_info=key_info
        )

        # Create signer configuration
        signer_config = WindowsStoreConfig(
            store="MY",
            certificate_filter=CertificateFilter(cn="Custom Certificate")
        )

        # Create and use signer
        signer = XMLSigner(signer_config, signature_params)
        success = signer.sign_file("custom.xml", "custom_signed.xml")

        print(f"Custom signature: {'Success' if success else 'Failed'}")

    except Exception as e:
        print(f"Custom signature error: {e}")

def example_multiple_certificate_sources():
    """Example: Working with multiple certificate sources"""
    print("\n=== Multiple Certificate Sources ===")

    # Define common certificate filter
    cert_filter = CertificateFilter(
        cn="Multi Certificate",
        o="Test Organization"
    )

    # Define validation config
    validation = ValidationConfig.basic_validation()

    # Try Windows Store first
    try:
        print("Trying Windows Certificate Store...")
        store_config = WindowsStoreConfig(
            store="MY",
            certificate_filter=cert_filter,
            validation_config=validation
        )
        signer = XMLSigner(store_config)
        success = signer.sign_file("multi.xml", "multi_store_signed.xml")
        print(f"Windows Store: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"Windows Store failed: {e}")

    # Try PFX if store fails
    try:
        print("Trying PFX file...")
        pfx_config = PFXConfig(
            pfx_file="backup.pfx",
            password="password123",
            certificate_filter=cert_filter,
            validation_config=validation
        )
        signer = XMLSigner(pfx_config)
        success = signer.sign_file("multi.xml", "multi_pfx_signed.xml")
        print(f"PFX file: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"PFX failed: {e}")

    # Try HSM as last resort
    try:
        print("Trying HSM token...")
        hsm_config = HSMConfig(
            pin="123456",
            certificate_filter=cert_filter,
            validation_config=validation
        )
        signer = XMLSigner(hsm_config)
        success = signer.sign_file("multi.xml", "multi_hsm_signed.xml")
        print(f"HSM token: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"HSM failed: {e}")

def example_certificate_discovery():
    """Example: Certificate discovery and selection"""
    print("\n=== Certificate Discovery ===")

    try:
        from managex_xml_sdk import WindowsStoreSigner

        # Create signer
        signer = WindowsStoreSigner(WindowsStoreConfig(store="MY"))

        # Get all certificates
        all_certs = signer.get_all_certificates_from_store()
        print(f"Found {len(all_certs)} total certificates")

        # Filter for signing certificates
        signing_certs = signer.filter_valid_signing_certificates(all_certs)
        print(f"Found {len(signing_certs)} valid signing certificates")

        # Show certificate details
        for i, cert_info in enumerate(signing_certs[:5], 1):  # Show first 5
            print(f"  {i}. {cert_info.subject_name}")
            print(f"     Serial: {cert_info.serial_number}")
            print(f"     Valid: {cert_info.valid_from} to {cert_info.valid_to}")
            print(f"     Thumbprint: {cert_info.thumbprint}")
            print()

    except Exception as e:
        print(f"Certificate discovery error: {e}")

def example_validation_levels():
    """Example: Different validation levels"""
    print("\n=== Validation Levels ===")

    cert_filter = CertificateFilter(cn="Validation Test")

    # Basic validation
    try:
        print("Basic validation...")
        basic_config = ValidationConfig.basic_validation()
        signer_config = WindowsStoreConfig(
            certificate_filter=cert_filter,
            validation_config=basic_config
        )
        signer = XMLSigner(signer_config)
        success = signer.sign_file("validation.xml", "basic_validated.xml")
        print(f"Basic validation: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"Basic validation error: {e}")

    # Strict validation
    try:
        print("Strict validation...")
        strict_config = ValidationConfig.strict_validation()
        signer_config = WindowsStoreConfig(
            certificate_filter=cert_filter,
            validation_config=strict_config
        )
        signer = XMLSigner(signer_config)
        success = signer.sign_file("validation.xml", "strict_validated.xml")
        print(f"Strict validation: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"Strict validation error: {e}")

    # Custom validation
    try:
        print("Custom validation...")
        custom_config = ValidationConfig(
            check_validity=True,
            check_revocation_crl=True,
            check_revocation_ocsp=False,  # Skip OCSP for speed
            trusted_roots_folder="root_certificates",
            require_key_usage_for_signing=True
        )
        signer_config = WindowsStoreConfig(
            certificate_filter=cert_filter,
            validation_config=custom_config
        )
        signer = XMLSigner(signer_config)
        success = signer.sign_file("validation.xml", "custom_validated.xml")
        print(f"Custom validation: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"Custom validation error: {e}")

def example_error_handling():
    """Example: Comprehensive error handling"""
    print("\n=== Error Handling ===")

    from managex_xml_sdk.exceptions import (
        CertificateValidationError,
        SigningError,
        CertificateNotFoundError,
        TrustedRootsNotFoundError
    )

    try:
        # Try to create signer with non-existent certificate
        config = WindowsStoreConfig(
            certificate_filter=CertificateFilter(cn="NonExistentCertificate")
        )
        signer = XMLSigner(config)
        success = signer.sign_file("test.xml", "error_test.xml")

    except CertificateNotFoundError as e:
        print(f"Certificate not found: {e}")
    except CertificateValidationError as e:
        print(f"Certificate validation failed: {e}")
    except SigningError as e:
        print(f"Signing process failed: {e}")
    except TrustedRootsNotFoundError as e:
        print(f"Trusted roots not found: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def example_bulk_operations():
    """Example: Bulk operations with progress tracking"""
    print("\n=== Bulk Operations ===")

    try:
        from managex_xml_sdk import create_xml_signer

        # Configuration
        config = {
            "method": "store",
            "store": "MY",
            "cn": "Bulk Signer"
        }

        # Create signer once for efficiency
        signer = create_xml_signer(**config)

        # Simulate bulk files
        bulk_files = [
            f"bulk_{i:03d}.xml" for i in range(1, 101)  # 100 files
        ]

        # Process with progress tracking
        successful = 0
        failed = 0

        print(f"Processing {len(bulk_files)} files...")

        for i, xml_file in enumerate(bulk_files, 1):
            try:
                output_file = f"signed_{xml_file}"
                success = signer.sign_file(xml_file, output_file)

                if success:
                    successful += 1
                else:
                    failed += 1

                # Progress update every 10 files
                if i % 10 == 0:
                    print(f"Progress: {i}/{len(bulk_files)} "
                          f"(Success: {successful}, Failed: {failed})")

            except Exception as e:
                failed += 1
                print(f"Error processing {xml_file}: {e}")

        print(f"Bulk operation complete:")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Success rate: {successful/len(bulk_files)*100:.1f}%")

    except Exception as e:
        print(f"Bulk operation error: {e}")

def example_configuration_management():
    """Example: Configuration management and templates"""
    print("\n=== Configuration Management ===")

    # Define configuration templates
    CONFIGS = {
        "development": {
            "validation": ValidationConfig(
                check_validity=False,
                check_revocation_crl=False,
                check_revocation_ocsp=False,
                trusted_roots_folder="dev_roots"
            ),
            "signature_id": "DEV-Signature"
        },
        "testing": {
            "validation": ValidationConfig.basic_validation("test_roots"),
            "signature_id": "TEST-Signature"
        },
        "production": {
            "validation": ValidationConfig.strict_validation("prod_roots"),
            "signature_id": "PROD-Signature"
        }
    }

    # Select environment
    environment = "testing"  # This could come from environment variable
    config_template = CONFIGS[environment]

    try:
        # Create signer with environment-specific configuration
        signer_config = WindowsStoreConfig(
            store="MY",
            certificate_filter=CertificateFilter(cn="Environment Test"),
            validation_config=config_template["validation"]
        )

        # Create signature parameters
        signature_params = SignatureEnvelopeParameters.create_default(
            signature_id=config_template["signature_id"]
        )

        # Create and use signer
        signer = XMLSigner(signer_config, signature_params)
        success = signer.sign_file("env_test.xml", f"{environment}_signed.xml")

        print(f"Environment '{environment}' signing: {'Success' if success else 'Failed'}")

    except Exception as e:
        print(f"Configuration management error: {e}")

if __name__ == "__main__":
    print("ManageX XML Signing SDK - Advanced Examples")
    print("=" * 60)

    # Run all advanced examples
    example_custom_signature_parameters()
    example_multiple_certificate_sources()
    example_certificate_discovery()
    example_validation_levels()
    example_error_handling()
    example_bulk_operations()
    example_configuration_management()

    print("\n" + "=" * 60)
    print("Advanced examples completed!")