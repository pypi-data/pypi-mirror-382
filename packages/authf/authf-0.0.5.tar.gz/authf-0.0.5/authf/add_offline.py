#!/usr/bin/env python3
import os
import json
import base64
from getpass import getpass
from .engine import CredentialsManager, print_color, DeCode

def decrypt_secret_key(encrypted_key_base64, password):
    """
    Decrypts an encrypted key using a specified password.
    
    Args:
    encrypted_key_base64 (str): The base64-encoded encrypted key.
    password (str): The password used to decrypt the key.
    
    Returns:
    bytes: The decrypted key, or None if decryption fails.
    """
    try:
        encrypted_key = base64.b64decode(encrypted_key_base64)
        decoder = DeCode(password)
        decrypted_key = decoder.decrypt(encrypted_key)
        return decrypted_key
    except Exception as e:
        print_color(f"Decryption failed: {str(e)}", "red")
        return None

def re_encrypt_key(decrypted_key, password):
    """
    Re-encrypts a decrypted key with a new or same password.
    
    Args:
    decrypted_key (bytes): The decrypted key to be re-encrypted.
    password (str): The password to use for re-encrypting the key.
    
    Returns:
    str: The base64-encoded re-encrypted key, or None if re-encryption fails.
    """
    try:
        encoder = DeCode(password)
        re_encrypted_key = encoder.encrypt(decrypted_key)
        return base64.b64encode(re_encrypted_key).decode()
    except Exception as e:
        print_color(f"Re-encryption failed: {str(e)}", "red")
        return None

def add_offline():
    """
    Adds or updates an account's encrypted key from one machine to another one.
    The user is prompted to input account details and encryption information.
    Re-encryption option is provided if needed.
    """
    manager = CredentialsManager()  # Initialize the CredentialsManager from engine.py
    account_name = input("Enter the account name: ")
    
    if account_name in manager.credentials:
        response = input(f"Account '{account_name}' already exists. Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print_color("Operation canceled. No changes made.", "yellow")
            return
    else:
        response = input(f"Account '{account_name}' does not exist. Do you want to add it? (yes/no): ")
        if response.lower() != 'yes':
            print_color("Operation canceled. No changes made.", "yellow")
            return

    encrypted_key_base64 = input("Enter the encrypted secret key (Base64): ")
    password = getpass("Enter the password used for encrypting the key: ")

    decrypted_key = decrypt_secret_key(encrypted_key_base64, password)
    if decrypted_key is not None:
        # Ask user if they want to use another password for re-encrypting the key
        use_new_password = input("Do you want to re-encrypt the key using a different password? (yes/no): ").lower()
        if use_new_password == 'yes':
            new_password = getpass("Enter the new password for re-encrypting the key: ")
            re_encrypted_key_base64 = re_encrypt_key(decrypted_key, new_password)
        else:
            re_encrypted_key_base64 = re_encrypt_key(decrypted_key, password)
        
        if re_encrypted_key_base64:
            manager.add_account(account_name, re_encrypted_key_base64)
            print_color("Account updated successfully. Secret key re-encrypted and saved securely.", "green")
        else:
            print_color("Re-encryption failed. Changes not saved.", "red")
    else:
        print_color("Failed to verify secret key with provided password.", "red")

if __name__ == '__main__':
    add_offline()
