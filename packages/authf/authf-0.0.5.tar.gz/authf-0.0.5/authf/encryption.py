from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import cryptography
import sys  
import base64
# import pyperclip



def colored(text, color):
    """
    Apply ANSI color codes to the text.

    Parameters 
    ----------
    text : str
        The text to be colored.
    color : str
        The color to apply to the text.
        Available options: 'grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'.

    Returns
    -------
    str
        The colored text.
    """
    color_map = {
        'grey': '\033[90m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
    }
    reset = '\033[0m'

    if color not in color_map:
        raise ValueError("Invalid color code. Please choose from: 'grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'.")
    
    return f"{color_map[color]}{text}{reset}"

def print_color(txt, color_code):
    """
    Prints the given text in the specified color.

    Parameters 
    ----------
    txt : str
        The text to be printed.
    color_code : str
        The color code to apply to the text.
        Available options: 'grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'.

    Notes
    -----
    Utilizes the 'colored' function to apply ANSI color codes to the text.
    """
    try:
        print(colored(txt, color_code))
    except ValueError as e:
        print(e)




class DeCode:
    """
    A cryptography class that provides password-based encryption and decryption capabilities.

    This class is designed to securely handle encryption and decryption of data using a symmetric key derived
    from a user-provided password. It utilizes the PBKDF2 HMAC algorithm for key derivation and Fernet for
    symmetric encryption, offering a balance between security and performance for handling sensitive data.

    Attributes:
        key (bytes): A symmetric key derived from the provided password, suitable for use with Fernet encryption.

    Methods:
        __init__(self, password): Initializes the DeCode instance, deriving a cryptographic key from the given password.
        derive_key(self, password): Derives a cryptographic key using PBKDF2 HMAC with SHA256, based on the given password.
        encrypt(self, data): Encrypts the provided data string using the derived key and returns the encrypted data as bytes.
        decrypt(self, encrypted_data): Decrypts the provided encrypted data bytes using the derived key and returns the
                                       decrypted data as a string. If decryption fails due to an invalid key, it prints
                                       an error message and exits the program.

    Raises:
        cryptography.fernet.InvalidToken: If the decryption process fails due to an invalid key, indicating a potential
                                          mismatch between the encryption and decryption keys, usually caused by using
                                          a wrong password.

    Note:
        The class is designed with security in mind, employing a strong hash function (SHA256) and a robust key derivation
        function (PBKDF2 HMAC) to mitigate against brute-force and other common password-based attacks. It is important
        to handle the key and password with care to maintain the security of the encrypted data.
    """
    def __init__(self, password):
        self.key = self.derive_key(password)

    def derive_key(self, password):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'authf_salt',  
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def encrypt(self, data):
        cipher_suite = Fernet(self.key)
        return cipher_suite.encrypt(data.encode())

    def decrypt(self, encrypted_data):
        try:
            cipher_suite = Fernet(self.key)
            return cipher_suite.decrypt(encrypted_data).decode()
        except cryptography.fernet.InvalidToken:
            print_color("You entered the wrong password to decrypt your account's TOTP!", "red")
            sys.exit()


if __name__ == "__main__":
    passwd = input("Enter your password: ")
    locker = DeCode(passwd)

    lock_unlock = input("Enter 'E' to encrypt or 'D' to Decrypt: ")

    if lock_unlock.lower() == 'e':
        secret_key = input("Enter your secret key: ")
        secret_key_encrypted = locker.encrypt(secret_key)
        print(secret_key_encrypted)
      #  pyperclip.copy(secret_key_encrypted.decode())  # Copy the encrypted message to clipboard
      #  print("Encrypted message copied to clipboard.")

    elif lock_unlock.lower() == 'd':
        encrypted_key = input("Enter encrypted message: ")
        secret_key = locker.decrypt(encrypted_key)
        print(secret_key)
