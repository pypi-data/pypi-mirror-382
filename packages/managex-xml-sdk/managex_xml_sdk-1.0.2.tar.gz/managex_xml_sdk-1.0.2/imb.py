import os
import sys
import base64
import hashlib
import subprocess
import json
import tempfile
import glob
import requests
from lxml import etree
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from cryptography.hazmat.primitives.serialization import pkcs12
import argparse
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
from win32 import win32crypt
from win32.lib import win32cryptcon
from datetime import datetime, timezone
import ipaddress
import re

# HSM support (optional import)
try:
    import PyKCS11 as PK11
    HSM_AVAILABLE = True
except ImportError:
    HSM_AVAILABLE = False
    print("[WARNING] PyKCS11 not available - HSM support disabled")


# === Enhanced Configuration ===
app_name = "PKI Mode"
xml_file_to_sign = "new.xml"  # Can be any XML file path
signature_id = "PKI Mode 2.8"
cert_store = "MY"  # Certificate store (MY = Personal, ROOT = Trusted Root, etc.)

# Enhanced Certificate Validation Configuration (will be updated by CLI args)
check_validity = "no"  # Check if certificate is valid (not expired)
check_revocation_crl = "no"  # Check certificate revocation via CRL
check_revocation_ocsp = "no"  # Check certificate revocation via OCSP
root_certificates_folder = "root_certificates"  # Folder containing trusted root certificates (.pem files)

# Enhanced Certificate Matching Criteria (will be updated by CLI args)
target_cn = ""   # Certificate CN to use for signing
target_o = ""    # Organization name to match
target_ou = ""   # Organization Unit name to match  
target_e = ""    # Email from SAN RFC822 Name to match
target_sn = ""   # Certificate serial number (hex format)
target_ca = ""   # Certifying Authority name to match

# HSM Configuration (will be auto-detected based on connected tokens)
hsm_dll_paths = [
    r"C:\Windows\System32\SignatureP11.dll",
    r"C:\Windows\System32\eToken.dll",
    r"C:\Windows\System32\eps2003csp11v2",
    r"C:\Windows\System32\CryptoIDA_pkcs11.dll"
]


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
    signature_info: SignatureInfo
    reference_info: ReferenceInfo
    key_info: KeyInfo
    namespace_prefix: Optional[str] = None

    def __post_init__(self):
        self.validate()

    def validate(self) -> bool:
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


# === Enhanced Certificate Information Class ===
class CertificateInfo:
    def __init__(self, cert_context, subject_name, issuer_name, serial_number, valid_from, valid_to, cert=None):
        self.cert_context = cert_context
        self.subject_name = subject_name
        self.issuer_name = issuer_name
        self.serial_number = serial_number
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.cert_bytes = cert_context.CertEncoded if hasattr(cert_context, 'CertEncoded') else cert_context
        self.cert = cert
        
    def __str__(self):
        return f"{self.subject_name} (Serial: {self.serial_number})"


# === Enhanced Certificate Validation Functions ===
def load_trusted_root_certificates(root_folder):
    """Load trusted root certificates from PEM files in the specified folder and subfolders"""
    trusted_roots = []
    if not os.path.exists(root_folder):
        print(f"[WARNING] Root certificates folder '{root_folder}' not found")
        return trusted_roots

    # Search for .pem files recursively in all subfolders
    pem_files = glob.glob(os.path.join(root_folder, "**", "*.pem"), recursive=True)

    if not pem_files:
        # If no files in subfolders, check root folder directly
        pem_files = glob.glob(os.path.join(root_folder, "*.pem"))

    print(f"[+] Found {len(pem_files)} PEM file(s) to process...")

    for pem_file in pem_files:
        try:
            # Extract CA folder name for better identification
            rel_path = os.path.relpath(pem_file, root_folder)
            ca_folder = os.path.dirname(rel_path) if os.path.dirname(rel_path) else "Root"

            with open(pem_file, 'rb') as f:
                cert_data = f.read()

            # Handle multiple certificates in single PEM file
            cert_start = b'-----BEGIN CERTIFICATE-----'
            cert_end = b'-----END CERTIFICATE-----'

            start_indices = []
            end_indices = []

            pos = 0
            while True:
                start = cert_data.find(cert_start, pos)
                if start == -1:
                    break
                start_indices.append(start)
                pos = start + len(cert_start)

            pos = 0
            while True:
                end = cert_data.find(cert_end, pos)
                if end == -1:
                    break
                end_indices.append(end + len(cert_end))
                pos = end + len(cert_end)

            for start, end in zip(start_indices, end_indices):
                single_cert_data = cert_data[start:end]
                try:
                    cert = x509.load_pem_x509_certificate(single_cert_data, default_backend())
                    trusted_roots.append(cert)
                    cert_cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                    print(f"[+] Loaded trusted certificate: {cert_cn} (from {ca_folder}/)")
                except Exception as e:
                    print(f"[WARNING] Failed to load certificate from {pem_file}: {e}")

        except Exception as e:
            print(f"[WARNING] Failed to read {pem_file}: {e}")

    print(f"[+] Total loaded: {len(trusted_roots)} trusted certificates from all CA folders")
    return trusted_roots


def get_certificate_thumbprint(cert):
    """Get certificate thumbprint (SHA1 hash)"""
    cert_der = cert.public_bytes(serialization.Encoding.DER)
    thumbprint = hashlib.sha1(cert_der).hexdigest().upper()
    return thumbprint

def get_certificate_chain_from_store(cert):
    """Get certificate chain from system certificate store (cross-platform)"""
    chain_certs = []

    # For now, we'll use a simple approach that works cross-platform
    # We'll check the issuer chain by looking at the certificate's issuer
    print(f"[+] Performing cross-platform certificate chain validation...")

    try:
        current_cert = cert
        chain_certs.append({
            'thumbprint': get_certificate_thumbprint(current_cert),
            'subject': current_cert.subject.rfc4514_string()
        })

        # Simple chain building - we'll just add the current certificate
        # In a more complex implementation, we could try to find intermediate certificates
        print(f"[+] Built basic certificate chain with 1 certificate")

    except Exception as e:
        print(f"[+] Could not build certificate chain: {e}")

    return chain_certs

def get_authority_key_identifier(cert):
    """Get Authority Key Identifier from certificate"""
    try:
        aki_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
        if aki_ext.value.key_identifier:
            return aki_ext.value.key_identifier.hex().upper()
    except x509.ExtensionNotFound:
        pass
    return None

def get_subject_key_identifier(cert):
    """Get Subject Key Identifier from certificate"""
    try:
        ski_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.SUBJECT_KEY_IDENTIFIER)
        return ski_ext.value.digest.hex().upper()
    except x509.ExtensionNotFound:
        pass
    return None

def check_certificate_chain(cert, trusted_roots):
    """Check if certificate chain is valid against trusted roots using secure methods"""
    if not trusted_roots:
        print(f"[!] ERROR: No trusted root certificates loaded from root_certificates folder")
        return False

    print(f"[+] Verifying certificate against {len(trusted_roots)} trusted root certificates...")

    # Get certificate identifiers
    cert_thumbprint = get_certificate_thumbprint(cert)
    cert_aki = get_authority_key_identifier(cert)

    print(f"[+] User certificate thumbprint: {cert_thumbprint}")
    if cert_aki:
        print(f"[+] User certificate Authority Key Identifier: {cert_aki}")
    else:
        print(f"[+] User certificate has no Authority Key Identifier")

    # Build trusted root database with all identifiers
    trusted_data = {}
    for root_cert in trusted_roots:
        root_thumbprint = get_certificate_thumbprint(root_cert)
        root_ski = get_subject_key_identifier(root_cert)
        root_cn = root_cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value

        trusted_data[root_thumbprint] = {
            'cert': root_cert,
            'cn': root_cn,
            'ski': root_ski,
            'thumbprint': root_thumbprint
        }

        print(f"[+] Trusted root: {root_cn}")
        print(f"    Thumbprint: {root_thumbprint}")
        if root_ski:
            print(f"    Subject Key Identifier: {root_ski}")

    # Method 1: Check if certificate is directly a trusted root (thumbprint match)
    if cert_thumbprint in trusted_data:
        print(f"[+] Certificate is directly a trusted root: {trusted_data[cert_thumbprint]['cn']}")
        return True

    # Method 2: Secure Authority/Subject Key Identifier matching
    if cert_aki:
        print(f"[+] Checking Authority Key Identifier matching...")
        for root_data in trusted_data.values():
            if root_data['ski'] and cert_aki == root_data['ski']:
                print(f"[+] Authority Key Identifier matches trusted root: {root_data['cn']}")
                print(f"    User cert AKI: {cert_aki}")
                print(f"    Root cert SKI: {root_data['ski']}")

                # Additional verification: Cryptographic signature check
                try:
                    root_public_key = root_data['cert'].public_key()
                    root_public_key.verify(
                        cert.signature,
                        cert.tbs_certificate_bytes,
                        padding.PKCS1v15(),
                        cert.signature_hash_algorithm
                    )
                    print(f"[+] Cryptographic verification successful against: {root_data['cn']}")
                    return True
                except Exception as e:
                    print(f"[!] Cryptographic verification failed: {e}")
                    continue

    # Method 3: Direct cryptographic verification (for certificates without AKI/SKI)
    print(f"[+] Attempting direct cryptographic verification...")
    for root_data in trusted_data.values():
        try:
            root_public_key = root_data['cert'].public_key()
            root_public_key.verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                padding.PKCS1v15(),
                cert.signature_hash_algorithm
            )
            print(f"[+] Certificate cryptographically verified against root: {root_data['cn']}")
            return True
        except Exception:
            continue

    # Method 4: Check for intermediate CA scenario
    cert_issuer = cert.issuer.rfc4514_string()
    print(f"[+] Certificate not directly issued by trusted root")
    print(f"[+] Certificate issuer: {cert_issuer}")
    print(f"[+] This appears to be an intermediate CA scenario")
    print(f"[!] For security, intermediate CA certificates must be added to root_certificates folder")

    print(f"[!] ERROR: Certificate chain validation failed - no cryptographic proof found")
    print(f"[!] Certificate thumbprint: {cert_thumbprint}")
    print(f"[!] Available trusted root thumbprints:")
    for root_data in trusted_data.values():
        print(f"[!]   - {root_data['cn']}: {root_data['thumbprint']}")

    return False


def check_certificate_validity(cert):
    """Check if certificate is currently valid (not expired)"""
    now = datetime.now(timezone.utc)
    try:
        not_before = cert.not_valid_before_utc
        not_after = cert.not_valid_after_utc
    except AttributeError:
        not_before = cert.not_valid_before.replace(tzinfo=timezone.utc)
        not_after = cert.not_valid_after.replace(tzinfo=timezone.utc)
    
    return not_before <= now <= not_after


def check_key_usage_for_signing(cert):
    """Check if certificate has Digital Signature and Non-Repudiation key usage"""
    try:
        key_usage_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.KEY_USAGE)
        key_usage = key_usage_ext.value
        
        # Check for Digital Signature and Non-Repudiation
        has_digital_signature = key_usage.digital_signature
        has_non_repudiation = key_usage.content_commitment  # content_commitment is the new name for non_repudiation
        
        return has_digital_signature and has_non_repudiation
    except x509.ExtensionNotFound:
        # If Key Usage extension is not present, assume signing is allowed
        return True
    except Exception as e:
        print(f"[WARNING] Error checking key usage: {e}")
        return True


def get_crl_distribution_points(cert):
    """Get CRL Distribution Points from certificate"""
    try:
        crl_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.CRL_DISTRIBUTION_POINTS)
        crl_urls = []
        for dp in crl_ext.value:
            if dp.full_name:
                for name in dp.full_name:
                    if isinstance(name, x509.UniformResourceIdentifier):
                        crl_urls.append(name.value)
        return crl_urls
    except x509.ExtensionNotFound:
        return []


def check_certificate_revocation_crl(cert):
    """Check certificate revocation status via CRL"""
    crl_urls = get_crl_distribution_points(cert)
    if not crl_urls:
        print("[WARNING] No CRL distribution points found in certificate")
        return True  # Assume not revoked if no CRL available
    
    for crl_url in crl_urls:
        try:
            print(f"[+] Checking CRL: {crl_url}")
            response = requests.get(crl_url, timeout=10)
            if response.status_code == 200:
                crl = x509.load_der_x509_crl(response.content, default_backend())
                
                # Check if certificate serial number is in revoked list
                for revoked_cert in crl:
                    if revoked_cert.serial_number == cert.serial_number:
                        print(f"[!] Certificate is revoked (found in CRL)")
                        return False
                
                print(f"[+] Certificate not found in CRL - not revoked")
                return True
        except Exception as e:
            print(f"[WARNING] Failed to check CRL {crl_url}: {e}")
            continue
    
    return True  # Assume not revoked if CRL check fails


def get_ocsp_responder_url(cert):
    """Get OCSP responder URL from certificate"""
    try:
        aia_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
        for access_description in aia_ext.value:
            if access_description.access_method == x509.AuthorityInformationAccessOID.OCSP:
                return access_description.access_location.value
    except x509.ExtensionNotFound:
        pass
    return None


def check_certificate_revocation_ocsp(cert, issuer_cert=None):
    """Check certificate revocation status via OCSP"""
    ocsp_url = get_ocsp_responder_url(cert)
    if not ocsp_url:
        print("[WARNING] No OCSP responder URL found in certificate")
        return True  # Assume not revoked if no OCSP available
    
    try:
        print(f"[+] Checking OCSP: {ocsp_url}")
        # Note: Full OCSP implementation requires more complex logic
        # This is a simplified check - you may need to implement full OCSP request/response handling
        print("[WARNING] OCSP checking not fully implemented - assuming certificate is valid")
        return True
    except Exception as e:
        print(f"[WARNING] OCSP check failed: {e}")
        return True


def matches_certificate_criteria(cert, cn=None, o=None, ou=None, e=None, sn=None, ca=None):
    """Check if certificate matches the specified criteria"""
    try:
        # Extract certificate details
        subject = cert.subject
        
        # Check CN (Common Name)
        if cn:
            try:
                cert_cn = subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                if cn.lower() not in cert_cn.lower():
                    return False
            except IndexError:
                return False  # No CN found
        
        # Check O (Organization)
        if o:
            try:
                cert_o = subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value
                if o.lower() not in cert_o.lower():
                    return False
            except IndexError:
                return False  # No Organization found
        
        # Check OU (Organizational Unit)
        if ou:
            try:
                cert_ou = subject.get_attributes_for_oid(x509.NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value
                if ou.lower() not in cert_ou.lower():
                    return False
            except IndexError:
                return False  # No OU found
        
        # Check Email from SAN
        if e:
            try:
                san_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                email_found = False
                for name in san_ext.value:
                    if isinstance(name, x509.RFC822Name):
                        if e.lower() == name.value.lower():
                            email_found = True
                            break
                if not email_found:
                    return False
            except x509.ExtensionNotFound:
                return False  # No SAN extension found
        
        # Check Serial Number (hex format)
        if sn:
            cert_sn_hex = format(cert.serial_number, 'x').upper()
            target_sn_hex = sn.replace(':', '').upper()
            if cert_sn_hex != target_sn_hex:
                return False
        
        # Check Certifying Authority (Issuer CN)
        if ca:
            try:
                issuer_cn = cert.issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                if ca.lower() not in issuer_cn.lower():
                    return False
            except IndexError:
                return False  # No Issuer CN found
        
        return True
        
    except Exception as e:
        print(f"[WARNING] Error checking certificate criteria: {e}")
        return False


def validate_certificate_for_signing(cert, trusted_roots):
    """Comprehensive certificate validation for signing"""
    print(f"[+] Validating certificate: {cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value}")

    # MANDATORY: Check certificate chain first - this is now required
    if not check_certificate_chain(cert, trusted_roots):
        print(f"[!] CRITICAL ERROR: Certificate chain validation failed - certificate is not issued by trusted root CA")
        print(f"[!] Signing operation cannot proceed without valid root certificate verification")
        return False

    # Check key usage for signing
    if not check_key_usage_for_signing(cert):
        print(f"[!] Certificate does not have required key usage for signing (Digital Signature + Non-Repudiation)")
        return False

    # Check validity period
    if check_validity == "yes" and not check_certificate_validity(cert):
        print(f"[!] Certificate is expired or not yet valid")
        return False

    # Check CRL revocation
    if check_revocation_crl == "yes" and not check_certificate_revocation_crl(cert):
        print(f"[!] Certificate is revoked (CRL check)")
        return False

    # Check OCSP revocation
    if check_revocation_ocsp == "yes" and not check_certificate_revocation_ocsp(cert):
        print(f"[!] Certificate is revoked (OCSP check)")
        return False

    print(f"[+] Certificate validation passed - all checks including root CA verification successful")
    return True


# === Enhanced Certificate Selection Dialog ===
def show_powershell_cert_dialog(valid_certificates):
    """Show certificate selection dialog with only valid signing certificates"""
    try:
        # Create certificate array for PowerShell
        cert_array_script = ""
        for i, cert_info in enumerate(valid_certificates):
            # Convert certificate bytes to base64 for PowerShell
            cert_b64 = base64.b64encode(cert_info.cert_bytes).decode('utf-8')
            cert_array_script += f'$cert{i} = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new([System.Convert]::FromBase64String("{cert_b64}"))\n'
            cert_array_script += f'$certCollection.Add($cert{i})\n'
        
        ps_script = f'''
try {{
    Add-Type -AssemblyName System.Security
    Add-Type -AssemblyName System.Windows.Forms

    $certCollection = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2Collection
    
    {cert_array_script}

    if ($certCollection.Count -eq 0) {{
        Write-Host "No valid signing certificates found"
        exit 1
    }}

    $selectedCert = [System.Security.Cryptography.X509Certificates.X509Certificate2UI]::SelectFromCollection(
        $certCollection,
        "{app_name}",
        "Please select a certificate to sign the XML (Only valid signing certificates are shown):",
        [System.Security.Cryptography.X509Certificates.X509SelectionFlag]::SingleSelection
    )

    if ($selectedCert.Count -gt 0) {{
        $cert = $selectedCert[0]
        
        $certInfo = @{{
            Subject = $cert.Subject
            Issuer = $cert.Issuer
            SerialNumber = $cert.SerialNumber
            Thumbprint = $cert.Thumbprint
            NotBefore = $cert.NotBefore.ToString("yyyy-MM-dd HH:mm:ss")
            NotAfter = $cert.NotAfter.ToString("yyyy-MM-dd HH:mm:ss")
        }}
        
        $json = $certInfo | ConvertTo-Json -Compress
        Write-Host "SELECTED_CERT:$json"
    }} else {{
        Write-Host "CANCELLED"
        exit 0
    }}
}} catch {{
    Write-Host "PowerShell Error: $($_.Exception.Message)"
    exit 1
}}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
            f.write(ps_script)
            script_path = f.name
        
        try:
            print("[+] Opening certificate selection dialog...")
            
            result = subprocess.run([
                'powershell.exe',
                '-ExecutionPolicy', 'Bypass',
                '-File', script_path
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                if 'SELECTED_CERT:' in result.stdout:
                    json_lines = [line for line in result.stdout.split('\n') if line.startswith('SELECTED_CERT:')]
                    if json_lines:
                        json_data = json_lines[0].replace('SELECTED_CERT:', '')
                        cert_data = json.loads(json_data)
                        print(f"[+] Certificate selected: {cert_data.get('Subject', 'Unknown')}")
                        return cert_data
                elif 'CANCELLED' in result.stdout:
                    print("[+] Certificate selection cancelled by user")
                    return None
            
            print(f"[!] Certificate selection failed")
            return None
                    
        finally:
            try:
                os.unlink(script_path)
            except:
                pass
                
    except Exception as e:
        print(f"[!] Certificate selection error: {e}")
        return None


# === Base Signer Interface ===
class BaseSigner:
    def get_certificate(self, target_cn: str = None):
        raise NotImplementedError
    
    def sign_data(self, data: bytes, signature_algorithm: SignatureAlgorithm):
        raise NotImplementedError
    
    def cleanup(self):
        pass


# === Enhanced Windows Certificate Store Signer ===
class WindowsCertStoreSigner(BaseSigner):
    def __init__(self, subject=None, certstore='MY', trusted_roots=None):
        self.subject = subject
        self.certstore = certstore
        self.cert_context = None
        self.cert = None
        self.cert_bytes = None
        self.trusted_roots = trusted_roots or []

    def get_all_certificates_from_store(self, certstore='MY'):
        certificates = []
        st = win32crypt.CertOpenSystemStore(certstore, None)
        
        try:
            certs = st.CertEnumCertificatesInStore()
            for cert_context in certs:
                try:
                    subject_name = win32crypt.CertNameToStr(cert_context.Subject)
                    issuer_name = win32crypt.CertNameToStr(cert_context.Issuer)
                    
                    cert_der = cert_context.CertEncoded
                    cert = x509.load_der_x509_certificate(cert_der, backend=default_backend())
                    
                    try:
                        valid_from = cert.not_valid_before_utc
                        valid_to = cert.not_valid_after_utc
                    except AttributeError:
                        valid_from = cert.not_valid_before
                        valid_to = cert.not_valid_after
                    
                    cert_info = CertificateInfo(
                        cert_context=cert_context,
                        subject_name=subject_name,
                        issuer_name=issuer_name,
                        serial_number=cert.serial_number,
                        valid_from=valid_from,
                        valid_to=valid_to,
                        cert=cert
                    )
                    
                    certificates.append(cert_info)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            pass
        finally:
            try:
                st.CertCloseStore()
            except:
                pass
        
        return certificates

    def filter_valid_signing_certificates(self, certificates):
        """Filter certificates that are valid for signing and match criteria"""
        valid_certs = []
        
        for cert_info in certificates:
            try:
                cert = cert_info.cert
                
                # Check if certificate matches the specified criteria
                if not matches_certificate_criteria(cert, target_cn, target_o, target_ou, target_e, target_sn, target_ca):
                    continue
                
                # Validate certificate for signing
                if validate_certificate_for_signing(cert, self.trusted_roots):
                    valid_certs.append(cert_info)
                    
            except Exception as e:
                print(f"[WARNING] Error validating certificate {cert_info.subject_name}: {e}")
                continue
        
        return valid_certs

    def find_matching_certificate(self, cert_data, certificates):
        if not cert_data or not certificates:
            return None
        
        # Strategy 1: Match by serial number
        for cert_info in certificates:
            if str(cert_info.serial_number) == cert_data['SerialNumber']:
                return cert_info
        
        # Strategy 2: Match by CN
        if 'CN=' in cert_data['Subject']:
            ps_cn = cert_data['Subject'].split('CN=')[1].split(',')[0].strip()
            for cert_info in certificates:
                if ps_cn in cert_info.subject_name:
                    return cert_info
        
        # Strategy 3: Match by Organization
        if ', O=' in cert_data['Subject']:
            ps_org = cert_data['Subject'].split(', O=')[1].split(',')[0].strip()
            for cert_info in certificates:
                if ps_org in cert_info.subject_name:
                    return cert_info
        
        return None

    def get_certificate(self, target_cn_param: str = None):
        all_certificates = self.get_all_certificates_from_store(self.certstore)
        
        if not all_certificates:
            raise Exception(f"No certificates found in {self.certstore} store")
        
        # Filter for valid signing certificates
        valid_certificates = self.filter_valid_signing_certificates(all_certificates)
        
        if not valid_certificates:
            raise Exception("No valid signing certificates found that match the criteria")
        
        if len(valid_certificates) == 1:
            selected_cert = valid_certificates[0]
            print(f"[+] Using certificate: {self._extract_cn(selected_cert.subject_name)}")
        else:
            selected_cert = self._show_selection_dialog(valid_certificates)
        
        if selected_cert is None:
            raise Exception("No certificate selected")
        
        self.cert_context = selected_cert.cert_context
        self.cert_bytes = selected_cert.cert_bytes
        self.cert = selected_cert.cert
        
        return "win_cert", self.cert_bytes, self.cert

    def _show_selection_dialog(self, certificates):
        print(f"[+] Found {len(certificates)} valid signing certificates")
        
        cert_data = show_powershell_cert_dialog(certificates)
        
        if cert_data is None:
            print("[+] Operation cancelled by user")
            sys.exit(0)
        
        selected_cert = self.find_matching_certificate(cert_data, certificates)
        
        if selected_cert is None:
            raise Exception("Could not match selected certificate")
        
        return selected_cert

    def _extract_cn(self, subject_name):
        try:
            if 'CN=' in subject_name:
                return subject_name.split('CN=')[1].split(',')[0].strip()
            else:
                parts = [p.strip() for p in subject_name.split(',')]
                for part in parts:
                    if len(part) > 5 and not part.isdigit() and not any(x in part.upper() for x in ['OID', 'STREET', 'DELHI', 'MUMBAI']):
                        return part
                return parts[-1] if parts else subject_name
        except:
            return subject_name

    def sign_data(self, data, signature_algorithm: SignatureAlgorithm = SignatureAlgorithm.RSA_SHA256):
        try:
            hash_algo = self._get_hash_algorithm_from_signature_algo(signature_algorithm)
            
            st = win32crypt.CertOpenSystemStore(self.certstore, None)
            cert_context = None
            
            try:
                certs = st.CertEnumCertificatesInStore()
                for cert in certs:
                    if cert.CertEncoded == self.cert_bytes:
                        cert_context = cert
                        break
                
                if cert_context is None:
                    raise Exception("Certificate not found for signing")
                
                keyspec, cryptprov = cert_context.CryptAcquireCertificatePrivateKey(
                    win32cryptcon.CRYPT_ACQUIRE_COMPARE_KEY_FLAG
                )
                
                chash = cryptprov.CryptCreateHash(hash_algo, None, 0)
                chash.CryptHashData(data, 0)
                signature = chash.CryptSignHash(keyspec, 0)
                
                return signature[::-1]
                
            finally:
                try:
                    st.CertCloseStore()
                except:
                    pass
            
        except Exception as e:
            print(f"Error signing data: {e}")
            return None

    def _get_hash_algorithm_from_signature_algo(self, signature_algorithm: SignatureAlgorithm):
        if signature_algorithm in [SignatureAlgorithm.RSA_SHA1, SignatureAlgorithm.DSA_SHA1, SignatureAlgorithm.ECDSA_SHA1]:
            return win32cryptcon.CALG_SHA1
        elif signature_algorithm in [SignatureAlgorithm.RSA_SHA256, SignatureAlgorithm.DSA_SHA256, SignatureAlgorithm.ECDSA_SHA256]:
            return win32cryptcon.CALG_SHA_256
        elif signature_algorithm in [SignatureAlgorithm.RSA_SHA384, SignatureAlgorithm.ECDSA_SHA384]:
            return win32cryptcon.CALG_SHA_384
        elif signature_algorithm in [SignatureAlgorithm.RSA_SHA512, SignatureAlgorithm.ECDSA_SHA512]:
            return win32cryptcon.CALG_SHA_512
        else:
            return win32cryptcon.CALG_SHA_256


# === Enhanced PFX Signer ===
class PFXSigner(BaseSigner):
    def __init__(self, pfx_file: str, pfx_password: str = None, trusted_roots=None):
        self.pfx_file = pfx_file
        self.pfx_password = pfx_password.encode() if pfx_password else None
        self.private_key = None
        self.cert = None
        self.trusted_roots = trusted_roots or []
        
    def get_certificate(self, target_cn_param: str = None):
        try:
            with open(self.pfx_file, "rb") as f:
                pfx_data = f.read()
            
            # Try multiple methods for compatibility
            try:
                from cryptography.hazmat.primitives.serialization import load_pkcs12
                p12 = load_pkcs12(pfx_data, self.pfx_password)
                private_key = p12.key
                cert = p12.cert.certificate if p12.cert else None
                additional_certs = p12.additional_certs
            except (ImportError, AttributeError):
                try:
                    private_key, cert, additional_certs = pkcs12.load_key_and_certificates(
                        pfx_data, 
                        self.pfx_password,
                        backend=default_backend()
                    )
                except AttributeError:
                    try:
                        from OpenSSL import crypto
                        p12 = crypto.load_pkcs12(pfx_data, self.pfx_password)
                        private_key = p12.get_privatekey()
                        cert = p12.get_certificate()
                        cert_bytes = crypto.dump_certificate(crypto.FILETYPE_ASN1, cert)
                        cert = x509.load_der_x509_certificate(cert_bytes, default_backend())
                        additional_certs = []
                    except ImportError:
                        raise ValueError("Could not load PFX file. Try upgrading cryptography package")
            
            if cert is None:
                raise ValueError("No certificate found in PFX file")
            
            # Check if certificate matches criteria
            if not matches_certificate_criteria(cert, target_cn, target_o, target_ou, target_e, target_sn, target_ca):
                raise ValueError("Certificate does not match the specified criteria")
            
            # Validate certificate for signing
            if not validate_certificate_for_signing(cert, self.trusted_roots):
                raise ValueError("Certificate is not valid for signing")
            
            cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
            print(f"[+] Found valid signing certificate with CN = {cn}")
            
            self.private_key = private_key
            self.cert = cert
            return "pfx_key", cert.public_bytes(serialization.Encoding.DER), cert
        
        except Exception as e:
            raise ValueError(f"Error loading PFX file: {e}")
    
    def sign_data(self, data: bytes, signature_algorithm: SignatureAlgorithm):
        if not self.private_key:
            raise ValueError("Private key not loaded")
        
        hash_algo_map = {
            SignatureAlgorithm.RSA_SHA1: hashes.SHA1(),
            SignatureAlgorithm.RSA_SHA256: hashes.SHA256(),
            SignatureAlgorithm.RSA_SHA384: hashes.SHA384(),
            SignatureAlgorithm.RSA_SHA512: hashes.SHA512(),
            SignatureAlgorithm.ECDSA_SHA1: hashes.SHA1(),
            SignatureAlgorithm.ECDSA_SHA256: hashes.SHA256(),
            SignatureAlgorithm.ECDSA_SHA384: hashes.SHA384(),
            SignatureAlgorithm.ECDSA_SHA512: hashes.SHA512(),
        }
        
        hash_algo = hash_algo_map.get(signature_algorithm)
        if not hash_algo:
            raise ValueError(f"Unsupported signature algorithm for PFX: {signature_algorithm}")
        
        try:
            if signature_algorithm.value.startswith("http://www.w3.org/2000/09/xmldsig#rsa") or \
               signature_algorithm.value.startswith("http://www.w3.org/2001/04/xmldsig-more#rsa"):
                if isinstance(self.private_key, rsa.RSAPrivateKey):
                    signature = self.private_key.sign(
                        data,
                        padding.PKCS1v15(),
                        hash_algo
                    )
                else:
                    signature = self._sign_with_openssl_key(data, hash_algo)
            else:
                if isinstance(self.private_key, ec.EllipticCurvePrivateKey):
                    signature = self.private_key.sign(
                        data,
                        ec.ECDSA(hash_algo)
                    )
                else:
                    signature = self._sign_with_openssl_key(data, hash_algo)
            
            return signature
        
        except Exception as e:
            raise ValueError(f"Error signing data with PFX: {e}")
    
    def _sign_with_openssl_key(self, data, hash_algo):
        try:
            if hasattr(self.private_key, 'sign'):
                return self.private_key.sign(data, padding.PKCS1v15(), hash_algo)
            else:
                raise ValueError("Unsupported private key type")
        except Exception as e:
            raise ValueError(f"OpenSSL key signing failed: {e}")


# === Enhanced HSM Token Signer ===
class HSMTokenSigner(BaseSigner):
    def __init__(self, dll_path: str = None, trusted_roots=None):
        if not HSM_AVAILABLE:
            raise ValueError("PyKCS11 not available - install with: pip install PyKCS11")
        
        self.dll_path = dll_path or self._find_hsm_dll()
        if not self.dll_path:
            raise ValueError("No HSM DLL found")
        
        self.pkcs11 = PK11.PyKCS11Lib()
        self.pkcs11.load(self.dll_path)
        self.session = None
        self.keyid = None
        self.token_info = None
        self.trusted_roots = trusted_roots or []

    def _find_hsm_dll(self):
        """Find first available HSM DLL (legacy method for single DLL usage)"""
        available_dlls = self._get_all_available_dlls()
        if available_dlls:
            return available_dlls[0]['dll_path']
        return None

    def _get_all_available_dlls(self):
        """Get all HSM DLLs with their connected tokens"""
        available_dlls = []

        for dll_path in hsm_dll_paths:
            if os.path.exists(dll_path):
                try:
                    # Test if this DLL has any connected tokens
                    test_pkcs11 = PK11.PyKCS11Lib()
                    test_pkcs11.load(dll_path)
                    slots = test_pkcs11.getSlotList(tokenPresent=True)

                    if slots:
                        print(f"[+] Found HSM DLL with connected tokens: {dll_path}")
                        print(f"[+] Found {len(slots)} token(s) connected")
                        available_dlls.append({
                            'dll_path': dll_path,
                            'slots': slots,
                            'pkcs11_lib': test_pkcs11
                        })
                    else:
                        print(f"[+] Found HSM DLL but no tokens connected: {dll_path}")

                except Exception as e:
                    print(f"[+] HSM DLL found but failed to load: {dll_path} - {e}")
                    continue

        if not available_dlls:
            print(f"[!] No HSM DLL found with connected tokens")

        return available_dlls

    def get_available_tokens(self):
        """Get list of available tokens from current DLL"""
        tokens = []
        slots = self.pkcs11.getSlotList(tokenPresent=True)
        for slot in slots:
            try:
                token = self.pkcs11.getTokenInfo(slot)
                actual_label = token.label.rstrip('\x00 ')
                tokens.append({
                    'slot': slot,
                    'label': actual_label,
                    'manufacturer': token.manufacturerID.rstrip('\x00 '),
                    'model': token.model.rstrip('\x00 '),
                    'serial': token.serialNumber.rstrip('\x00 '),
                    'dll_path': self.dll_path
                })
            except PK11.PyKCS11Error:
                continue
        return tokens

    @staticmethod
    def get_all_available_tokens():
        """Get tokens from all available HSM DLLs"""
        if not HSM_AVAILABLE:
            print("PyKCS11 not available - install with: pip install PyKCS11")
            return []

        all_tokens = []

        for dll_path in hsm_dll_paths:
            if os.path.exists(dll_path):
                try:
                    # Test if this DLL has any connected tokens
                    test_pkcs11 = PK11.PyKCS11Lib()
                    test_pkcs11.load(dll_path)
                    slots = test_pkcs11.getSlotList(tokenPresent=True)

                    if slots:
                        print(f"[+] Checking tokens in DLL: {dll_path}")
                        for slot in slots:
                            try:
                                token = test_pkcs11.getTokenInfo(slot)
                                actual_label = token.label.rstrip('\x00 ')
                                all_tokens.append({
                                    'slot': slot,
                                    'label': actual_label,
                                    'manufacturer': token.manufacturerID.rstrip('\x00 '),
                                    'model': token.model.rstrip('\x00 '),
                                    'serial': token.serialNumber.rstrip('\x00 '),
                                    'dll_path': dll_path
                                })
                            except PK11.PyKCS11Error:
                                continue
                    else:
                        print(f"[+] No tokens found in DLL: {dll_path}")

                except Exception as e:
                    print(f"[+] Failed to check DLL: {dll_path} - {e}")
                    continue

        return all_tokens

    def auto_login(self, pin: str):
        """Automatically login to the first available token"""
        tokens = self.get_available_tokens()
        
        if not tokens:
            raise ValueError("No HSM tokens found")
        
        if len(tokens) == 1:
            token = tokens[0]
            print(f"[+] Using token: {token['label']} (Model: {token['model']})")
        else:
            print("[+] Available tokens:")
            for i, token in enumerate(tokens, 1):
                print(f"  {i}. {token['label']} (Model: {token['model']}, Serial: {token['serial']})")
            
            choice = input("Select token (1-{}): ".format(len(tokens)))
            try:
                token = tokens[int(choice) - 1]
            except (ValueError, IndexError):
                token = tokens[0]  # Use first token as default
            
        try:
            self.session = self.pkcs11.openSession(token['slot'], PK11.CKF_SERIAL_SESSION | PK11.CKF_RW_SESSION)
            self.session.login(pin)
            self.token_info = token
            return True
        except PK11.PyKCS11Error as e:
            raise ValueError(f"Failed to login to token '{token['label']}': {e}")

    def logout(self):
        if self.session:
            try:
                self.session.logout()
                self.session.closeSession()
            except:
                pass

    def get_certificate(self, target_cn_param: str = None):
        if not self.session:
            raise ValueError("Not logged into HSM session")

        try:
            pk11objects = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_CERTIFICATE)]
            )
            all_attributes = [PK11.CKA_VALUE, PK11.CKA_ID]

            valid_certs = []

            for obj in pk11objects:
                try:
                    attrs = self.session.getAttributeValue(obj, all_attributes)
                    attr_dict = dict(zip(all_attributes, attrs))
                    cert_bytes = bytes(attr_dict[PK11.CKA_VALUE])
                    keyid = bytes(attr_dict[PK11.CKA_ID])

                    cert = x509.load_der_x509_certificate(cert_bytes, backend=default_backend())

                    # FIRST: Check if private key exists for this certificate
                    if not self._has_private_key(keyid):
                        cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                        print(f"[+] Skipping certificate (no private key): {cn}")
                        continue

                    # Check if certificate matches criteria
                    if not matches_certificate_criteria(cert, target_cn, target_o, target_ou, target_e, target_sn, target_ca):
                        continue

                    # Validate certificate for signing
                    if validate_certificate_for_signing(cert, self.trusted_roots):
                        valid_certs.append((keyid, cert_bytes, cert))

                except PK11.PyKCS11Error:
                    continue

            if not valid_certs:
                raise ValueError("No valid signing certificates found that match the criteria")

            if len(valid_certs) == 1:
                keyid, cert_bytes, cert = valid_certs[0]
                cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                print(f"[+] Found valid signing certificate with private key: {cn}")
                self.keyid = keyid
                return keyid, cert_bytes, cert
            else:
                # If multiple certificates, let user choose or use first one
                print(f"[+] Found {len(valid_certs)} valid signing certificates with private keys")
                for i, (keyid, cert_bytes, cert) in enumerate(valid_certs, 1):
                    cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                    print(f"  {i}. {cn}")

                # For now, use first certificate. You could implement selection logic here
                keyid, cert_bytes, cert = valid_certs[0]
                cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                print(f"[+] Using first certificate: {cn}")
                self.keyid = keyid
                return keyid, cert_bytes, cert

        except Exception as e:
            raise ValueError(f"Error finding certificate: {e}")

    def _has_private_key(self, keyid):
        """Check if private key exists for given key ID"""
        try:
            private_keys = self.session.findObjects([
                (PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY),
                (PK11.CKA_ID, keyid)
            ])
            return len(private_keys) > 0
        except PK11.PyKCS11Error:
            return False

    def sign_data(self, data: bytes, signature_algorithm: SignatureAlgorithm):
        if not self.session or not self.keyid:
            raise ValueError("HSM not properly initialized")

        try:
            privKey = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY), (PK11.CKA_ID, self.keyid)]
            )[0]

            mechanism = self._get_pkcs11_mechanism(signature_algorithm)
            signature = self.session.sign(privKey, data, mechanism)
            return bytes(signature)
        except Exception as e:
            raise ValueError(f"Error signing data with HSM: {e}")

    def _get_pkcs11_mechanism(self, signature_algorithm: SignatureAlgorithm):
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

    def cleanup(self):
        self.logout()


# === XML Signing Functions ===
def apply_enveloped_transform(element):
    elem_copy = etree.fromstring(etree.tostring(element))
    signature_elements = elem_copy.xpath('//ds:Signature',
                                       namespaces={'ds': 'http://www.w3.org/2000/09/xmldsig#'})
    for sig in signature_elements:
        sig.getparent().remove(sig)
    return elem_copy

def get_hash_algorithm(digest_algorithm: DigestAlgorithm):
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

def sign_xml_document(xml_content, cert, key_handle, signer: BaseSigner, envelope_params: SignatureEnvelopeParameters = None):
    if envelope_params is None:
        envelope_params = SignatureEnvelopeParameters(
            signature_info=SignatureInfo(),
            reference_info=ReferenceInfo(),
            key_info=KeyInfo()
        )

    envelope_params.validate()
    doc = etree.fromstring(xml_content)

    ns_map = {envelope_params.namespace_prefix: "http://www.w3.org/2000/09/xmldsig#"} if envelope_params.namespace_prefix else {None: "http://www.w3.org/2000/09/xmldsig#"}

    temp_signature = etree.Element("Signature", nsmap=ns_map)
    if envelope_params.signature_info.signature_id:
        temp_signature.set("Id", envelope_params.signature_info.signature_id)
    doc.append(temp_signature)

    transformed_doc = apply_enveloped_transform(doc)
    c14n_xml = etree.tostring(transformed_doc, method='c14n', exclusive=False)

    hash_algo = get_hash_algorithm(envelope_params.reference_info.digest_algorithm)
    digest = hash_algo(c14n_xml).digest()
    digest_b64 = base64.b64encode(digest).decode('utf-8')

    doc.remove(temp_signature)

    signed_info = etree.Element("SignedInfo", nsmap=ns_map)

    canon_method = etree.SubElement(signed_info, "CanonicalizationMethod")
    canon_method.set("Algorithm", envelope_params.signature_info.canonicalization_algorithm.value)

    sig_method = etree.SubElement(signed_info, "SignatureMethod")
    sig_method.set("Algorithm", envelope_params.signature_info.signature_algorithm.value)

    reference = etree.SubElement(signed_info, "Reference")
    reference.set("URI", envelope_params.reference_info.uri)
    if envelope_params.reference_info.reference_id:
        reference.set("Id", envelope_params.reference_info.reference_id)

    transforms = etree.SubElement(reference, "Transforms")
    for transform_algo in envelope_params.reference_info.transforms:
        transform = etree.SubElement(transforms, "Transform")
        transform.set("Algorithm", transform_algo.value)

    digest_method = etree.SubElement(reference, "DigestMethod")
    digest_method.set("Algorithm", envelope_params.reference_info.digest_algorithm.value)

    digest_value = etree.SubElement(reference, "DigestValue")
    digest_value.text = digest_b64

    signed_info_c14n = etree.tostring(signed_info, method='c14n', exclusive=False)

    signature_bytes = signer.sign_data(signed_info_c14n, envelope_params.signature_info.signature_algorithm)
    if signature_bytes is None:
        raise Exception("Failed to sign data")

    signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')

    signature_elem = etree.Element("Signature", nsmap=ns_map)
    if envelope_params.signature_info.signature_id:
        signature_elem.set("Id", envelope_params.signature_info.signature_id)
    signature_elem.append(signed_info)

    sig_value = etree.SubElement(signature_elem, "SignatureValue")
    sig_value.text = signature_b64

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
                    pass

            if envelope_params.key_info.include_certificate:
                x509_cert_elem = etree.SubElement(x509_data, "X509Certificate")
                cert_der = cert.public_bytes(serialization.Encoding.DER)
                cert_b64 = base64.b64encode(cert_der).decode('utf-8')
                x509_cert_elem.text = cert_b64

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

    doc.append(signature_elem)
    return doc

def list_certificates(certstore='MY'):
    print(f"\n[+] Listing certificates in '{certstore}' store:")
    print("-" * 60)
    
    # Load trusted roots
    trusted_roots = load_trusted_root_certificates(root_certificates_folder)
    
    signer = WindowsCertStoreSigner(trusted_roots=trusted_roots)
    certificates = signer.get_all_certificates_from_store(certstore)
    
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

def main():
    # Declare global variables at the start
    global target_cn, target_o, target_ou, target_e, target_sn, target_ca
    global check_validity, check_revocation_crl, check_revocation_ocsp, root_certificates_folder
    
    parser = argparse.ArgumentParser(
        description='Enhanced PKI XML Signer with Certificate Validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic signing with Windows Store
  python script.py --file document.xml

  # Sign with specific organization
  python script.py --o "Capricorn" --file document.xml

  # Use HSM with custom DLL and specific criteria
  python script.py --use-hsm --hsm-dll "C:\\custom\\hsm.dll" --cn "John Doe" --ca "My CA"

  # Use PFX with validation checks
  python script.py --use-pfx mycert.pfx --check-validity yes --check-crl yes

  # List valid signing certificates
  python script.py --list-certs

  # Sign with multiple criteria matching
  python script.py --o "Company" --email "user@company.com" --serial "1A2B3C4D"
        '''
    )
    
    # === File Options ===
    file_group = parser.add_argument_group('File Options')
    file_group.add_argument('--file', '-f', default=xml_file_to_sign,
                           help=f'XML file to sign (default: {xml_file_to_sign})')
    file_group.add_argument('--output', '-o',
                           help='Output file name (default: <input_file>_signed.xml)')
    
    # === Certificate Matching Criteria ===
    criteria_group = parser.add_argument_group('Certificate Matching Criteria', 
                                              'Specify one or more criteria to filter certificates')
    criteria_group.add_argument('--cn', 
                               help='Certificate Common Name to match (partial match)')
    criteria_group.add_argument('--o', 
                               help='Organization name to match (partial match)')
    criteria_group.add_argument('--ou', 
                               help='Organizational Unit to match (partial match)')
    criteria_group.add_argument('--email', 
                               help='Email from SAN RFC822Name to match (exact match, e.g., user@domain.com)')
    criteria_group.add_argument('--serial', 
                               help='Certificate serial number in hex format (exact match, e.g., 1A2B3C4D)')
    criteria_group.add_argument('--ca', 
                               help='Certifying Authority (Issuer CN) to match (partial match)')
    
    # === Certificate Method Selection ===
    method_group = parser.add_argument_group('Certificate Source Methods')
    cert_group = method_group.add_mutually_exclusive_group()
    cert_group.add_argument('--use-store', action='store_true', default=True,
                           help='Use Windows Certificate Store (default)')
    cert_group.add_argument('--use-hsm', action='store_true',
                           help='Use HSM token for signing')
    cert_group.add_argument('--use-pfx', metavar='PFX_FILE',
                           help='Use PFX file for signing')
    
    # === Method-Specific Options ===
    store_group = parser.add_argument_group('Windows Certificate Store Options')
    store_group.add_argument('--store', default=cert_store,
                            help=f'Certificate store name (default: {cert_store})')
    
    hsm_group = parser.add_argument_group('HSM Token Options')
    hsm_group.add_argument('--hsm-dll', 
                          help='HSM DLL path (auto-detected if not specified)')
    hsm_group.add_argument('--token-pin', 
                          help='HSM token PIN (will prompt if not provided)')
    
    pfx_group = parser.add_argument_group('PFX File Options')
    pfx_group.add_argument('--pfx-password', 
                          help='PFX file password (will prompt if not provided)')
    
    # === Certificate Validation Options ===
    validation_group = parser.add_argument_group('Certificate Validation Options')
    validation_group.add_argument('--root-certs-folder', default=root_certificates_folder,
                                 help=f'Folder containing trusted root certificates (.pem files) (default: {root_certificates_folder})')
    validation_group.add_argument('--check-validity', choices=['yes', 'no'], default=check_validity,
                                 help='Check if certificate is valid (not expired) (default: yes)')
    validation_group.add_argument('--check-crl', choices=['yes', 'no'], default=check_revocation_crl,
                                 help='Check certificate revocation via CRL (default: no)')
    validation_group.add_argument('--check-ocsp', choices=['yes', 'no'], default=check_revocation_ocsp,
                                 help='Check certificate revocation via OCSP (default: no)')
    
    # === Information Commands ===
    info_group = parser.add_argument_group('Information Commands')
    info_group.add_argument('--list-certs', action='store_true',
                           help='List all valid signing certificates in Windows store')
    info_group.add_argument('--list-tokens', action='store_true',
                           help='List available HSM tokens')
    
    # === Signature Algorithm Options ===
    sig_group = parser.add_argument_group('Signature Algorithm Options')
    sig_group.add_argument('--sig-algo', choices=['rsa-sha1', 'rsa-sha256', 'rsa-sha384', 'rsa-sha512',
                                                  'ecdsa-sha1', 'ecdsa-sha256', 'ecdsa-sha384', 'ecdsa-sha512'],
                          default='rsa-sha256', help='Signature algorithm (default: rsa-sha256)')
    sig_group.add_argument('--digest-algo', choices=['sha1', 'sha256', 'sha384', 'sha512'], default='sha256',
                          help='Digest algorithm (default: sha256)')
    
    # === XML Signature Options ===
    xml_group = parser.add_argument_group('XML Signature Options')
    xml_group.add_argument('--sig-id', help='Optional signature ID')
    xml_group.add_argument('--ref-id', help='Optional reference ID')
    
    # === KeyInfo Options ===
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

    # Update global variables with command line arguments
    target_cn = args.cn or ""
    target_o = args.o or ""
    target_ou = args.ou or ""
    target_e = args.email or ""
    target_sn = args.serial or ""
    target_ca = args.ca or ""
    check_validity = args.check_validity
    check_revocation_crl = args.check_crl
    check_revocation_ocsp = args.check_ocsp
    root_certificates_folder = args.root_certs_folder

    # List certificates if requested
    if args.list_certs:
        list_certificates(args.store)
        return

    # List HSM tokens if requested
    if args.list_tokens:
        if not HSM_AVAILABLE:
            print("PyKCS11 not available - install with: pip install PyKCS11")
            return
        try:
            # Get tokens from all available DLLs
            all_tokens = HSMTokenSigner.get_all_available_tokens()
            if all_tokens:
                print(f"\n[+] Found {len(all_tokens)} HSM token(s) across all DLLs:")
                print("-" * 80)
                for i, token in enumerate(all_tokens, 1):
                    print(f"{i}. Label: {token['label']}")
                    print(f"   Manufacturer: {token['manufacturer']}")
                    print(f"   Model: {token['model']}")
                    print(f"   Serial: {token['serial']}")
                    print(f"   DLL: {token['dll_path']}")
                    print()
            else:
                print("No HSM tokens found in any DLL")
        except Exception as e:
            print(f"Error listing tokens: {e}")
        return

    # Determine signing method
    if args.use_pfx:
        args.use_store = False
        args.use_hsm = False
    elif args.use_hsm:
        args.use_store = False

    input_file = args.file
    if not os.path.exists(input_file):
        sys.exit(f"Error: File '{input_file}' not found!")

    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_signed.xml"

    # Load trusted root certificates - MANDATORY step
    print(f"[+] Loading trusted root certificates from: {root_certificates_folder}")
    trusted_roots = load_trusted_root_certificates(root_certificates_folder)

    # Verify that root certificates are loaded
    if not trusted_roots:
        print(f"[!] CRITICAL ERROR: No trusted root certificates found in '{root_certificates_folder}' folder")
        print(f"[!] Please ensure the folder exists and contains .pem files with root certificates")
        print(f"[!] Signing operation cannot proceed without trusted root certificates")
        sys.exit(1)

    # Display certificate matching criteria
    criteria = []
    if target_cn:
        criteria.append(f"CN='{target_cn}'")
    if target_o:
        criteria.append(f"O='{target_o}'")
    if target_ou:
        criteria.append(f"OU='{target_ou}'")
    if target_e:
        criteria.append(f"Email='{target_e}'")
    if target_sn:
        criteria.append(f"Serial='{target_sn}'")
    if target_ca:
        criteria.append(f"CA='{target_ca}'")
    
    if criteria:
        print(f"[+] Certificate matching criteria: {', '.join(criteria)}")
    else:
        print("[+] No specific certificate criteria specified - will show all valid signing certificates")
    
    # Display validation settings
    validation_settings = []
    if check_validity == "yes":
        validation_settings.append("Validity check")
    if check_revocation_crl == "yes":
        validation_settings.append("CRL revocation check")
    if check_revocation_ocsp == "yes":
        validation_settings.append("OCSP revocation check")
    
    if validation_settings:
        print(f"[+] Validation checks enabled: {', '.join(validation_settings)}")

    # Configure signature parameters
    try:
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

        signature_info = SignatureInfo(
            signature_id=args.sig_id if args.sig_id else signature_id,
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

    except ValueError as e:
        sys.exit(f"Parameter validation error: {e}")

    # Initialize signer based on method
    signer = None
    try:
        if args.use_store:
            print("[+] Using Windows Certificate Store")
            signer = WindowsCertStoreSigner(
                subject=target_cn if target_cn else None,
                certstore=args.store,
                trusted_roots=trusted_roots
            )
            key_handle, cert_bytes, cert = signer.get_certificate(target_cn)
            
        elif args.use_hsm:
            print("[+] Using HSM token")
            if not args.token_pin:
                import getpass
                args.token_pin = getpass.getpass("Enter HSM token PIN: ")
            
            signer = HSMTokenSigner(args.hsm_dll, trusted_roots=trusted_roots)
            if not signer.auto_login(args.token_pin):
                sys.exit("Failed to login to HSM token")
            
            key_handle, cert_bytes, cert = signer.get_certificate(target_cn)
            
        elif args.use_pfx:
            print(f"[+] Using PFX file: {args.use_pfx}")
            if not args.pfx_password:
                import getpass
                args.pfx_password = getpass.getpass("Enter PFX password: ")
            
            signer = PFXSigner(args.use_pfx, args.pfx_password, trusted_roots=trusted_roots)
            key_handle, cert_bytes, cert = signer.get_certificate(target_cn)

        print(f"[+] Successfully loaded certificate")
        print(f"[+] Certificate Subject: {cert.subject.rfc4514_string()}")
        print(f"[+] Certificate Issuer: {cert.issuer.rfc4514_string()}")
        print(f"[+] Certificate Serial: {cert.serial_number}")
        
        # Display certificate validity
        try:
            not_before = cert.not_valid_before_utc
            not_after = cert.not_valid_after_utc
        except AttributeError:
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after
        print(f"[+] Certificate Valid: {not_before} to {not_after}")

        # Read and sign XML
        print(f"[+] Reading XML file: {input_file}")
        with open(input_file, "rb") as f:
            xml_content = f.read()

        print("[+] Adding XML signature...")
        signed_doc = sign_xml_document(xml_content, cert, key_handle, signer, envelope_params)

        print(f"[+] Writing signed XML to: {output_file}")
        signed_xml = etree.tostring(signed_doc, encoding="UTF-8", xml_declaration=False, pretty_print=False)
        with open(output_file, "wb") as f:
            f.write(signed_xml)

        print(f"[+] XML successfully signed! Output: {output_file}")

    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)
    finally:
        if signer:
            signer.cleanup()


if __name__ == "__main__":
    main()

