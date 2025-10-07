#!/usr/bin/env python3

import argparse
import getpass
from .crypto import encryption,decrypt, hash_master_password, verify_master_password
from . import database
import os


# Colors using ANSI escape codes
BLUE = "\033[94m"
GREEN = "\033[92m"  
DARK_GREEN = "\033[32m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

_is_master = None

def check_master_password():
    """
        Check the master password is existes or not
    """

    database.init_db()
    isexists =  database.get_hash()
    if isexists is None:
        print("No Master Password Set. Let's Create One Now.")
        while True:
            pwd1 = getpass.getpass("Create Master password: ")
            pwd2 = getpass.getpass("Confirm Master password: ")
            if not pwd1:
                print("Master password not be empty.")
                continue
            if pwd1 != pwd2:
                print("Password not same! Try Again.")
                continue
            hashed_password = hash_master_password(pwd1)
            database.store_hash(hashed_password)
            print(f"{YELLOW} Master password saved , Keep it safe. {RESET}")
            return

def master_password_manager() -> str:
    global _is_master
    if _is_master is not None:
        return _is_master

    # Check if the Master Password already in env variable 
    env = os.getenv("MASTER_PASSWORD")
    if env:
        print(f"{GREEN} Read master password from environment variable. it's insecure!! {RESET}")
        _is_master = env
        return _is_master

    stored = database.get_hash()
    if stored is None:
        raise RuntimeError(f"{RED} Hash word Not Found! first set the master password.{RESET}")
    max_attempt = 3
    for a in range (1 , max_attempt+1):
        attempt = getpass.getpass("Enter Master Password")
        if verify_master_password(attempt , stored):
           print(f"{YELLOW} Master password verified successfully.{RESET}\n")
           os.environ["MASTER_PASSWORD"] = attempt
           _is_master = attempt
           return attempt
        else:
            print(f"{RED}Wrong Password (attemmpt:{a}{RESET}")
    print(f"{DARK_GREEN} Attempts are done {RESET}")
    raise SystemExit

# Add new service or replace existing one
def add_command(args):
    master = master_password_manager()
    encrypted_password = encryption(args.password , master)
    database.store_secrets(args.service , args.username , encrypted_password)
    print(f"{BLUE} Successfully Added Service:{args.service} {RESET}")

# Get a service
def get_command(args):
    master = master_password_manager()
    row = database.get_secrets(args.service)
    if not row:
        print(f"{BLUE} No entry found for serive:{args.service} {RESET}")
        return
    _ , service , username , ciphertext = row
    plaintext = decrypt(ciphertext, master )
    print("Service:", service)
    print("Username:", username)
    print("Password:", plaintext)

# Get list of all services
def get_list(args):
    master = master_password_manager()
    print()
    rows = database.get_all_secrets()
    if not rows:
        print(f"{DARK_GREEN} Nothing To Show {RESET}")
        return
    sid = 1
    if args.show:
        rows.reverse()
        print(f"{'ID':<3} {'SERVICE':<22} {'USERNAME':<22} {'PASSWORD'}")
        print("-"*70)
        for id , service , username , ciphertext in rows:
            try:
                pwd = decrypt(ciphertext, master)
            except Exception as e:
                pwd = f"<Decryption failed!>"
            if username is not None:
                print(f"{sid:<3} {service:22} {username:22} {pwd}")
            else:
                print(f"{sid:<3} {service:22} {"-----":22} {pwd}")
            sid += 1

    else:
        print(f"{'ID':<3} {'SERVICE':<22} {'USERNAME':<22}")
        print("-"*50)
        for id , service , username , _ in rows:
            if username is not None:
                print(f"{sid:<3} {service:22} {username:22}")
            else:
                print(f"{sid:<3} {service:22} {"-----":22}")
            sid += 1


# Delete  service 
def delete_command(args):
    master = master_password_manager()
    database.delete_service(args.service)
    print(f"{YELLOW} Successfully Deleted Service:{args.service} {RESET}")

def main():
    parser = argparse.ArgumentParser(prog="passman" , description="Password Mange CLI")
    subparser = parser.add_subparsers(dest="command" , required=True)

    # Add passowrd...
    add_pars = subparser.add_parser("add" , help="Add a new Password")
    add_pars.add_argument("service",help="service name")
    add_pars.add_argument( "--username", "-u" ,help="Username for the service (optional)")
    add_pars.add_argument("password", help="Password for the service")
    add_pars.set_defaults(func = add_command)

    # Get passowrd...
    get_pars = subparser.add_parser("get" , help="Get a Password")
    get_pars.add_argument("service",help="service name to retrieve")
    get_pars.set_defaults(func=get_command)

    # List Passwords...
    list_pars = subparser.add_parser("list" , help="List of all Services")
    list_pars.add_argument("--show", action="store_true", help="show services")
    list_pars.set_defaults(func=get_list)

    # Delete service....
    del_pars = subparser.add_parser("del" , help="delete a Password")
    del_pars.add_argument("service",help="service name")
    del_pars.set_defaults(func = delete_command)

    args = parser.parse_args()
    check_master_password()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
if __name__ == "__main__":
    main()
