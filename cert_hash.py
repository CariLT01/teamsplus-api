from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization

with open("server.crt", "rb") as f:
    cert = x509.load_pem_x509_certificate(f.read())

public_key = cert.public_key()
spki = public_key.public_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

digest = hashes.Hash(hashes.SHA256())
digest.update(spki)
fingerprint = digest.finalize()
print(fingerprint.hex())  # <- This goes into CERT_KEY