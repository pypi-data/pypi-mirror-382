from .engine import *


if __name__ == "__main__":

    credential_manager = CredentialsManager()

    account_name = input("Enter Account Name: ")
    secret_key = input("Enter Secret Key: ")

    credential_manager.add_account(account_name, secret_key)



    account_name_to_retrive = input("Enter Account Name to retrive Secret key: ")
    secret_key_retrived = credential_manager.get_secret_key(account_name_to_retrive)


    if secret_key_retrived:
        print(f"Secret key for {account_name_to_retrive} : {secret_key_retrived}")

    else:
        print(f"No secret key found for {account_name_to_retrive}")

