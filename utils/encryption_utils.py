import base64, json, os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from utils.dict_utils import get_value_if_key_exists
from utils.format_utils import format_red, format_blue
from utils.parse_utils import contains_encrypted_defaults
from utils.prompt_utils import get_input

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
    salt: bytes = bytes.fromhex(existing_salt) if bool(existing_salt) else os.urandom(16)
    encryption_key = calculate_key(config, salt, passphrase)
    encrypted_text: bytes = encryption_key.encrypt(text_to_encrypt.encode(encoding_format))

    return salt.hex(), encrypted_text.hex()

def decrypt(config: dict, salt: str, encrypted_text: str, passphrase: str) -> str | bool:
    try:
        decryption_key: Fernet = calculate_key(config, bytes.fromhex(salt), passphrase)
        decrypted_text: str = decryption_key.decrypt(bytes.fromhex(encrypted_text)).decode(encoding_format)

        return decrypted_text
        
    except InvalidToken:   
        return False

class DecryptionException(Exception):
    pass

def decrypt_prompt(config: dict, prompt: dict) -> dict:
    passphrase: str = get_value_if_key_exists(config, 'passphrase')
    salt: str = get_value_if_key_exists(prompt, 'salt')
    default_value: str = get_value_if_key_exists(prompt, 'default_value')
    if bool(salt) and bool(default_value) and bool(passphrase):
        decrypted_default_value: str | bool = decrypt(config, salt, default_value, passphrase)
        if bool(decrypted_default_value):
            return dict( prompt, **{ 'default_value' : decrypted_default_value } )
        else:
            raise DecryptionException
    return prompt

def decrypt_prompts(config: dict) -> dict:
    prompts_filename: str = get_value_if_key_exists(config, 'interactive_prompts_filename')
    config_files_path: str = get_value_if_key_exists(config, 'config_files_path')
    prompts_file_path: str = os.path.join(config_files_path, prompts_filename)

    with open(prompts_file_path) as prompts_file:
        prompts_file_contents: dict= json.load(prompts_file)
    
    prompts: list[dict] = get_value_if_key_exists(prompts_file_contents, 'prompts')
    passphrase = get_value_if_key_exists(config, 'passphrase')
    if contains_encrypted_defaults(prompts):
        if not bool(passphrase):
            print(f'Encrypted defaults found in \'{format_blue(prompts_filename)}\'.')
            passphrase_prompt: str = 'Please enter the encryption passphrase'
            config['passphrase'] = get_input(config, 'getpass', passphrase_prompt, confirm_input = False)
        try:
            decrypted_prompts: list[dict] = [
                decrypt_prompt(config, prompt)
                for prompt in prompts ]
            return dict(prompts_file_contents, **{ 'prompts': decrypted_prompts })    

        except DecryptionException:
            print(format_red('Incorrect passphrase!'))
            config['passphrase'] = False
            return decrypt_prompts(config)

    return prompts_file_contents