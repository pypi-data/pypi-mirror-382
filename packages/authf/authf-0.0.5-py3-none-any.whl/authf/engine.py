import os
import json
import pyotp
from .encryption import *



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


class CredentialsManager:
    """
    A class for managing credentials securely.

    Attributes:
        filename (str): The path to the JSON file storing the credentials.
        credentials (dict): A dictionary containing account names as keys and secret keys as values.
    """
    def __init__(self) -> None:
        """
        Initializes the CredentialsManager object.

        The default filename for storing credentials is '~/.authf.json'.

        Returns:
            None
        """
        self.filename = os.path.expanduser("~/.authf.json")
        self.credentials = self.load_credentials()

    def load_credentials(self):
        """
        Loads credentials from the JSON file.

        If the file does not exist or is empty, an empty dictionary is returned.

        Returns:
            dict: A dictionary containing loaded credentials.
        """
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {}

    def add_account(self, account_name, secret_key):
        """
        Adds a new account and its secret key to the credentials.

        Args:
            account_name (str): The name of the account.
            secret_key (str): The secret key associated with the account.

        Returns:
            None
        """
        try:
            self.credentials[account_name] = secret_key
            with open(self.filename, 'w') as file:
                json.dump(self.credentials, file)
        except Exception as e:
            print_color(f"Unexpected error {e}")


    def get_secret_key(self, account_name):
        """
        Retrieves the secret key associated with the specified account.

        Args:
            account_name (str): The name of the account whose secret key is to be retrieved.

        Returns:
            str or None: The secret key if found, otherwise None.
        """
        return self.credentials.get(account_name)

class Authenticator:
    """
    A class for generating Time-Based One-Time Passwords (TOTP) for authentication.

    Attributes:
        totp (pyotp.TOTP or None): The TOTP object for generating one-time passwords.
    """
    def __init__(self) -> None:
        """
        Initializes the Authenticator object.

        Returns:
            None
        """
        pass        

    def generate_totp(self, secret_key):
        """
        Generates a Time-Based One-Time Password (TOTP) using the provided secret key.

        Args:
            secret_key (str): The secret key associated with the account.

        Returns:
            str or None: The generated one-time password if successful, otherwise None.
        """

        try:
            self.totp = pyotp.TOTP(secret_key)
            return self.totp.now()
        except TypeError:
            print("No account or secret key found.")

