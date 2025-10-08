"""
Certificate Manager - Core certificate handling functionality
"""

import os
import glob
import hashlib
from typing import List, Optional
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from ..models.certificate_models import CertificateInfo, ValidationConfig
from ..exceptions import TrustedRootsNotFoundError

class CertificateManager:
    """
    Manages certificate operations including loading, validation, and filtering
    """

    def __init__(self, trusted_roots_folder: str = "root_certificates"):
        """
        Initialize certificate manager

        Args:
            trusted_roots_folder: Path to trusted root certificates folder
        """
        self.trusted_roots_folder = trusted_roots_folder
        self._trusted_roots = None

    def load_trusted_root_certificates(self) -> List[x509.Certificate]:
        """
        Load trusted root certificates from PEM files in the specified folder and subfolders

        Returns:
            List of loaded certificates

        Raises:
            TrustedRootsNotFoundError: If no trusted roots found
        """
        trusted_roots = []

        if not os.path.exists(self.trusted_roots_folder):
            raise TrustedRootsNotFoundError(f"Root certificates folder '{self.trusted_roots_folder}' not found")

        # Search for .pem files recursively in all subfolders
        pem_files = glob.glob(os.path.join(self.trusted_roots_folder, "**", "*.pem"), recursive=True)

        if not pem_files:
            # If no files in subfolders, check root folder directly
            pem_files = glob.glob(os.path.join(self.trusted_roots_folder, "*.pem"))

        if not pem_files:
            raise TrustedRootsNotFoundError(f"No PEM files found in '{self.trusted_roots_folder}'")

        print(f"[+] Found {len(pem_files)} PEM file(s) to process...")

        for pem_file in pem_files:
            try:
                # Extract CA folder name for better identification
                rel_path = os.path.relpath(pem_file, self.trusted_roots_folder)
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

        if not trusted_roots:
            raise TrustedRootsNotFoundError(f"No valid certificates loaded from '{self.trusted_roots_folder}'")

        print(f"[+] Total loaded: {len(trusted_roots)} trusted certificates from all CA folders")
        self._trusted_roots = trusted_roots
        return trusted_roots

    def get_trusted_roots(self) -> List[x509.Certificate]:
        """
        Get cached trusted root certificates, load if not already loaded

        Returns:
            List of trusted root certificates
        """
        if self._trusted_roots is None:
            self._trusted_roots = self.load_trusted_root_certificates()
        return self._trusted_roots

    @staticmethod
    def get_certificate_thumbprint(cert: x509.Certificate) -> str:
        """
        Get certificate thumbprint (SHA1 hash)

        Args:
            cert: X.509 certificate

        Returns:
            Thumbprint as uppercase hex string
        """
        cert_der = cert.public_bytes(serialization.Encoding.DER)
        thumbprint = hashlib.sha1(cert_der).hexdigest().upper()
        return thumbprint

    @staticmethod
    def get_authority_key_identifier(cert: x509.Certificate) -> Optional[str]:
        """
        Get Authority Key Identifier from certificate

        Args:
            cert: X.509 certificate

        Returns:
            AKI as uppercase hex string or None
        """
        try:
            aki_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
            if aki_ext.value.key_identifier:
                return aki_ext.value.key_identifier.hex().upper()
        except x509.ExtensionNotFound:
            pass
        return None

    @staticmethod
    def get_subject_key_identifier(cert: x509.Certificate) -> Optional[str]:
        """
        Get Subject Key Identifier from certificate

        Args:
            cert: X.509 certificate

        Returns:
            SKI as uppercase hex string or None
        """
        try:
            ski_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.SUBJECT_KEY_IDENTIFIER)
            return ski_ext.value.digest.hex().upper()
        except x509.ExtensionNotFound:
            pass
        return None