# Password Vault

A local password manager built with Python and Flask. Users can create an account, log in, generate secure passwords, and store encrypted credentials in a personal vault.

GitHub repository: https://github.com/raifkhatib/Password-vault-project

## Features

- Secure user registration and login
- Password hashing using Werkzeug
- Server-side login sessions
- Separate encrypted vault for each user
- Add, view, edit, and delete credentials
- Secure password generator
- Fernet authenticated encryption
- PBKDF2-HMAC-SHA256 key derivation
- CSRF protection on forms
- Automatic HTML escaping through Jinja
- SQLAlchemy ORM database access
- Security headers and Content Security Policy
- Responsive web interface
- Automated security, model, and web tests

## Technologies

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-WTF
- Flask-Login
- Flask-Session
- CacheLib
- Cryptography
- SQLite
- Pytest
- HTML and CSS

## Project Structure

```text
Password-vault-project/
├── static/
│   └── styles.css
├── templates/
│   ├── base.html
│   ├── credential_detail.html
│   ├── credential_form.html
│   ├── generator.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── vault.html
├── tests/
│   ├── test_models.py
│   ├── test_security.py
│   └── test_web_security.py
├── app.py
├── forms.py
├── models.py
├── requirements.txt
├── security.py
├── setup_and_run.ps1
└── README.md
```

The `instance` directory and SQLite database are created locally and are excluded from Git.

## Automated Setup on Windows

Open PowerShell in the project folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_and_run.ps1
```

The script will:

1. Create a Python virtual environment.
2. Install the required packages.
3. generate a temporary secret key for the current run.
4. Initialize the SQLite database.
5. Run all automated tests.
6. Start the Flask application.

After the checks pass, open:

```text
http://127.0.0.1:5000
```

Press `Ctrl+C` in the terminal to stop the server.

## Manual Setup

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the application:

```powershell
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Running the Tests

With the virtual environment activated, run:

```powershell
python -m pytest -q
```

The current automated test suite covers:

- Password hashing and verification
- Random user encryption salts
- Credential ownership relationships
- Repeatable key derivation
- Different keys from different salts
- Encryption and decryption
- Detection of modified ciphertext
- Password generator requirements
- Rejection of short generated-password lengths
- HTTP security headers
- Authentication protection
- CSRF protection

## Application Flow

1. A user registers with a username and master password.
2. The master password is hashed before the user is stored.
3. During login, the submitted password is checked against the stored hash.
4. A vault encryption key is derived from the master password and the user's random encryption salt.
5. The derived key is held in the server-side session while the user is logged in.
6. Credential fields are encrypted before they are saved in SQLite.
7. Credentials are decrypted only after an authenticated owner requests them.
8. Logging out clears the user's server-side session.

## Security Design

### Authentication passwords

Master passwords are processed using Werkzeug password hashing. The original master password is not stored in the database.

### Credential encryption

Credential values are encrypted using Fernet authenticated encryption. Fernet provides confidentiality and detects ciphertext modification.

A separate key is derived for each user using:

- PBKDF2-HMAC-SHA256
- A random 16-byte user salt
- 600,000 iterations
- The user's master password

The database stores encrypted credential fields rather than readable passwords.

### Access control

Protected routes require authentication. Credential database queries include both the credential ID and the current user's ID, preventing users from requesting another user's records through a changed URL.

### Web security

The application uses:

- Flask-WTF CSRF tokens
- Jinja automatic output escaping
- SQLAlchemy instead of raw SQL
- HTTP-only session cookies
- SameSite session cookie protection
- Server-side sessions
- Content Security Policy
- Clickjacking protection
- MIME-sniffing protection
- No-store caching rules for protected pages

## Password Generator

The password generator uses Python's `secrets` module instead of a predictable pseudo-random generator.

Generated passwords contain at least:

- One uppercase letter
- One lowercase letter
- One number
- One symbol

The minimum permitted length is 12 characters.

## Important Limitations

This project is intended as a local university demonstration and is not a production password manager.

The development server uses local HTTP. A public deployment would additionally require:

- HTTPS
- A production WSGI server
- A permanent secret key stored securely
- Secure session cookies
- Login rate limiting
- Multi-factor authentication
- Production database and key management
- Independent security testing
- Backup and recovery procedures

Do not store real account passwords in the demonstration database.

## Development Progress

The Git history records the project in functional stages, including:

- Initial Flask application
- Database setup
- Secure user registration
- Login and protected sessions
- Responsive interface styling
- Encrypted credential storage
- Credential viewing, editing, and deletion
- Secure password generation
- Automated security tests
- Automated setup and run script

## Author

Raif El-Khatib  
BSc Computer Science project