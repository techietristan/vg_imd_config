import base64, os
from getpass import getpass
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from utils.dict_utils import get_value_if_key_exists

encoding_format: str = 'utf-8'

def calculate_key(config: dict, salt: bytes, passphrase: str) -> Fernet:
    iterations_in_config = get_value_if_key_exists(config, 'encryption_iterations')
    iterations: int = iterations_in_config if bool(iterations_in_config) else 65536

    key_derivation_function: PBKDF2HMAC = PBKDF2HMAC(
        algorithm =     hashes.SHA256(),
        length =        32,
        salt =          salt,
        iterations =    iterations  
    )
    encoded_passphrase: bytes = passphrase.encode(encoding_format)
    base64_key: bytes = base64.urlsafe_b64encode(key_derivation_function.derive(encoded_passphrase))
    encryption_key: Fernet = Fernet(base64_key)

    return encryption_key

def encrypt(config: dict, passphrase: str, text_to_encrypt: str, existing_salt: str = '') -> tuple[str, str]:
    encoded_passphrase: bytes = passphrase.encode(encoding_format)
    salt: bytes = bytes.fromhex(existing_salt) if bool(existing_salt) else os.urandom(16)
    encryption_key = calculate_key(config, salt, passphrase)
    encrypted_text: bytes = encryption_key.encrypt(text_to_encrypt.encode(encoding_format))

    return salt.hex(), encrypted_text.hex()

def decrypt(config: dict, salt: str, encrypted_text: str, passphrase: str) -> str | bool:
    try:
        decryption_key: Fernet = calculate_key(config, bytes.fromhex(salt), passphrase)
        decrypted_text: str = decryption_key.decrypt(bytes.fromhex(encrypted_text)).decode(encoding_format)

        return decrypted_text

    except InvalidToken as token_error:
        
        return False
