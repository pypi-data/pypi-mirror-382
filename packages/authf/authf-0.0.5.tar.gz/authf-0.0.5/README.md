![image](https://github.com/1darshanpatil/authf/assets/72539638/803b3fdd-a880-4a0f-9143-9f4247076a04)


# Authf

Authf is an authentication management package developed for Python. It offers a command-line interface that enables the addition, display, and deletion of accounts, along with the capability to generate Time-Based One-Time Passwords (TOTPs) for verifying accounts.



## Features
* Incorporate new accounts featuring encrypted secret keys.
* Account information is securely encrypted using the PBKDF2HMAC cryptography method and saved locally on your device.
* Operates without the need for an internet connection.
* The TOTP remains inaccessible to others, ensuring your security even in the even of devices loss, provided your passwords remain secure.
* Manage (view & remove) TOTP tokens used for account verification.




## Installation



You can install `Authf` using pip:
```bash
pip install authf
```
## Version
```bash
authf --version
```


## Usage



Once installed, you can use the `authf` command to access the authentication tool. Here are some examples of how to use it:

- Add a new account:
```bash
$ authf --addaccount
Enter the account name: apple
Enter password to encrypt the secret key: 
Enter the secret key without any error: theSecretkey
Your TOTP for verification of the account is 685197
```

- View TOTP:
```bash
$ authf --totp
Enter the account name: apple
Enter password to view TOTP: 
Your TOTP for authentication is 270142
```

The primary use of this tool is to allow you to transfer your accounts from one machine to another. Additionally, it provides an opportunity to change the password for existing scripts.

```python
>>> from authf import add_offline; help(add_offline)
```
- Restore accounts Offline:
```bash
$ authf --addoffline
```


- Remove your all accounts

    *Warning: Using the following command will completely remove all your 2FA authentication accounts*

```bash
$ authf --rm
```


## Requirements

AuthF requires Python 3.x. All dependencies are listed in the `requirements.txt` file.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


## Contact

If you have any questions or feedback, feel free to open an issue on GitHub.
