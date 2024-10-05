from unittest import TestCase
from cryptography.fernet import Fernet

from utils.encryption_utils import calculate_key, encrypt, decrypt

test_config: dict = {'encryption_iterations': 64}
test_passphrase: str = 'test_passphrase'
test_text_to_encrypt: str = 'test_value'
test_salt: bytes = b't?#\x869\x9b\xb39\xa1\x137\xb8P\x19e\xc2'

class Test_Calculate_Key(TestCase):

    def test_calculte_key_returns_fernet(self):
        test_encryption_key = calculate_key(test_config, test_salt, test_passphrase)
        self.assertIsInstance(test_encryption_key, Fernet)


class Test_Encrypt(TestCase):

    def test_encrypt_returns_tuple_of_bytes(self):
        returned_tuple = encrypt(test_config, test_passphrase, test_text_to_encrypt, test_salt)
        self.assertIsInstance(returned_tuple, tuple)
        self.assertIsInstance(returned_tuple[0], bytes)
        self.assertIsInstance(returned_tuple[1], bytes)

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




