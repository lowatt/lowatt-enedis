import binascii
from typing import IO


def decrypt_aes_128_cbc(key: str, iv: str, fd: IO[bytes]) -> bytes:
    """Decrypt AES 128 CBC enedis encrypted file.

    Should be equivalent to:
    openssl enc -d -aes-128-cbc -K <hex key> -iv <hex iv> -in ERDF_<..>.zip -out output.zip
    """
    import cryptography.hazmat.primitives.ciphers as crypto

    cipher = crypto.Cipher(
        crypto.algorithms.AES128(binascii.unhexlify(key)),
        crypto.modes.CBC(binascii.unhexlify(iv)),
    )
    decryptor = cipher.decryptor()
    return decryptor.update(fd.read()) + decryptor.finalize()
