import binascii
import os
import sys
from pathlib import Path
from unittest import mock

import cryptography.hazmat.primitives.ciphers as crypto
import pytest

from lowatt_enedis.__main__ import run


def test_decrypt(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    key = binascii.hexlify(os.urandom(16))
    iv = binascii.hexlify(os.urandom(16))
    cipher = crypto.Cipher(
        crypto.algorithms.AES128(binascii.unhexlify(key)),
        crypto.modes.CBC(binascii.unhexlify(iv)),
    )
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(b"some xml secrets") + encryptor.finalize()
    with (tmp_path / "encrypted").open("wb") as f:
        f.write(encrypted)

    with mock.patch.object(
        sys,
        "argv",
        [
            "lowatt-enedis",
            "decrypt",
            "--key",
            key.decode("ascii"),
            "--iv",
            iv.decode("ascii"),
            "--output",
            str(tmp_path / "decrypted"),
            str(tmp_path / "encrypted"),
        ],
    ), pytest.raises(SystemExit) as cm:
        run()
    assert cm.value.code == 0
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == ""
    with (tmp_path / "decrypted").open("rb") as f:
        assert f.read() == b"some xml secrets"
