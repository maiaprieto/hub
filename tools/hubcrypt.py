#!/usr/bin/env python3
"""Cifra y descifra los datos de la app Hub.

Formato de data.enc.json (compatible con WebCrypto en el navegador):
  {"v":1, "kdf":"PBKDF2-SHA256", "iter":600000,
   "salt":"<base64 16 bytes>", "iv":"<base64 12 bytes>",
   "ct":"<base64 ciphertext+tag AES-256-GCM>"}

La clave NUNCA va en el repositorio: se lee de la variable de entorno HUB_KEY.

Uso:
  HUB_KEY='...' python3 tools/hubcrypt.py decrypt data.enc.json > data.json
  HUB_KEY='...' python3 tools/hubcrypt.py encrypt data.json data.enc.json
  HUB_KEY='...' python3 tools/hubcrypt.py check data.enc.json

Al cifrar se reutiliza la sal del data.enc.json existente (así la app del
móvil puede seguir usando la clave que ya tiene guardada) y el IV es siempre
nuevo.
"""
import base64
import json
import os
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITER = 600_000


def _key(passphrase: str, salt: bytes, iterations: int) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations)
    return kdf.derive(passphrase.encode("utf-8"))


def _passphrase() -> str:
    # Igual que la app: sin espacios alrededor y en minúsculas
    p = os.environ.get("HUB_KEY", "").strip().lower()
    if not p:
        sys.exit("Falta la variable de entorno HUB_KEY")
    return p


def decrypt(path: str) -> dict:
    env = json.load(open(path, encoding="utf-8"))
    salt = base64.b64decode(env["salt"])
    iv = base64.b64decode(env["iv"])
    ct = base64.b64decode(env["ct"])
    key = _key(_passphrase(), salt, int(env.get("iter", ITER)))
    plain = AESGCM(key).decrypt(iv, ct, None)
    return json.loads(plain.decode("utf-8"))


def encrypt(data: dict, out_path: str) -> None:
    salt, iterations = None, ITER
    if os.path.exists(out_path):
        try:
            old = json.load(open(out_path, encoding="utf-8"))
            salt = base64.b64decode(old["salt"])
            iterations = int(old.get("iter", ITER))
        except Exception:
            salt = None
    if salt is None:
        salt = os.urandom(16)
    iv = os.urandom(12)
    key = _key(_passphrase(), salt, iterations)
    plain = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ct = AESGCM(key).encrypt(iv, plain, None)
    env = {
        "v": 1,
        "kdf": "PBKDF2-SHA256",
        "iter": iterations,
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ct": base64.b64encode(ct).decode(),
    }
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(env, f)
    os.replace(tmp, out_path)


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "decrypt":
        json.dump(decrypt(sys.argv[2]), sys.stdout, ensure_ascii=False, indent=2)
        print()
    elif cmd == "encrypt":
        if len(sys.argv) < 4:
            sys.exit(__doc__)
        data = json.load(open(sys.argv[2], encoding="utf-8"))
        encrypt(data, sys.argv[3])
        # Comprobación: se puede volver a abrir
        assert decrypt(sys.argv[3]) == data
        print("Cifrado OK ->", sys.argv[3])
    elif cmd == "check":
        d = decrypt(sys.argv[2])
        print("OK, actualizado:", d.get("updated"))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
