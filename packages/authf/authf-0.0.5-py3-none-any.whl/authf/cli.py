#!/usr/bin/env python3
import pyperclip
from .engine import *
from authf import __version__
from .encryption import *
from .add_offline import *
import argparse
import base64
import os
import getpass


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



def adding():
    """
    Facilitates the secure addition of an account and its corresponding secret key to a credentials storage system.
    The user is prompted to input the account name, a password for secret key encryption, and the secret key itself.
    The secret key is then encrypted with the provided password, encoded in base64 for compatibility with JSON storage,
    and the encrypted key along with the account name are saved in a JSON file. A Time-based One-time Password (TOTP)
    is generated for the secret key to facilitate immediate verification or further setup processes.

    Steps involved in the process:
    1. Collecting the account name, encryption password, and secret key from the user.
    2. Encrypting the secret key using the specified password and encoding this encrypted key in base64 format.
    3. Saving the account name and the base64-encoded encrypted secret key into a JSON file for secure storage.
    4. Generating a TOTP based on the unencrypted secret key for verification purposes.
    5. Displaying the generated TOTP and providing an option to copy it to the clipboard for user convenience.

    Parameters:
        None

    Returns:
        None: Outputs the TOTP for the added account and may copy this TOTP to the clipboard based on user preference.

    Raises:
        None: The function is designed to handle errors internally and provide user-friendly feedback for common issues,
              such as encryption or storage errors, though these are not explicitly raised as exceptions in the docstring.

    Note: This function relies on `CredentialsManager` for secure storage handling and `Authenticator` for TOTP generation.
    It employs `getpass` for secure password input, preventing the password from being displayed on the screen during entry.
    User feedback and options are enhanced with colored messages to clearly communicate status and actions to the user.
    """
    entered_account_name = input("Enter the account name: ")
    passwd_to_encrypt_key = getpass.getpass("Enter password to encrypt the secret key: ")
    secret_key = input("Enter the secret key without any error: ")
    locker = DeCode(passwd_to_encrypt_key)
    entered_secret_key = locker.encrypt(secret_key)
    entered_secret_key_base64 = base64.b64encode(entered_secret_key).decode()
    # As we are storing the secret key in an encrypted format, which is in bytes, and bytes cannot be serialized to JSON.
    # print(entered_secret_key_base64)
    # Saving info. in json file
    credential_manager = CredentialsManager()
    credential_manager.add_account(entered_account_name, entered_secret_key_base64)
    authapp = Authenticator()
    totp_is = authapp.generate_totp(secret_key)
    print("Your TOTP for verification of the account is ", end="")
    print_color(f"{totp_is}", "yellow")
    ask_to_copy = input("Copy to clipboard (Y/n): ")
    if ask_to_copy.lower() == 'y':
        pyperclip.copy(totp_is)
        print_color("Copied to clipboard!", "green")

def viewing_totp():
    """
    Prompts for an account name and a decryption password to retrieve and decrypt the associated secret key,
    then generates a Time-based One-time Password (TOTP) for the account. This process includes several steps:
    1. Asking the user for the account name linked to the secret key.
    2. Requesting the password used to decrypt the secret key.
    3. Fetching the encrypted secret key from a JSON file, where it is stored in base64 format.
    4. Decrypting the secret key using the provided password.
    5. Generating a TOTP based on the decrypted secret key.
    6. Displaying the generated TOTP to the user and offering an option to copy it to the clipboard.

    The function handles potential errors gracefully, providing user-friendly feedback for various failure scenarios,
    such as when the specified account is not found.

    Parameters:
        None

    Returns:
        None: The function prints the generated TOTP to the console and may copy it to the clipboard if the user
              opts to do so.

    Raises:
        TypeError: If the specified account cannot be found in the credentials storage, indicating a possible
                   mismatch in the account name input.

    Note: This function relies on external classes `CredentialsManager` for retrieving encrypted secret keys,
    `DeCode` for decryption, and `Authenticator` for TOTP generation. It ensures security by using `getpass` for
    password input, preventing password echo back in the console. Additionally, it uses colored output to distinguish
    important information and feedback for enhanced user interaction.
    """
    entered_account_name = input("Enter the account name: ")

    passwd_to_decrypt_key = getpass.getpass("Enter password to view TOTP: ")
    try:

        # Retrieving and decoding the secret key
        credentials_manager = CredentialsManager()
        encrypted_key_base64 = credentials_manager.get_secret_key(entered_account_name)
        encrypted_key = base64.b64decode(encrypted_key_base64)
        locker = DeCode(passwd_to_decrypt_key)
        secret_key_is = locker.decrypt(encrypted_key)
    # print(secret_key_is)
        authapp = Authenticator()
        totp_is = authapp.generate_totp(secret_key=secret_key_is) 
        print("Your TOTP for authentication is ", end="")
        print_color(f"{totp_is}", "yellow")
        ask_to_copy = input("Copy to clipboard (Y/n): ")
        if ask_to_copy.lower() == 'y':
            pyperclip.copy(totp_is)
            print_color("Copied to clipboard!", "green")
    except TypeError:
        print_color("Uh-Oh! Account not found.","red")



def hard_reset():
    """
    Initiates the process to securely delete the '.authf.json' file from the user's home directory.
    This file is presumed to contain sensitive secret keys. The function first seeks confirmation
    from the user to proceed with the deletion. If the user confirms, it then attempts to delete the file.

    The deletion process involves the following steps:
    1. Prompting the user for confirmation to delete the file. This step is crucial to avoid accidental
       deletions of sensitive information.
    2. If confirmation is given, the function tries to remove the file from the filesystem.
    3. The user is informed of the outcome of the operation. If the file does not exist, if there are
       permission issues, or if any other exception occurs, appropriate messages are displayed to the user.

    Confirmation input is case-insensitive for 'Y'. Any input other than 'Y' or 'y' will abort the operation.

    Exceptions Raised:
        FileNotFoundError: Raised if the '.authf.json' file does not exist at the expected location, indicating
                           there are no secret keys to delete.
        PermissionError: Raised if the program lacks the necessary permissions to delete the file, suggesting
                         potential issues with file ownership or access rights.
        Exception: Raised for any other unforeseen errors that might occur during the file deletion process.

    Note: The function utilizes `os.remove` for file deletion and handles exceptions to provide user-friendly
    feedback for various failure scenarios. Additionally, it uses colored output to highlight important messages,
    enhancing user interaction and experience.
    """
    
    file_path = os.path.expanduser("~/.authf.json")
    
    confirmation = input(colored("Are you sure you want to delete the secret keys file? (Y/n): ", "red")).strip().lower()
    if confirmation not in  ("Y", 'y'):
        print("Operation aborted.")
        return

    try: 
        os.remove(file_path)
        print_color("Secret keys file deleted successfully.", "green")
    except FileNotFoundError:
        print_color("No accounts found!", "red")
    except PermissionError:
        print_color("Permission denied to delete!", "red")
    except Exception as e:
        print_color(f"An error occurred: {e}", "red")




def main():
    """
    Main entry point for the Authentication Tool.

    This function sets up command-line arguments for managing authentication-related tasks. It allows users to add new accounts, display Time-Based One-Time Passwords (TOTPs), remove accounts, and check the current version of the package. Based on the arguments provided, it calls the appropriate function to handle the requested action.

    Arguments:
    --addaccount : Flag to add a new account.
    --totp       : Flag to display the TOTP for an account.
    --rm         : Flag to remove an existing account.
    --addoffline : Flag to let you restore accounts from other devices.
    --version    : Flag to display the current version of the package.
    """
    parser = argparse.ArgumentParser(description="Authentication Tool", allow_abbrev=False)

    # Add arguments
    parser.add_argument("--addaccount", action="store_true", help="Add a new account")
    parser.add_argument("--totp", action="store_true", help="Shows TOTP")
    parser.add_argument("--rm", action="store_true", help="Removes your accounts")
    parser.add_argument("--addoffline", action="store_true", help="Helps you store accounts from other devices")
    parser.add_argument("--version", action="store_true", help="Current Package version")
    args = parser.parse_args()

    if args.addaccount:
        adding()
    elif args.totp:
        viewing_totp()
    elif args.rm:
        hard_reset()
    elif args.addoffline:
        add_offline()
    elif args.version:
        print(f"Authf: {__version__}")
    else:
        print("Usage: authf [--addaccount | --totp | --rm | --addoffline | --version]")

if __name__ == "__main__":
    main()
