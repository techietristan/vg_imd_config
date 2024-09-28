import base64, os
from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def calculate_key(salt: bytes, passphrase: str):
    key_derivation_function: callable = PBKDF2HMAC(
        algorithm =     hashes.SHA256(),
        length =        32,
        salt =          salt,
        iterations =    64 #16777216,
    )
    encoded_passphrase: bytes = passphrase.encode('utf-8')
    base64_key: bytes = base64.urlsafe_b64encode(key_derivation_function.derive(encoded_passphrase))
    encryption_key: cryptography.fernet.Fernet = Fernet(base64_key)
    
    return encryption_key

def encrypt(passphrase: str, text_to_encrypt: str) -> tuple[bytes, bytes]:
    encoded_passphrase: bytes = passphrase.encode('utf-8')
    salt: bytes = os.urandom(16)
    encryption_key = calculate_key(salt, passphrase)
    encrypted_text: bytes = encryption_key.encrypt(text_to_encrypt.encode('utf-8'))

    return salt, encrypted_text

def decrypt(salt: bytes, encrypted_text: bytes):
    decrypt_passphrase= getpass('Please enter the encryption passphrase: ')
    decryption_key = calculate_key(salt, decrypt_passphrase)
    decrypted_text = decryption_key.decrypt(encrypted_text)

    return decrypted_text

