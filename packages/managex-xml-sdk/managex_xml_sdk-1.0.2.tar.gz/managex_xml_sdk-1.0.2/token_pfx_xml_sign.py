#!/usr/bin/env vpython3
# *-* coding: utf-8 *-*
from lxml import etree
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from endesive import xades, signer, hsm

import os
import sys
import sysconfig

# === Token config ===
dllpath = r"C:\Windows\System32\Watchdata\PROXKey CSP India V3.0\wdpkcs.dll"
token_label = "Aniket"
token_pin = "123456789"
target_cn = "Aniket Chaturvedi"  # Certificate CN to use for signing

import PyKCS11 as PK11


class Signer(hsm.HSM):
    def certificate(self):
        self.login(token_label, token_pin)
        keyid = bytes((0x66, 0x66, 0x90))
        try:
            pk11objects = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_CERTIFICATE)]
            )
            all_attributes = [
                # PK11.CKA_SUBJECT,
                PK11.CKA_VALUE,
                # PK11.CKA_ISSUER,
                # PK11.CKA_CERTIFICATE_CATEGORY,
                # PK11.CKA_END_DATE,
                PK11.CKA_ID,
            ]

            for obj in pk11objects:
                try:
                    attrs = self.session.getAttributeValue(obj, all_attributes)
                    attr_dict = dict(zip(all_attributes, attrs))
                    cert_bytes = bytes(attr_dict[PK11.CKA_VALUE])
                    keyid = bytes(attr_dict[PK11.CKA_ID])

                    # Load cert to check CN
                    cert = x509.load_der_x509_certificate(cert_bytes, backend=default_backend())
                    cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
                    if cn == target_cn:
                        print(f"[+] Found certificate with CN = {cn}")
                        return keyid, cert_bytes
                except PK11.PyKCS11Error:
                    continue
        finally:
            self.logout()

        print(f"[-] No certificate found with CN = {target_cn}")
        return None, None

    def sign(self, keyid, data, mech):
        self.login(token_label, token_pin)
        try:
            privKey = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY), (PK11.CKA_ID, keyid)]
            )[0]
            mech = getattr(PK11, "CKM_%s_RSA_PKCS" % mech.upper())
            sig = self.session.sign(privKey, data, PK11.Mechanism(mech, None))
            return bytes(sig)
        finally:
            self.logout()


def main():
    clshsm = Signer(dllpath)
    keyid, cert = clshsm.certificate()

    def signproc(tosign, algosig):
        return clshsm.sign(keyid, tosign, algosig)

    data = open("xml.xml", "rb").read()
    cert = x509.load_der_x509_certificate(cert, backend=default_backend())
    certcontent = cert.public_bytes(serialization.Encoding.DER)

    cls = xades.BES()
    doc = cls.enveloping(
        "dokument.xml",
        data,
        "application/xml",
        cert,
        certcontent,
        signproc,
        False,
        True,
    )
    data = etree.tostring(doc, encoding="UTF-8", xml_declaration=True, standalone=False)

    open("xml-hsm-softhsm2-enveloping.xml", "wb").write(data)


if __name__ == "__main__":
    main()