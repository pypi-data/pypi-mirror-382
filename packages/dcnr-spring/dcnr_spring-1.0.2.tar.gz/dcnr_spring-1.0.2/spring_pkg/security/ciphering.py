__all__ = ['cipher', 'decipher']

def cipher(text: str, key: str) -> str:
    """
    Encrypts the input text using the XOR algorithm and the key.
    Returns the result as a hexadecimal string.
    
    Args:
        text (str): The text we want to encrypt.
        key (str): A key (e.g. 24 characters long) that is repeated if the text is longer.
    
    Returns:
        str: Encrypted text in hex format.
    """
    # Zakódujeme text a kľúč do bajtov (UTF-8)
    text_bytes = text.encode('utf-8')
    key_bytes = key.encode('utf-8')
    
    # Vykonáme XOR pre každý bajt, kľúč sa opakuje
    encrypted_bytes = bytearray(
        b ^ key_bytes[i % len(key_bytes)]
        for i, b in enumerate(text_bytes)
    )
    
    # Pre konverziu do čitateľného reťazca použijeme hex kódovanie
    return encrypted_bytes.hex()


def decipher(encrypted_hex: str, key: str) -> str:
    """
    Decrypts a hexadecimal string that was encrypted with the encrypt() function,
    using the same algorithm and XOR key.
    
    Args:
        encrypted_hex (str): Encrypted text in hex format.
        key (str): The encryption key used.
    
    Returns:
        str: Original (decrypted) text.
    """
    # Prevod hex reťazca späť do bajtov
    encrypted_bytes = bytes.fromhex(encrypted_hex)
    key_bytes = key.encode('utf-8')
    
    # XOR pre každý bajt opäť
    decrypted_bytes = bytearray(
        b ^ key_bytes[i % len(key_bytes)]
        for i, b in enumerate(encrypted_bytes)
    )
    
    # Dekódujeme bajty späť na text (UTF-8)
    return decrypted_bytes.decode('utf-8')


# Príklad použitia:
if __name__ == "__main__":
    original_text = "This is example text with length of approximatelly 100 characters. " \
                    "Out target is to test ciphering and deciphering."
    key = "SecretKey12345678901234"  # Approx 24 chars

    encrypted = cipher(original_text, key)
    decrypted = decipher(encrypted, key)

    print("Original text:")
    print(original_text)
    print("\nCiphered (hex):")
    print(encrypted)
    print("\nDeciphered text:")
    print(decrypted)
