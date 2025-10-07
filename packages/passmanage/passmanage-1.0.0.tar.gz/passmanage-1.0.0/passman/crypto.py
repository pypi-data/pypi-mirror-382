from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import bcrypt
import os

KEY_LENGTH = 32
I_VECTOR = 16
SALT_SIZE = 16
ITERATIONS = 100_000

def derive_key(master_password: str , salt: bytes)->bytes:
    kdf = PBKDF2HMAC(
        algorithm= hashes.SHA256(),
        length= KEY_LENGTH,
        salt= salt,
        iterations= ITERATIONS,
        backend=default_backend()
    )
    key = kdf.derive(master_password.encode())
    return key


def encryption(plaintext: str, master_password: str) -> bytes:
    salt = os.urandom(SALT_SIZE)
    iv = os.urandom(I_VECTOR)
    key = derive_key(master_password , salt)

    # Create a Cipher object
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

     # Encrypt the plaintext
    encrypted = cipher.encryptor().update(plaintext.encode()) + cipher.encryptor().finalize()

     # Return the SALT and IV and EncryptedText in bytes
    return salt+iv+encrypted

def decrypt(cipherblob: bytes , master_password: str) -> str:
    # Extract the IV and ciphertext
    salt = cipherblob[:SALT_SIZE]
    iv = cipherblob[SALT_SIZE:SALT_SIZE+I_VECTOR]
    ciphertext = cipherblob[SALT_SIZE+I_VECTOR:]
    key = derive_key(master_password , salt)

    # Create a Cipher object
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())

    # Decrypt the ciphertext
    decrypted = cipher.decryptor().update(ciphertext) + cipher.decryptor().finalize()
    return decrypted.decode()

def hash_master_password(master_password: str) -> bytes:
    hashed_password = bcrypt.hashpw(master_password.encode(), bcrypt.gensalt())
    return hashed_password

def verify_master_password(master_password: str , hashed_password: bytes) -> bool:
    try:
        return bcrypt.checkpw(master_password.encode(), hashed_password)
    except Exception:
        return False
