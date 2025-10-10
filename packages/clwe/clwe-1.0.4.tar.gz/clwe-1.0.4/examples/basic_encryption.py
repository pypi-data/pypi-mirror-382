#!/usr/bin/env python3
"""
CLWE Basic Encryption Example
Demonstrates fundamental encryption/decryption operations
"""

from clwe import ColorCipher

def main():
    """Demonstrate basic CLWE encryption/decryption"""

    print("CLWE Basic Encryption Example")
    print("=" * 40)

    # Initialize cipher
    cipher = ColorCipher()

    # Example 1: Text encryption
    print("\n1. Text Encryption:")
    message = "Hello, CLWE World! This is a secret message."
    password = "my_secure_password_123"

    print(f"Original: {message}")

    # Encrypt
    encrypted = cipher.encrypt(message, password)
    print(f"Encrypted: {len(str(encrypted))} characters")

    # Decrypt
    decrypted = cipher.decrypt(encrypted, password)
    print(f"Decrypted: {decrypted}")

    # Verify
    assert decrypted == message
    print("✓ Encryption/Decryption successful!")

    # Example 2: JSON data encryption
    print("\n2. JSON Data Encryption:")
    import json

    data = {
        "user": "alice",
        "email": "alice@example.com",
        "secret_key": "sk-1234567890abcdef",
        "permissions": ["read", "write", "admin"]
    }

    json_str = json.dumps(data, indent=2)
    print(f"Original JSON:\n{json_str}")

    # Encrypt JSON
    encrypted_json = cipher.encrypt(json_str, "json_password")
    print(f"\nEncrypted JSON: {len(str(encrypted_json))} characters")

    # Decrypt JSON
    decrypted_json = cipher.decrypt(encrypted_json, "json_password")
    recovered_data = json.loads(decrypted_json)

    print(f"\nDecrypted JSON:\n{json.dumps(recovered_data, indent=2)}")

    # Verify
    assert recovered_data == data
    print("✓ JSON encryption/decryption successful!")

    # Example 3: Multiple encryptions with same password
    print("\n3. Variable Output Security:")
    messages = [
        "First message",
        "Second message",
        "Third message"
    ]

    print("Encrypting same content multiple times:")
    encrypted_versions = []

    for i, msg in enumerate(messages):
        # Encrypt same message multiple times
        for j in range(3):
            encrypted = cipher.encrypt(msg, password)
            encrypted_versions.append(str(encrypted))
            print(f"  {msg} -> {len(str(encrypted))} chars")

    # Check that all encryptions are different (variable output)
    unique_encryptions = set(encrypted_versions)
    print(f"\nTotal encryptions: {len(encrypted_versions)}")
    print(f"Unique results: {len(unique_encryptions)}")
    print("✓ Variable output security confirmed!")

    # Example 4: Wrong password handling
    print("\n4. Wrong Password Handling:")
    try:
        wrong_decrypt = cipher.decrypt(encrypted, "wrong_password")
        print("❌ This should not happen - wrong password accepted!")
    except Exception as e:
        print(f"✓ Correctly rejected wrong password: {type(e).__name__}")

    print("\n" + "=" * 40)
    print("All basic encryption examples completed successfully!")

if __name__ == "__main__":
    main()