from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from service.utils import crypto

public_key_example = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyfj3fAwU7Ddz8DOQm0gH
Nbd+kheV4CR+guI9Ut7lTW7LfnmrUMUNduc6ffRV1XmgLgfEO0d2lC6ehHskr/B7
XRV3O8/gR1Nj2wr6fxZC/KSE0gdTt01Cx3hdcTSD3nV/z63oIWDSAtvhhHNP4ACk
u83fo9Km3OvPVtVj1LtYV6azWMbj9N5gN+B7wmd18LyRaOX6GM66WEhDxSWTrEnT
LspvuocQvgZX8h7p+yRwQap/bR/xjrN2NcYPB1s8nMFgUeqNh2AO3QI4QmEFSlf4
Prckt4zeH2fNcpuL3iyiYarmvshNIhfodLEBs0W+AMOuuYkXSPfO3x1seoqmM+Gw
kwIDAQAB
-----END PUBLIC KEY-----
"""


def test_load_pem_public_key(tmp_path):
    public_key_file = tmp_path / "public.pem"
    public_key_file.write_text(public_key_example)

    public_key = crypto.load_pem_public_key(public_key_file)

    assert isinstance(public_key, RSAPublicKey)
