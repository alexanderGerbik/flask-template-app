from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_rsa_key_pair(key_size=2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=key_size, backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def load_pem_public_key(public_key_filename):
    data = open(public_key_filename, "rb").read()
    return serialization.load_pem_public_key(data, backend=default_backend())


def cast_public_key_to_str(public_key):
    key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return key_bytes.decode("utf-8")
