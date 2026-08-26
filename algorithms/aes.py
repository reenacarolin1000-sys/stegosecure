import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag


SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
ITERATIONS = 600000


def derive_key(password, salt):
    """
    Derive a 256-bit AES key from the user's password.
    """

    if not password:
        raise ValueError("Encryption key cannot be empty.")

    if isinstance(password, str):
        password = password.encode("utf-8")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS
    )

    return kdf.derive(password)


def encrypt_message(message, password):
    """
    Encrypt a text message using AES-256-GCM.

    Returns a Base64 encoded encrypted value containing:
    salt + nonce + ciphertext.
    """

    if not message:
        raise ValueError("Message cannot be empty.")

    if not password:
        raise ValueError("Encryption key cannot be empty.")

    message_bytes = message.encode("utf-8")

    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)

    key = derive_key(password, salt)

    aes = AESGCM(key)

    ciphertext = aes.encrypt(
        nonce,
        message_bytes,
        None
    )

    encrypted_data = salt + nonce + ciphertext

    return base64.b64encode(encrypted_data).decode("utf-8")


def decrypt_message(encrypted_message, password):
    """
    Decrypt an AES-256-GCM encrypted message.
    """

    if not encrypted_message:
        raise ValueError("Encrypted message cannot be empty.")

    if not password:
        raise ValueError("Encryption key cannot be empty.")

    try:

        encrypted_data = base64.b64decode(
            encrypted_message
        )

        salt = encrypted_data[:SALT_SIZE]

        nonce = encrypted_data[
            SALT_SIZE:SALT_SIZE + NONCE_SIZE
        ]

        ciphertext = encrypted_data[
            SALT_SIZE + NONCE_SIZE:
        ]

        key = derive_key(password, salt)

        aes = AESGCM(key)

        plaintext = aes.decrypt(
            nonce,
            ciphertext,
            None
        )

        return plaintext.decode("utf-8")

    except InvalidTag:

        raise ValueError(
            "Incorrect encryption key or corrupted encrypted data."
        )

    except Exception:

        raise ValueError(
            "Unable to decrypt the message."
        )


def ciphertext_to_binary(encrypted_message):
    """
    Convert the encrypted Base64 string into a binary string.
    """

    encrypted_data = base64.b64decode(
        encrypted_message
    )

    binary = ''.join(
        format(byte, "08b")
        for byte in encrypted_data
    )

    return binary


def binary_to_ciphertext(binary):
    """
    Convert a binary string back into the Base64
    encrypted message format.
    """

    if not binary:
        raise ValueError("Binary data cannot be empty.")

    if len(binary) % 8 != 0:
        raise ValueError(
            "Binary data length must be a multiple of 8."
        )

    byte_values = [
        int(
            binary[index:index + 8],
            2
        )
        for index in range(
            0,
            len(binary),
            8
        )
    ]

    encrypted_data = bytes(byte_values)

    return base64.b64encode(
        encrypted_data
    ).decode("utf-8")


if __name__ == "__main__":

    original_message = "This is a secret message."
    password = "my-secure-key"

    print("Original message:")
    print(original_message)

    encrypted = encrypt_message(
        original_message,
        password
    )

    print("\nEncrypted message:")
    print(encrypted)

    binary = ciphertext_to_binary(
        encrypted
    )

    print("\nBinary length:")
    print(len(binary))

    reconstructed = binary_to_ciphertext(
        binary
    )

    print("\nBinary reconstruction successful:")
    print(reconstructed == encrypted)

    decrypted = decrypt_message(
        reconstructed,
        password
    )

    print("\nDecrypted message:")
    print(decrypted)

    print("\nEncryption test successful:")
    print(decrypted == original_message)