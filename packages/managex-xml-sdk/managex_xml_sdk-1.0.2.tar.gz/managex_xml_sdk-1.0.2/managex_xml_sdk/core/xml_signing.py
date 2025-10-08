"""
XML Digital Signature Implementation for ManageX SDK
Based on XML-Signature Syntax and Processing (xmldsig-core)
"""

import base64
import hashlib
from lxml import etree
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from ..models.signature_models import (
    SignatureEnvelopeParameters, DigestAlgorithm, TransformAlgorithm
)
from ..exceptions import SigningError


def apply_enveloped_transform(element):
    """Apply enveloped signature transform (remove existing signatures)"""
    elem_copy = etree.fromstring(etree.tostring(element))
    signature_elements = elem_copy.xpath('//ds:Signature',
                                       namespaces={'ds': 'http://www.w3.org/2000/09/xmldsig#'})
    for sig in signature_elements:
        sig.getparent().remove(sig)
    return elem_copy


def get_hash_algorithm(digest_algorithm: DigestAlgorithm):
    """Get hash algorithm function from digest algorithm enum"""
    if digest_algorithm == DigestAlgorithm.SHA1:
        return hashlib.sha1
    elif digest_algorithm == DigestAlgorithm.SHA256:
        return hashlib.sha256
    elif digest_algorithm == DigestAlgorithm.SHA384:
        return hashlib.sha384
    elif digest_algorithm == DigestAlgorithm.SHA512:
        return hashlib.sha512
    else:
        raise ValueError(f"Unsupported digest algorithm: {digest_algorithm}")


def sign_xml_document(xml_content: bytes, cert: x509.Certificate, signer,
                     envelope_params: SignatureEnvelopeParameters = None) -> bytes:
    """
    Sign XML document using XML Digital Signature standards

    Args:
        xml_content: XML content to sign as bytes
        cert: Certificate for signing
        signer: Signer instance with sign_data method
        envelope_params: Signature envelope parameters

    Returns:
        Signed XML content as bytes

    Raises:
        SigningError: If signing fails
    """
    try:
        if envelope_params is None:
            envelope_params = SignatureEnvelopeParameters.create_default()

        envelope_params.validate()
        doc = etree.fromstring(xml_content)

        # Set up namespace mapping
        ns_map = {envelope_params.namespace_prefix: "http://www.w3.org/2000/09/xmldsig#"} if envelope_params.namespace_prefix else {None: "http://www.w3.org/2000/09/xmldsig#"}

        # Create temporary signature element to apply enveloped transform
        temp_signature = etree.Element("Signature", nsmap=ns_map)
        if envelope_params.signature_info.signature_id:
            temp_signature.set("Id", envelope_params.signature_info.signature_id)
        doc.append(temp_signature)

        # Apply enveloped transform and canonicalize
        transformed_doc = apply_enveloped_transform(doc)
        c14n_xml = etree.tostring(transformed_doc, method='c14n', exclusive=False)

        # Calculate digest of the document
        hash_algo = get_hash_algorithm(envelope_params.reference_info.digest_algorithm)
        digest = hash_algo(c14n_xml).digest()
        digest_b64 = base64.b64encode(digest).decode('utf-8')

        # Remove temporary signature
        doc.remove(temp_signature)

        # Build SignedInfo element
        signed_info = etree.Element("SignedInfo", nsmap=ns_map)

        # CanonicalizationMethod
        canon_method = etree.SubElement(signed_info, "CanonicalizationMethod")
        canon_method.set("Algorithm", envelope_params.signature_info.canonicalization_algorithm.value)

        # SignatureMethod
        sig_method = etree.SubElement(signed_info, "SignatureMethod")
        sig_method.set("Algorithm", envelope_params.signature_info.signature_algorithm.value)

        # Reference
        reference = etree.SubElement(signed_info, "Reference")
        reference.set("URI", envelope_params.reference_info.uri)
        if envelope_params.reference_info.reference_id:
            reference.set("Id", envelope_params.reference_info.reference_id)

        # Transforms
        transforms = etree.SubElement(reference, "Transforms")
        for transform_algo in envelope_params.reference_info.transforms:
            transform = etree.SubElement(transforms, "Transform")
            transform.set("Algorithm", transform_algo.value)

        # DigestMethod
        digest_method = etree.SubElement(reference, "DigestMethod")
        digest_method.set("Algorithm", envelope_params.reference_info.digest_algorithm.value)

        # DigestValue
        digest_value = etree.SubElement(reference, "DigestValue")
        digest_value.text = digest_b64

        # Canonicalize SignedInfo for signing
        signed_info_c14n = etree.tostring(signed_info, method='c14n', exclusive=False)

        # Sign the canonicalized SignedInfo
        signature_bytes = signer.sign_data(signed_info_c14n, envelope_params.signature_info.signature_algorithm)
        if signature_bytes is None:
            raise SigningError("Failed to sign data - signer returned None")

        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')

        # Build complete Signature element
        signature_elem = etree.Element("Signature", nsmap=ns_map)
        if envelope_params.signature_info.signature_id:
            signature_elem.set("Id", envelope_params.signature_info.signature_id)
        signature_elem.append(signed_info)

        # SignatureValue
        sig_value = etree.SubElement(signature_elem, "SignatureValue")
        sig_value.text = signature_b64

        # KeyInfo (if any elements are requested)
        if (envelope_params.key_info.include_subject_name or envelope_params.key_info.include_certificate or
            envelope_params.key_info.include_public_key or envelope_params.key_info.include_issuer_serial or
            envelope_params.key_info.include_subject_key_id):
            key_info = etree.SubElement(signature_elem, "KeyInfo")

            if envelope_params.key_info.key_name:
                key_name_elem = etree.SubElement(key_info, "KeyName")
                key_name_elem.text = envelope_params.key_info.key_name

            # X509Data
            if (envelope_params.key_info.include_subject_name or envelope_params.key_info.include_certificate or
                envelope_params.key_info.include_issuer_serial or envelope_params.key_info.include_subject_key_id):
                x509_data = etree.SubElement(key_info, "X509Data")

                if envelope_params.key_info.include_issuer_serial:
                    issuer_serial = etree.SubElement(x509_data, "X509IssuerSerial")
                    issuer_name = etree.SubElement(issuer_serial, "X509IssuerName")
                    issuer_name.text = cert.issuer.rfc4514_string()
                    serial_number = etree.SubElement(issuer_serial, "X509SerialNumber")
                    serial_number.text = str(cert.serial_number)

                if envelope_params.key_info.include_subject_name:
                    subject_name = etree.SubElement(x509_data, "X509SubjectName")
                    subject_name.text = cert.subject.rfc4514_string()

                if envelope_params.key_info.include_subject_key_id:
                    try:
                        ski_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.SUBJECT_KEY_IDENTIFIER)
                        ski_elem = etree.SubElement(x509_data, "X509SKI")
                        ski_elem.text = base64.b64encode(ski_ext.value.digest).decode('utf-8')
                    except x509.ExtensionNotFound:
                        pass

                if envelope_params.key_info.include_certificate:
                    x509_cert_elem = etree.SubElement(x509_data, "X509Certificate")
                    cert_der = cert.public_bytes(serialization.Encoding.DER)
                    cert_b64 = base64.b64encode(cert_der).decode('utf-8')
                    x509_cert_elem.text = cert_b64

            # KeyValue (for public key)
            if envelope_params.key_info.include_public_key:
                key_value = etree.SubElement(key_info, "KeyValue")
                public_key = cert.public_key()

                if hasattr(public_key, 'public_numbers'):  # RSA key
                    rsa_key_value = etree.SubElement(key_value, "RSAKeyValue")
                    public_numbers = public_key.public_numbers()

                    modulus = etree.SubElement(rsa_key_value, "Modulus")
                    modulus.text = base64.b64encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')).decode('utf-8')

                    exponent = etree.SubElement(rsa_key_value, "Exponent")
                    exponent.text = base64.b64encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, 'big')).decode('utf-8')

        # Add signature to document
        doc.append(signature_elem)

        # Return signed XML as bytes
        signed_xml = etree.tostring(doc, encoding="UTF-8", xml_declaration=False, pretty_print=False)
        return signed_xml

    except Exception as e:
        raise SigningError(f"XML signing failed: {e}")