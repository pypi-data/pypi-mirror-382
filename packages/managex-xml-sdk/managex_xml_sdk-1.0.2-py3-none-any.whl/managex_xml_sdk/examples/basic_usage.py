"""
Basic usage examples for ManageX XML Signing SDK
"""

from managex_xml_sdk import (
    create_xml_signer,
    sign_xml_file,
    validate_certificate,
    get_available_certificates,
    CertificateFilter,
    ValidationConfig
)

def example_quick_signing():
    """Example: Quick XML signing"""
    print("=== Quick XML Signing ===")

    # Simple configuration
    config = {
        "method": "store",
        "store": "MY",
        "cn": "Test Certificate"
    }

    try:
        success = sign_xml_file("sample.xml", "signed_sample.xml", config)
        print(f"Quick signing result: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"Quick signing error: {e}")

def example_windows_store_signing():
    """Example: Windows Certificate Store signing"""
    print("\n=== Windows Store Signing ===")

    try:
        # Create signer with specific criteria
        signer = create_xml_signer(
            method="store",
            store="MY",
            cn="Digital Signature",
            o="My Organization"
        )

        # Sign XML file
        success = signer.sign_file("document.xml", "signed_document.xml")
        print(f"Windows Store signing: {'Success' if success else 'Failed'}")

    except Exception as e:
        print(f"Windows Store signing error: {e}")

def example_pfx_signing():
    """Example: PFX file signing"""
    print("\n=== PFX File Signing ===")

    try:
        # Create PFX signer
        signer = create_xml_signer(
            method="pfx",
            pfx_file="certificate.pfx",
            password="password123",
            cn="PFX Certificate"
        )

        # Sign XML file
        success = signer.sign_file("document.xml", "pfx_signed_document.xml")
        print(f"PFX signing: {'Success' if success else 'Failed'}")

    except Exception as e:
        print(f"PFX signing error: {e}")

def example_hsm_signing():
    """Example: HSM token signing"""
    print("\n=== HSM Token Signing ===")

    try:
        # Create HSM signer
        signer = create_xml_signer(
            method="hsm",
            dll_path="C:\\Windows\\System32\\eToken.dll",
            pin="123456",
            cn="HSM Certificate"
        )

        # Sign XML file
        success = signer.sign_file("document.xml", "hsm_signed_document.xml")
        print(f"HSM signing: {'Success' if success else 'Failed'}")

    except Exception as e:
        print(f"HSM signing error: {e}")

def example_certificate_validation():
    """Example: Certificate validation"""
    print("\n=== Certificate Validation ===")

    try:
        # Validate certificate file
        is_valid = validate_certificate(
            cert_path="certificate.pem",
            trusted_roots_folder="root_certificates"
        )
        print(f"Certificate validation: {'Valid' if is_valid else 'Invalid'}")

    except Exception as e:
        print(f"Certificate validation error: {e}")

def example_list_certificates():
    """Example: List available certificates"""
    print("\n=== Available Certificates ===")

    try:
        # Get Windows Store certificates
        store_certs = get_available_certificates("store", store="MY")
        print(f"Windows Store certificates: {len(store_certs)}")

        for cert in store_certs[:3]:  # Show first 3
            print(f"  - {cert.subject_name}")

        # Get HSM certificates
        hsm_tokens = get_available_certificates("hsm")
        print(f"HSM tokens: {len(hsm_tokens)}")

        for token in hsm_tokens[:3]:  # Show first 3
            print(f"  - {token['label']} ({token['model']})")

    except Exception as e:
        print(f"List certificates error: {e}")

def example_advanced_configuration():
    """Example: Advanced configuration with validation"""
    print("\n=== Advanced Configuration ===")

    try:
        from managex_xml_sdk import (
            XMLSigner,
            WindowsStoreConfig,
            SignatureEnvelopeParameters
        )

        # Create certificate filter
        cert_filter = CertificateFilter(
            cn="Advanced Certificate",
            o="Advanced Organization",
            email="advanced@company.com"
        )

        # Create strict validation config
        validation = ValidationConfig.strict_validation("root_certificates")

        # Create signer configuration
        config = WindowsStoreConfig(
            store="MY",
            certificate_filter=cert_filter,
            validation_config=validation
        )

        # Create signature parameters
        signature_params = SignatureEnvelopeParameters.create_default(
            signature_id="Advanced-Signature-2024"
        )

        # Create and use signer
        signer = XMLSigner(config, signature_params)
        success = signer.sign_file("advanced.xml", "advanced_signed.xml")

        print(f"Advanced signing: {'Success' if success else 'Failed'}")

    except Exception as e:
        print(f"Advanced configuration error: {e}")

def example_batch_signing():
    """Example: Batch signing multiple files"""
    print("\n=== Batch Signing ===")

    try:
        # Configuration for batch signing
        config = {
            "method": "store",
            "store": "MY",
            "cn": "Batch Signer"
        }

        # Create signer once
        signer = create_xml_signer(**config)

        # Files to sign
        files_to_sign = [
            ("batch1.xml", "signed_batch1.xml"),
            ("batch2.xml", "signed_batch2.xml"),
            ("batch3.xml", "signed_batch3.xml")
        ]

        # Sign all files
        results = []
        for input_file, output_file in files_to_sign:
            try:
                success = signer.sign_file(input_file, output_file)
                results.append((input_file, success))
                print(f"  {input_file} -> {output_file}: {'✓' if success else '✗'}")
            except Exception as e:
                results.append((input_file, False))
                print(f"  {input_file} -> Error: {e}")

        successful = sum(1 for _, success in results if success)
        print(f"Batch signing complete: {successful}/{len(files_to_sign)} successful")

    except Exception as e:
        print(f"Batch signing error: {e}")

if __name__ == "__main__":
    print("ManageX XML Signing SDK - Examples")
    print("=" * 50)

    # Run all examples
    example_quick_signing()
    example_windows_store_signing()
    example_pfx_signing()
    example_hsm_signing()
    example_certificate_validation()
    example_list_certificates()
    example_advanced_configuration()
    example_batch_signing()

    print("\n" + "=" * 50)
    print("Examples completed!")