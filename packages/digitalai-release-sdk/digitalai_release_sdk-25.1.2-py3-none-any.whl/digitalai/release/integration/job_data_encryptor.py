import base64
from abc import ABC, abstractmethod

from Cryptodome.Cipher import AES


class JobDataEncryptor(ABC):
    """
    Abstract base class for encrypting and decrypting job data.
    """

    @abstractmethod
    def decrypt(self, content: str) -> str:
        """
        Decrypt the given content.

        Parameters:
        - content (str): Encrypted content.

        Returns:
        - str: Decrypted content.
        """
        pass

    @abstractmethod
    def encrypt(self, content: str) -> str:
        """
        Encrypt the given content.

        Parameters:
        - content (str): Unencrypted content.

        Returns:
        - str: Encrypted content.
        """
        pass


class NoOpJobDataEncryptor(JobDataEncryptor):
    """
    Job data encryptor that does not perform any encryption or decryption.
    """

    def decrypt(self, content: str) -> str:
        """
        Return the given content as-is.

        Parameters:
        - content (str): Encrypted content.

        Returns:
        - str: The same content that was passed in.
        """
        return content

    def encrypt(self, content: str) -> str:
        """
        Return the given content as-is.

        Parameters:
        - content (str): Unencrypted content.

        Returns:
        - str: The same content that was passed in.
        """
        return content


class AESJobDataEncryptor(JobDataEncryptor):
    """
    Encrypts and decrypts job data using the AES (Advanced Encryption Standard) algorithm.

    Attributes:
        secret_key (bytes): The secret key used for encryption and decryption.
    """

    def __init__(self, secret_key: str):
        """
        Initializes the encryptor with the secret key.

        Args:
            secret_key (str): The secret key as a base64 encoded string.
        """
        self.secret_key = base64.b64decode(secret_key)

    def decrypt(self, content: str) -> str:
        """
        Decrypts the given content using the secret key.

        Args:
            content (str): The content to decrypt, encoded as a base64 string.

        Returns:
            str: The decrypted content as a string.
        """
        byte_array = base64.b64decode(content)
        context_bytes = byte_array[16:-16]
        cipher = AES.new(self.secret_key, AES.MODE_GCM, byte_array[:16])
        decrypted = cipher.decrypt_and_verify(context_bytes, byte_array[-16:])
        return decrypted.decode("UTF-8")

    def encrypt(self, content: str) -> str:
        """
        Encrypts the given content using the secret key.

        Args:
            content (str): The content to encrypt.

        Returns:
            str: The encrypted content, encoded as a base64 string.
        """
        byte_array = content.encode("UTF-8")
        cipher = AES.new(self.secret_key, AES.MODE_GCM)
        encrypted, tag = cipher.encrypt_and_digest(byte_array)
        return base64.b64encode(cipher.nonce + encrypted + tag).decode("UTF-8")

