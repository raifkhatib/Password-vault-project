# Password Vault Security Notes

## Purpose

This document explains the security design of the Password Vault application, the controls currently implemented, and the limitations of the local demonstration environment.

The project protects two different types of information:

1. The user's master password, which is hashed for authentication.
2. Saved credential information, which is encrypted for later recovery.

Hashing and encryption serve different purposes and are not interchangeable.

## System Components

| Component | Responsibility |
|---|---|
| Browser | Displays pages and submits forms |
| Flask application | Validates requests and controls application logic |
| Flask-Login | Manages authenticated user state |
| Flask-Session and CacheLib | Store session information on the server |
| Flask-WTF | Validates forms and CSRF tokens |
| SQLAlchemy | Communicates with the SQLite database |
| SQLite | Stores users and encrypted credentials |
| Cryptography library | Derives keys and encrypts credential data |

## Registration Flow

1. The browser submits a username, master password, password confirmation, and CSRF token.
2. Flask-WTF validates the submitted fields.
3. The application checks whether the username is already registered.
4. Werkzeug hashes the master password.
5. The application generates a random 16-byte encryption salt.
6. The user record is stored in SQLite.
7. The original master password is not stored.

## Authentication Flow

1. The user submits a username and master password.
2. The application finds the user through SQLAlchemy.
3. Werkzeug checks the submitted password against the stored hash.
4. If authentication succeeds, Flask-Login creates the authenticated user state.
5. The application derives the user's vault key from the submitted master password and stored encryption salt.
6. The vault key is placed in the server-side session.
7. The browser receives only a session identifier, not the vault key.
8. Logging out clears the server-side session.

## Credential Storage Flow

1. An authenticated user submits credential information.
2. Flask-WTF validates the form and CSRF token.
3. The server obtains the vault key from the server-side session.
4. Each credential field is encrypted using Fernet.
5. SQLAlchemy stores the ciphertext in SQLite.
6. Readable credential passwords are not stored in the database.

## Credential Retrieval Flow

1. The authenticated user requests a credential.
2. The database query checks both the credential ID and current user ID.
3. If the record does not belong to the current user, it is not returned.
4. The server decrypts the credential using the vault key.
5. Jinja escapes displayed values before producing the HTML response.
6. Protected responses use no-store caching headers.

## Password Hashing

The master password is processed using Werkzeug password hashing.

A password hash is one-way. During login, the application checks whether the submitted password produces a valid result for the stored hash. It does not decrypt the stored hash.

This protects against storing master passwords as readable text.

## Key Derivation

The application derives a separate vault key for each user using:

- PBKDF2-HMAC-SHA256
- The user's master password
- A random 16-byte salt
- 600,000 iterations
- A 32-byte derived key encoded for Fernet

Using a different random salt for each user means identical master passwords do not automatically produce identical vault keys.

The salt does not need to be secret and is stored with the user record. Its purpose is to prevent precomputed attacks and make each derived key unique.

## Credential Encryption

Fernet provides authenticated symmetric encryption.

It provides:

- Confidentiality, because credential values are stored as ciphertext.
- Integrity checking, because modified ciphertext fails authentication.
- Symmetric encryption, meaning the same derived key is used for encryption and decryption.

The database stores encrypted service names, usernames, passwords, websites, and notes.

## Authentication Tags and Digital Signatures

Fernet includes a message authentication code that allows the application to detect modified ciphertext. This authentication tag is created during encryption and checked during decryption.

This is not a public-key digital signature. It does not prove identity to an independent third party because Fernet uses a shared symmetric key.

The application does not implement public-key digital signatures because it is a local client-server demonstration without separate message-signing users.

Flask-WTF creates signed CSRF tokens using the application's secret key. The server validates these tokens when forms are submitted. This proves that the form token was created for the application session, but it is also not a user-created public-key signature.

## CSRF Protection

All Flask-WTF forms contain a CSRF token.

For state-changing requests, the server checks this token before processing the request. Requests without a valid token are rejected.

Logout and credential deletion use POST forms rather than unprotected GET links.

## SQL Injection Protection

The application uses SQLAlchemy queries and does not build database commands by joining user input into raw SQL strings.

SQLAlchemy sends values as parameters, reducing the risk of SQL injection.

Database authorization queries also include the current user's ID.

## Cross-Site Scripting Protection

Jinja automatically escapes variables displayed inside HTML templates.

A Content Security Policy restricts scripts, styles, images, frames, forms, and objects. Inline JavaScript is not required by the current application.

User input should never be marked as safe unless it has been separately reviewed and sanitized.

## Session Security

Session data is stored on the server through Flask-Session and CacheLib.

Configured protections include:

- HTTP-only session cookies
- SameSite=Lax cookies
- Random session identifiers
- A 30-minute permanent session lifetime
- Session clearing during logout
- No-store caching on protected pages

`SESSION_COOKIE_SECURE` is disabled only because the project runs through local HTTP. It must be enabled when deploying with HTTPS.

## HTTP Security Headers

The application sends the following headers:

- `Content-Security-Policy`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Cross-Origin-Opener-Policy: same-origin`
- `Permissions-Policy`
- Protected-page cache restrictions

These controls help reduce clickjacking, content injection, MIME confusion, information leakage, and unwanted browser permissions.

## Password Generator Security

The password generator uses Python's `secrets` module, which is designed for security-sensitive randomness.

Each generated password contains at least:

- One uppercase character
- One lowercase character
- One number
- One symbol

The generator rejects lengths below 12 characters.

Generated passwords are displayed temporarily and are not automatically saved.

## Data in Transit

The current project runs at:

```text
http://127.0.0.1:5000
```

This is a local development address. Communication uses HTTP and is not protected by TLS.

Because the traffic remains on the same computer, this is acceptable only for a local university demonstration. A remote or public deployment must use HTTPS so credentials are encrypted while travelling between the browser and server.

Database encryption protects credentials at rest. It does not replace HTTPS protection for data in transit.

## Security Tests

The automated tests check:

- Password hashing and verification
- Random encryption salts
- User and credential ownership relationships
- Repeatable key derivation
- Different keys from different salts
- Successful encryption and decryption
- Rejection of tampered ciphertext
- Password generator character requirements
- Rejection of insecure generator lengths
- HTTP security headers
- Authentication requirements
- CSRF rejection

Run the tests with:

```powershell
python -m pytest -q
```

## Current Limitations

The project is a local educational demonstration, not a production password manager.

It does not currently provide:

- HTTPS
- Multi-factor authentication
- Login rate limiting
- Master-password recovery
- Security event auditing
- Automatic backups
- Production secret management
- Independent penetration testing
- Protection against a compromised logged-in computer
- Protection if an attacker obtains both the master password and database

A production version would require a production WSGI server, HTTPS, secure cookies, rate limiting, stronger operational controls, backup procedures, and independent security review.