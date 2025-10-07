
🔐 Passman — Simple CLI Password Manager

Passman is a lightweight, command-line based password manager built in Python.
It securely stores your passwords in an encrypted SQLite database — only accessible with your master password.

🚀 Features:

  🔒 Secure AES-based encryption using a master password

  🧠 Master password verified before any access

  🗄️ Passwords stored locally in an encrypted SQLite database

  📜 List, add, delete, or retrieve services easily

  🎨 Colored output for better readability

  ⚙️ Cross-platform (Linux, macOS, Windows)

📦 Installation:
  🧩 Option 1: Local Installation (Developer Mode)

  Clone the repository and install it locally in editable mode:
  ```bash:

  git clone https://github.com/<your-username>/passman.git
  cd passman
  pip install -e .

💡 The -e flag means “editable mode”, so any changes to the code will reflect instantly.

  Now, you can use the command:
  pass
  
🔑 First-Time Setup:

  When you run any command (like add, list, get, etc.) for the first time,
  passman will automatically ask you to create a master password:

    ```bash
    No Master Password Set. Let's Create One Now.
    Create Master Password: ********
    Confirm Master Password: ********
    Master password saved. Keep it safe!

  This password will be used to encrypt and decrypt all your stored credentials.
  You’ll need to enter it every time you open a new terminal session.

⚙️ Usage:

  📥 Add a new service
    Add a password for a service (e.g., Gmail, GitHub, Discord):

  ```bash
    pass add <service_name> -u <username> <password>

  🔍 Get a service password

  Retrieve a stored password for a service:
    pass get <service_name>

  📋 List all saved services
  1️⃣  Without showing passwords:
    pass list

  2️⃣ Show list with decrypted passwords: 
    pass list --show

  ❌ Delete a service
    Remove a saved password entry by service name:

    pass del <service_name>

💻 Development Commands 

   - Install locally (editable):
      pip install -e .
   - Uninstall:
      pip uninstall passman -y


🧠 Future Enhancements

  🔐 Multi-user support

  ☁️ Optional cloud sync

  🧩 Auto password generation

  🧰 Backup and restore feature