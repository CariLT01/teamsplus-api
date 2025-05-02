from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

def generate_self_signed_cert(cert_file: str, key_file: str) -> None:
    # 1) Generate RSA key
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    
    # 2) Build subject/issuer name
    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"my.server.local"),
    ])
    
    # 3) Build certificate
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)                   # self-signed
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"my.server.local")]),
            critical=False
        )
        .sign(key, hashes.SHA256())
    )
    
    # 4) Write key and cert to files
    with open(key_file, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

# Usage
generate_self_signed_cert("server.crt", "server.key")