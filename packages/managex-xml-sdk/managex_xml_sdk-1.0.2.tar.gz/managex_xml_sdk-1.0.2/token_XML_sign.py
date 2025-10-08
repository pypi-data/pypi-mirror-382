#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import base64
import hashlib
from lxml import etree
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import PyKCS11 as PK11
import argparse
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


# === Configuration ===
dllpath = r"C:\Windows\System32\Watchdata\PROXKey CSP India V3.0\wdpkcs.dll"
token_label = "Aniket"
token_pin = "123456789"
target_cn = "Aniket Chaturvedi"  # Certificate CN to use for signing

# dllpath = r"C:\Windows\System32\eps2003csp11v2.dll"
# token_label = "HYP2003"
# token_pin = "12345678"
# target_cn = "Pintu Prajapati"  # Certificate CN to use for signing


# XML file to sign (change this to sign different files)
xml_file_to_sign = "new.xml"  # Can be any XML file path

# Signature ID
signature_id = "PKI Mode 2.8"


# === XML Signature Parameters and Validation ===

class SignatureAlgorithm(Enum):
    RSA_SHA1 = "http://www.w3.org/2000/09/xmldsig#rsa-sha1"
    RSA_SHA256 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
    RSA_SHA384 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha384"
    RSA_SHA512 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha512"
    DSA_SHA1 = "http://www.w3.org/2000/09/xmldsig#dsa-sha1"
    DSA_SHA256 = "http://www.w3.org/2009/xmldsig11#dsa-sha256"
    ECDSA_SHA1 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha1"
    ECDSA_SHA256 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256"
    ECDSA_SHA384 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha384"
    ECDSA_SHA512 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha512"

class DigestAlgorithm(Enum):
    SHA1 = "http://www.w3.org/2000/09/xmldsig#sha1"
    SHA256 = "http://www.w3.org/2001/04/xmlenc#sha256"
    SHA384 = "http://www.w3.org/2001/04/xmldsig-more#sha384"
    SHA512 = "http://www.w3.org/2001/04/xmlenc#sha512"

class CanonicalizationAlgorithm(Enum):
    C14N_OMIT_COMMENTS = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
    C14N_WITH_COMMENTS = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments"
    EXCLUSIVE_C14N = "http://www.w3.org/2001/10/xml-exc-c14n#"

class TransformAlgorithm(Enum):
    ENVELOPED_SIGNATURE = "http://www.w3.org/2000/09/xmldsig#enveloped-signature"
    C14N_OMIT_COMMENTS = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
    EXCLUSIVE_C14N = "http://www.w3.org/2001/10/xml-exc-c14n#"

@dataclass
class SignatureInfo:
    signature_id: Optional[str] = None
    canonicalization_algorithm: CanonicalizationAlgorithm = CanonicalizationAlgorithm.C14N_OMIT_COMMENTS
    signature_algorithm: SignatureAlgorithm = SignatureAlgorithm.RSA_SHA256

    def validate(self) -> bool:
        """Validate SignatureInfo parameters"""
        if self.signature_id and not isinstance(self.signature_id, str):
            raise ValueError("signature_id must be a string")
        if not isinstance(self.canonicalization_algorithm, CanonicalizationAlgorithm):
            raise ValueError("Invalid canonicalization algorithm")
        if not isinstance(self.signature_algorithm, SignatureAlgorithm):
            raise ValueError("Invalid signature algorithm")
        return True

@dataclass
class ReferenceInfo:
    uri: str = ""
    digest_algorithm: DigestAlgorithm = DigestAlgorithm.SHA256
    transforms: List[TransformAlgorithm] = None
    reference_id: Optional[str] = None

    def __post_init__(self):
        if self.transforms is None:
            self.transforms = [TransformAlgorithm.ENVELOPED_SIGNATURE, TransformAlgorithm.EXCLUSIVE_C14N]

    def validate(self) -> bool:
        """Validate ReferenceInfo parameters"""
        if not isinstance(self.uri, str):
            raise ValueError("URI must be a string")
        if not isinstance(self.digest_algorithm, DigestAlgorithm):
            raise ValueError("Invalid digest algorithm")
        if not isinstance(self.transforms, list):
            raise ValueError("Transforms must be a list")
        for transform in self.transforms:
            if not isinstance(transform, TransformAlgorithm):
                raise ValueError("Invalid transform algorithm")
        if self.reference_id and not isinstance(self.reference_id, str):
            raise ValueError("reference_id must be a string")
        return True

@dataclass
class KeyInfo:
    include_subject_name: bool = True
    include_certificate: bool = True
    include_public_key: bool = False
    include_issuer_serial: bool = False
    include_subject_key_id: bool = False
    key_name: Optional[str] = None

    def validate(self) -> bool:
        """Validate KeyInfo parameters"""
        if not isinstance(self.include_subject_name, bool):
            raise ValueError("include_subject_name must be boolean")
        if not isinstance(self.include_certificate, bool):
            raise ValueError("include_certificate must be boolean")
        if not isinstance(self.include_public_key, bool):
            raise ValueError("include_public_key must be boolean")
        if not isinstance(self.include_issuer_serial, bool):
            raise ValueError("include_issuer_serial must be boolean")
        if not isinstance(self.include_subject_key_id, bool):
            raise ValueError("include_subject_key_id must be boolean")
        if self.key_name and not isinstance(self.key_name, str):
            raise ValueError("key_name must be a string")
        return True

@dataclass
class SignatureEnvelopeParameters:
    """Complete XML signature envelope parameters with validation"""
    signature_info: SignatureInfo
    reference_info: ReferenceInfo
    key_info: KeyInfo
    namespace_prefix: Optional[str] = None

    def __post_init__(self):
        """Validate all parameters after initialization"""
        self.validate()

    def validate(self) -> bool:
        """Validate all signature envelope parameters"""
        try:
            if not isinstance(self.signature_info, SignatureInfo):
                raise ValueError("signature_info must be SignatureInfo instance")
            self.signature_info.validate()

            if not isinstance(self.reference_info, ReferenceInfo):
                raise ValueError("reference_info must be ReferenceInfo instance")
            self.reference_info.validate()

            if not isinstance(self.key_info, KeyInfo):
                raise ValueError("key_info must be KeyInfo instance")
            self.key_info.validate()

            if self.namespace_prefix and not isinstance(self.namespace_prefix, str):
                raise ValueError("namespace_prefix must be a string")

            return True
        except ValueError as e:
            print(f"Validation error: {e}")
            raise



# === HSM Signer Class ===
class HSMSigner:
    def __init__(self, dll_path):
        self.dll_path = dll_path
        self.pkcs11 = PK11.PyKCS11Lib()
        self.pkcs11.load(dll_path)
        self.session = None

    def login(self, token_label, pin):
        slots = self.pkcs11.getSlotList(tokenPresent=True)
        for slot in slots:
            try:
                token = self.pkcs11.getTokenInfo(slot)
                # Fix for token labels with null characters and trailing spaces
                actual_label = token.label.rstrip('\x00 ')
                if actual_label == token_label:
                    self.session = self.pkcs11.openSession(slot, PK11.CKF_SERIAL_SESSION | PK11.CKF_RW_SESSION)
                    self.session.login(pin)
                    return True
            except PK11.PyKCS11Error:
                continue
        return False

    def logout(self):
        if self.session:
            try:
                self.session.logout()
                self.session.closeSession()
            except:
                pass

    def get_certificate(self):
        if not self.session:
            return None, None, None

        try:
            pk11objects = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_CERTIFICATE)]
            )
            all_attributes = [PK11.CKA_VALUE, PK11.CKA_ID]

            for obj in pk11objects:
                try:
                    attrs = self.session.getAttributeValue(obj, all_attributes)
                    attr_dict = dict(zip(all_attributes, attrs))
                    cert_bytes = bytes(attr_dict[PK11.CKA_VALUE])
                    keyid = bytes(attr_dict[PK11.CKA_ID])

                    cert = x509.load_der_x509_certificate(cert_bytes, backend=default_backend())
                    cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                    if cn == target_cn:
                        print(f"[+] Found certificate with CN = {cn}")
                        return keyid, cert_bytes, cert
                except PK11.PyKCS11Error:
                    continue

        except Exception as e:
            print(f"Error finding certificate: {e}")

        print(f"[-] No certificate found with CN = {target_cn}")
        return None, None, None

    def sign_data(self, keyid, data):
        if not self.session:
            return None

        try:
            privKey = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY), (PK11.CKA_ID, keyid)]
            )[0]

            # Use SHA1 with RSA PKCS#1 mechanism
            mechanism = PK11.Mechanism(PK11.CKM_SHA1_RSA_PKCS, None)
            signature = self.session.sign(privKey, data, mechanism)
            return bytes(signature)
        except Exception as e:
            print(f"Error signing data: {e}")
            return None

    def sign_data_with_mechanism(self, keyid, data, mechanism):
        """Sign data with specified PKCS#11 mechanism"""
        if not self.session:
            return None

        try:
            privKey = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY), (PK11.CKA_ID, keyid)]
            )[0]

            signature = self.session.sign(privKey, data, mechanism)
            return bytes(signature)
        except Exception as e:
            print(f"Error signing data with mechanism: {e}")
            return None


def apply_enveloped_transform(element):
    """Apply enveloped signature transform - remove all Signature elements"""
    # Create a copy to avoid modifying the original
    elem_copy = etree.fromstring(etree.tostring(element))

    # Remove all Signature elements from the copy
    signature_elements = elem_copy.xpath('//ds:Signature',
                                       namespaces={'ds': 'http://www.w3.org/2000/09/xmldsig#'})
    for sig in signature_elements:
        sig.getparent().remove(sig)

    return elem_copy

def get_hash_algorithm(digest_algorithm: DigestAlgorithm):
    """Get the appropriate hash algorithm based on digest algorithm"""
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

def get_pkcs11_mechanism(signature_algorithm: SignatureAlgorithm):
    """Get the appropriate PKCS#11 mechanism based on signature algorithm"""
    if signature_algorithm == SignatureAlgorithm.RSA_SHA1:
        return PK11.Mechanism(PK11.CKM_SHA1_RSA_PKCS, None)
    elif signature_algorithm == SignatureAlgorithm.RSA_SHA256:
        return PK11.Mechanism(PK11.CKM_SHA256_RSA_PKCS, None)
    elif signature_algorithm == SignatureAlgorithm.RSA_SHA384:
        return PK11.Mechanism(PK11.CKM_SHA384_RSA_PKCS, None)
    elif signature_algorithm == SignatureAlgorithm.RSA_SHA512:
        return PK11.Mechanism(PK11.CKM_SHA512_RSA_PKCS, None)
    elif signature_algorithm == SignatureAlgorithm.ECDSA_SHA1:
        return PK11.Mechanism(PK11.CKM_ECDSA_SHA1, None)
    elif signature_algorithm == SignatureAlgorithm.ECDSA_SHA256:
        return PK11.Mechanism(PK11.CKM_ECDSA_SHA256, None)
    elif signature_algorithm == SignatureAlgorithm.ECDSA_SHA384:
        return PK11.Mechanism(PK11.CKM_ECDSA_SHA384, None)
    elif signature_algorithm == SignatureAlgorithm.ECDSA_SHA512:
        return PK11.Mechanism(PK11.CKM_ECDSA_SHA512, None)
    else:
        raise ValueError(f"Unsupported signature algorithm: {signature_algorithm}")

def sign_xml_document(xml_content, cert, keyid, signer, envelope_params: SignatureEnvelopeParameters = None):
    """Add XMLDSig signature to existing XML document with validated parameters"""

    # Use default parameters if none provided
    if envelope_params is None:
        envelope_params = SignatureEnvelopeParameters(
            signature_info=SignatureInfo(),
            reference_info=ReferenceInfo(),
            key_info=KeyInfo()
        )

    # Validate parameters
    envelope_params.validate()

    # Parse the existing XML document
    doc = etree.fromstring(xml_content)

    # Create namespace map
    ns_map = {envelope_params.namespace_prefix: "http://www.w3.org/2000/09/xmldsig#"} if envelope_params.namespace_prefix else {None: "http://www.w3.org/2000/09/xmldsig#"}

    # Create a placeholder signature to get the final structure
    temp_signature = etree.Element("Signature", nsmap=ns_map)
    if envelope_params.signature_info.signature_id:
        temp_signature.set("Id", envelope_params.signature_info.signature_id)
    doc.append(temp_signature)

    # Apply enveloped signature transform for digest calculation
    transformed_doc = apply_enveloped_transform(doc)

    # Canonicalize the transformed document for digest calculation
    c14n_xml = etree.tostring(transformed_doc, method='c14n', exclusive=False)

    # Calculate digest of canonicalized XML using specified algorithm
    hash_algo = get_hash_algorithm(envelope_params.reference_info.digest_algorithm)
    digest = hash_algo(c14n_xml).digest()
    digest_b64 = base64.b64encode(digest).decode('utf-8')

    # Remove the temporary signature
    doc.remove(temp_signature)

    # Create SignedInfo element
    signed_info = etree.Element("SignedInfo", nsmap=ns_map)

    # Canonicalization method
    canon_method = etree.SubElement(signed_info, "CanonicalizationMethod")
    canon_method.set("Algorithm", envelope_params.signature_info.canonicalization_algorithm.value)

    # Signature method
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

    # Digest method
    digest_method = etree.SubElement(reference, "DigestMethod")
    digest_method.set("Algorithm", envelope_params.reference_info.digest_algorithm.value)

    # Digest value
    digest_value = etree.SubElement(reference, "DigestValue")
    digest_value.text = digest_b64

    # Canonicalize SignedInfo for signing
    signed_info_c14n = etree.tostring(signed_info, method='c14n', exclusive=False)

    # Get the appropriate mechanism and sign the SignedInfo
    mechanism = get_pkcs11_mechanism(envelope_params.signature_info.signature_algorithm)
    signature_bytes = signer.sign_data_with_mechanism(keyid, signed_info_c14n, mechanism)
    if signature_bytes is None:
        raise Exception("Failed to sign data")

    signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')

    # Create the complete Signature element
    signature_elem = etree.Element("Signature", nsmap=ns_map)
    if envelope_params.signature_info.signature_id:
        signature_elem.set("Id", envelope_params.signature_info.signature_id)
    signature_elem.append(signed_info)

    # Signature Value
    sig_value = etree.SubElement(signature_elem, "SignatureValue")
    sig_value.text = signature_b64

    # KeyInfo with certificate (if configured)
    if (envelope_params.key_info.include_subject_name or envelope_params.key_info.include_certificate or
        envelope_params.key_info.include_public_key or envelope_params.key_info.include_issuer_serial or
        envelope_params.key_info.include_subject_key_id):
        key_info = etree.SubElement(signature_elem, "KeyInfo")

        if envelope_params.key_info.key_name:
            key_name_elem = etree.SubElement(key_info, "KeyName")
            key_name_elem.text = envelope_params.key_info.key_name

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
                    pass  # SKI not present in certificate

            if envelope_params.key_info.include_certificate:
                x509_cert_elem = etree.SubElement(x509_data, "X509Certificate")
                cert_der = cert.public_bytes(serialization.Encoding.DER)
                cert_b64 = base64.b64encode(cert_der).decode('utf-8')
                x509_cert_elem.text = cert_b64

        if envelope_params.key_info.include_public_key:
            key_value = etree.SubElement(key_info, "KeyValue")
            public_key = cert.public_key()

            # Handle different key types
            if hasattr(public_key, 'public_numbers'):  # RSA key
                rsa_key_value = etree.SubElement(key_value, "RSAKeyValue")
                public_numbers = public_key.public_numbers()

                modulus = etree.SubElement(rsa_key_value, "Modulus")
                modulus.text = base64.b64encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')).decode('utf-8')

                exponent = etree.SubElement(rsa_key_value, "Exponent")
                exponent.text = base64.b64encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, 'big')).decode('utf-8')
            else:
                # For EC keys, we would need additional handling here
                pass

    # Add signature to the original document
    doc.append(signature_elem)

    return doc

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Sign XML files using HSM with validated signature parameters')
    parser.add_argument('--file', '-f', default=xml_file_to_sign,
                       help=f'XML file to sign (default: {xml_file_to_sign})')
    parser.add_argument('--output', '-o',
                       help='Output file name (default: <input_file>_signed.xml)')
    parser.add_argument('--sig-algo', choices=['rsa-sha1', 'rsa-sha256', 'rsa-sha384', 'rsa-sha512',
                                               'ecdsa-sha1', 'ecdsa-sha256', 'ecdsa-sha384', 'ecdsa-sha512'],
                       default='rsa-sha256', help='Signature algorithm (default: rsa-sha256)')
    parser.add_argument('--digest-algo', choices=['sha1', 'sha256', 'sha384', 'sha512'], default='sha256',
                       help='Digest algorithm (default: sha256)')
    parser.add_argument('--ref-id', help='Optional reference ID')
    parser.add_argument('--include-public-key', action='store_true',
                       help='Include public key in KeyInfo')
    parser.add_argument('--include-issuer-serial', action='store_true',
                       help='Include X509IssuerSerial in KeyInfo')
    parser.add_argument('--include-subject-key-id', action='store_true',
                       help='Include X509SKI (Subject Key Identifier) in KeyInfo')
    parser.add_argument('--exclude-cert', action='store_true',
                       help='Exclude certificate from KeyInfo')
    parser.add_argument('--exclude-subject', action='store_true',
                       help='Exclude subject name from KeyInfo')
    args = parser.parse_args()

    input_file = args.file

    # Check if input file exists
    if not os.path.exists(input_file):
        sys.exit(f"Error: File '{input_file}' not found!")

    # Generate output filename
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_signed.xml"

    # Configure signature envelope parameters
    try:
        # Map command line arguments to enums
        sig_algo_map = {
            'rsa-sha1': SignatureAlgorithm.RSA_SHA1,
            'rsa-sha256': SignatureAlgorithm.RSA_SHA256,
            'rsa-sha384': SignatureAlgorithm.RSA_SHA384,
            'rsa-sha512': SignatureAlgorithm.RSA_SHA512,
            'ecdsa-sha1': SignatureAlgorithm.ECDSA_SHA1,
            'ecdsa-sha256': SignatureAlgorithm.ECDSA_SHA256,
            'ecdsa-sha384': SignatureAlgorithm.ECDSA_SHA384,
            'ecdsa-sha512': SignatureAlgorithm.ECDSA_SHA512
        }
        digest_algo_map = {
            'sha1': DigestAlgorithm.SHA1,
            'sha256': DigestAlgorithm.SHA256,
            'sha384': DigestAlgorithm.SHA384,
            'sha512': DigestAlgorithm.SHA512
        }

        # Create signature parameters with validation (signature_id is fixed to ManageX-Signature)
        signature_info = SignatureInfo(
            signature_algorithm=sig_algo_map[args.sig_algo]
        )

        reference_info = ReferenceInfo(
            digest_algorithm=digest_algo_map[args.digest_algo],
            reference_id=args.ref_id
        )

        key_info = KeyInfo(
            include_subject_name=not args.exclude_subject,
            include_certificate=not args.exclude_cert,
            include_public_key=args.include_public_key,
            include_issuer_serial=args.include_issuer_serial,
            include_subject_key_id=args.include_subject_key_id
        )

        envelope_params = SignatureEnvelopeParameters(
            signature_info=signature_info,
            reference_info=reference_info,
            key_info=key_info
        )

        print(f"[+] Using signature algorithm: {args.sig_algo}")
        print(f"[+] Using digest algorithm: {args.digest_algo}")
        print(f"[+] Signature ID: ManageX-Signature (fixed)")

    except ValueError as e:
        sys.exit(f"Parameter validation error: {e}")

    # Initialize HSM signer
    signer = HSMSigner(dllpath)

    # Login to token
    if not signer.login(token_label, token_pin):
        sys.exit("Failed to login to token. Exiting...")

    try:
        # Get certificate and key ID
        keyid, cert_bytes, cert = signer.get_certificate()
        if keyid is None:
            sys.exit("Certificate not found. Exiting...")

        # Read XML file to sign
        print(f"[+] Reading XML file: {input_file}")
        with open(input_file, "rb") as f:
            xml_content = f.read()

        # Create signed XML with validated parameters
        print("[+] Adding XML signature with validated parameters...")
        signed_doc = sign_xml_document(xml_content, cert, keyid, signer, envelope_params)

        # Write output
        print(f"[+] Writing signed XML to: {output_file}")
        signed_xml = etree.tostring(signed_doc, encoding="UTF-8", xml_declaration=True, pretty_print=False)
        with open(output_file, "wb") as f:
            f.write(signed_xml)

        print(f"[+] XML successfully signed with validated parameters! Output: {output_file}")

    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)
    finally:
        signer.logout()


if __name__ == "__main__":
    main()
