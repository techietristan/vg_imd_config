from unittest import TestCase
from cryptography.fernet import Fernet

from utils.encryption_utils import calculate_key, encrypt, decrypt, decrypt_prompt, DecryptionException

test_config: dict = {'encryption_iterations': 64}
test_passphrase: str = 'test_passphrase'
test_text_to_encrypt: str = 'test_value'
test_salt: str = '743f2386399bb339a11337b8501965c2'

class Test_Calculate_Key(TestCase):

    def test_calculte_key_returns_fernet(self):
        test_encryption_key = calculate_key(test_config, bytes.fromhex(test_salt), test_passphrase)
        self.assertIsInstance(test_encryption_key, Fernet)


class Test_Encrypt(TestCase):

    def test_encrypt_returns_tuple_of_bytes(self):
        returned_tuple = encrypt(test_config, test_passphrase, test_text_to_encrypt, test_salt)
        self.assertIsInstance(returned_tuple, tuple)
        self.assertIsInstance(returned_tuple[0], str)
        self.assertIsInstance(returned_tuple[1], str)

    def test_encrypt_returns_salt_if_specified(self):
        returned_tuple = encrypt(test_config, test_passphrase, test_text_to_encrypt, test_salt)
        self.assertEqual(returned_tuple[0], test_salt)

class Test_Decrypt(TestCase):

    def test_decrypt_returns_original_text_to_encrypt(self):  
        salt, encrypted_text = encrypt(test_config, test_passphrase, test_text_to_encrypt)
        decrypted_text = decrypt(test_config, salt, encrypted_text, test_passphrase)
        self.assertEqual(test_text_to_encrypt, decrypted_text)

    def test_decrypt_returns_false_if_bad_passphrase_supplied(self):  
        salt, encrypted_text = encrypt(test_config, 'bad_passphrase', test_text_to_encrypt)
        decrypted_text = decrypt(test_config, salt, encrypted_text, test_passphrase)
        self.assertFalse(decrypted_text)

class TestDecryptPrompt(TestCase):
    test_string: str = "test_string"
    test_passphrase: str = "test_passphrase"
    invalid_passphrase: str = "invalid_passphrase"
    test_salt, test_encrypted_string = encrypt(test_config, test_passphrase, test_string)

    test_config: dict = { 
        "encryption_iterations": 64,
        "passphrase": test_passphrase
    }

    invalid_test_config: dict = { 
        "encryption_iterations": 64,
        "passphrase": invalid_passphrase
    }

    valid_encrypted_prompt: dict = {
        "salt": test_salt,
        "default_value": test_encrypted_string,
        "encrypt_default": 1 
    }

    invalid_encrypted_prompt: dict = {
        "default_value": test_encrypted_string,
        "encrypt_default": 1 
    }

    expected_decrypted_prompt: dict = {
        "salt": test_salt,
        "default_value": test_string,
        "encrypt_default": 1 
    }

    def test_decrypt_prompt_valid_input(self):
        returned_prompt: dict = decrypt_prompt(self.test_config, self.valid_encrypted_prompt)
        self.assertDictEqual(returned_prompt, self.expected_decrypted_prompt)
        
    def test_decrypt_prompt_invalid_input_returns_unaltered_prompt(self):
        returned_prompt: dict = decrypt_prompt(self.invalid_test_config, self.invalid_encrypted_prompt)
        self.assertDictEqual(returned_prompt, self.invalid_encrypted_prompt)

    def test_decrypt_prompt_invalid_passphrase_raises_exception(self):
        with self.assertRaises(DecryptionException):
            decrypt_prompt(self.invalid_test_config, self.valid_encrypted_prompt)





