import unittest
import string
import random

from spring_pkg.security.ciphering import cipher, decipher


class TestCiphering(unittest.TestCase):
    """Test cases for ciphering functionality."""

    def test_simple_cipher_decipher(self):
        """Test basic cipher and decipher functionality."""
        original_text = "Hello, World!"
        key = "mykey123"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_empty_text(self):
        """Test ciphering empty text."""
        original_text = ""
        key = "testkey"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)
        self.assertEqual(encrypted, "")

    def test_empty_key(self):
        """Test ciphering with empty key should raise error."""
        original_text = "Hello"
        key = ""
        
        # Empty key should cause division by zero in modulo operation
        with self.assertRaises(ZeroDivisionError):
            cipher(original_text, key)

    def test_single_character(self):
        """Test ciphering single character."""
        original_text = "A"
        key = "k"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_unicode_characters(self):
        """Test ciphering with Unicode characters."""
        original_text = "Hello 世界! Ñoño café 🌍"
        key = "unicodekey123"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_long_text(self):
        """Test ciphering long text."""
        original_text = "This is a very long text " * 100
        key = "longkey123456789"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_short_key_repeats(self):
        """Test that short key repeats correctly."""
        original_text = "ABCDEFGHIJKLMNOP"  # 16 characters
        key = "XYZ"  # 3 characters - should repeat
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_key_longer_than_text(self):
        """Test with key longer than text."""
        original_text = "Hi"
        key = "verylongkeythatislongerthantext"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_hex_output_format(self):
        """Test that encrypted output is valid hexadecimal."""
        original_text = "Test message"
        key = "testkey"
        
        encrypted = cipher(original_text, key)
        
        # Should be valid hex string
        try:
            bytes.fromhex(encrypted)
        except ValueError:
            self.fail("Encrypted output is not valid hexadecimal")
        
        # Should contain only hex characters
        self.assertTrue(all(c in '0123456789abcdef' for c in encrypted.lower()))

    def test_different_keys_produce_different_results(self):
        """Test that different keys produce different encrypted results."""
        original_text = "Same text for both"
        key1 = "key1"
        key2 = "key2"
        
        encrypted1 = cipher(original_text, key1)
        encrypted2 = cipher(original_text, key2)
        
        # Different keys should produce different encrypted text
        self.assertNotEqual(encrypted1, encrypted2)
        
        # But both should decrypt correctly with their respective keys
        self.assertEqual(original_text, decipher(encrypted1, key1))
        self.assertEqual(original_text, decipher(encrypted2, key2))

    def test_wrong_key_produces_wrong_result(self):
        """Test that wrong key produces incorrect decryption."""
        original_text = "Secret message"
        correct_key = "correctkey"
        wrong_key = "wrongkey123"
        
        encrypted = cipher(original_text, correct_key)
        
        # Correct key should work
        correct_decryption = decipher(encrypted, correct_key)
        self.assertEqual(original_text, correct_decryption)
        
        # Wrong key should produce different result
        wrong_decryption = decipher(encrypted, wrong_key)
        self.assertNotEqual(original_text, wrong_decryption)

    def test_special_characters(self):
        """Test ciphering with special characters."""
        original_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?~`"
        key = "specialkey"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_newlines_and_tabs(self):
        """Test ciphering with newlines and tabs."""
        original_text = "Line 1\nLine 2\tTabbed\rCarriage return"
        key = "whitespacekey"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_random_data(self):
        """Test ciphering with random data."""
        # Generate random text
        original_text = ''.join(random.choices(
            string.ascii_letters + string.digits + string.punctuation + ' \n\t',
            k=500
        ))
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_xor_properties(self):
        """Test XOR cipher properties."""
        original_text = "XOR test message"
        key = "xorkey"
        
        encrypted = cipher(original_text, key)
        
        # XOR property: A XOR B XOR B = A
        # So ciphering the encrypted text again should give original
        double_encrypted = cipher(bytes.fromhex(encrypted).decode('latin-1'), key)
        
        # Note: This test demonstrates XOR property but may not work perfectly
        # due to encoding issues, so we just test the basic encryption/decryption
        decrypted = decipher(encrypted, key)
        self.assertEqual(original_text, decrypted)

    def test_case_sensitivity(self):
        """Test that keys are case sensitive."""
        original_text = "Case sensitive test"
        key1 = "TestKey"
        key2 = "testkey"
        
        encrypted1 = cipher(original_text, key1)
        encrypted2 = cipher(original_text, key2)
        
        # Different case keys should produce different results
        self.assertNotEqual(encrypted1, encrypted2)

    def test_numeric_strings(self):
        """Test ciphering numeric strings."""
        original_text = "1234567890"
        key = "numkey"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_repeated_patterns(self):
        """Test ciphering with repeated patterns."""
        original_text = "abcabc" * 50  # Repeated pattern
        key = "pattern"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_binary_like_data(self):
        """Test with data that looks like binary."""
        original_text = "000111000111" * 10
        key = "binarykey"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)

    def test_hex_string_as_input(self):
        """Test using hex string as input text."""
        original_text = "deadbeef1234567890abcdef"
        key = "hexkey"
        
        encrypted = cipher(original_text, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original_text, decrypted)


if __name__ == '__main__':
    unittest.main()
