# Password Vault User Guide

## Starting the Application

Open PowerShell in the project folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_and_run.ps1
```

Wait until the terminal displays:

```text
All checks passed.
Open http://127.0.0.1:5000 in your browser.
```

Open a browser and visit:

```text
http://127.0.0.1:5000
```

Keep the PowerShell terminal open while using the application.

## Creating an Account

1. Select **Create an account**.
2. Enter a username.
3. Enter a master password containing at least 12 characters.
4. Enter the same password in the confirmation field.
5. Select **Create account**.

The username must contain only letters, numbers, and underscores.

The master password is hashed before being stored. It should not be reused from a real account.

## Logging In

1. Select **Log in**.
2. Enter the registered username.
3. Enter the correct master password.
4. Select **Log in**.

After successful authentication, the homepage shows the signed-in username and a link to the vault.

## Opening the Vault

Select **Open your vault** from the homepage or **Vault** from the navigation bar.

The vault displays credentials belonging only to the signed-in user.

## Adding a Credential

1. Open the vault.
2. Select **Add credential**.
3. Enter a service name, such as `GitHub`.
4. Enter the username or email used for the service.
5. Enter the password.
6. Optionally enter a website address and notes.
7. Select **Save credential**.

The application encrypts the credential fields before saving them in SQLite.

Use only fictional information when demonstrating the project.

## Viewing a Credential

1. Open the vault.
2. Find the required credential.
3. Select **View**.

The application retrieves the encrypted database record, confirms ownership, decrypts it, and displays the details.

## Editing a Credential

1. Open the credential.
2. Select **Edit**.
3. Change the required information.
4. Re-enter the credential password.
5. Select **Save credential**.

The updated values are encrypted before being stored again.

## Deleting a Credential

1. Open the credential.
2. Select **Delete**.
3. Confirm the deletion if the browser requests confirmation.

Deletion uses a protected POST request with a CSRF token.

## Generating a Password

1. Select **Generator** in the navigation bar.
2. Choose a password length of at least 12 characters.
3. Select **Generate password**.
4. Copy the displayed password before leaving or refreshing the page.

Generated passwords are not automatically saved. To keep one, add it to a credential in the vault.

## Logging Out

Select **Log out** in the navigation bar.

Logging out clears the vault encryption key from the server-side session. The protected vault pages cannot be opened again until the user logs back in.

## Running the Tests

Stop the server with `Ctrl+C`, then run:

```powershell
python -m pytest -q
```

A successful result should show all tests passing.

## Stopping the Application

Return to the PowerShell terminal running Flask and press:

```text
Ctrl+C
```

The local website will stop. Visit the same address again only after restarting the application.

## Troubleshooting

### The browser says the page cannot be reached

The Flask server is not running. Start it using:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_and_run.ps1
```

### PowerShell blocks script execution

Use the complete command:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_and_run.ps1
```

This bypass applies to that PowerShell process and does not permanently change the system policy.

### A Python package is missing

Activate the virtual environment and reinstall the requirements:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Login fails

Check that the username and master password are correct. Passwords are case-sensitive.

### A generated password disappeared

Generated passwords exist only on the generator result page. Copy the password before refreshing, closing, or leaving the page.

## Demonstration Checklist

For a short project demonstration:

1. Start the application.
2. Show the automated tests passing.
3. Register a demonstration user.
4. Log in.
5. Generate a secure password.
6. Add a fictional credential.
7. View the credential.
8. Edit the credential.
9. Delete the credential.
10. Log out.
11. Show that the vault requires authentication.