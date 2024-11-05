import getpass
import re
import json
import os
from email_validator import validate_email, EmailNotValidError
import secrets
import crypt
from cryptography.fernet import Fernet

def getName():
    name = input("Enter Full Name: ")
    return name
    
def getEmail():
    while True:
        try:
            email = str(input("Enter Email Address: "))
            validate_email(email)
            return email
        except EmailNotValidError as e:
            print(str(e))
            continue
        else:
            break

def setPassword():

    password = getpass.getpass('Enter Password: ')
    while not validPassword(password):
        print("Password must contain at least one digit, one uppercase letter, at least one lowercase letter, and one special symbol.")
        password = getpass.getpass('Enter Password: ')
    
    passwordMatch = getpass.getpass("Re-enter Password: ")
    if passwordMatch != password:
        print("Passwords do not match.")
        password = setPassword()
    return password
    

def validPassword(password):
    passwordConditions = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    return re.search(re.compile(passwordConditions), password)
    

def registerNewUser():
    if os.path.exists("users.json"):
        os.remove("users.json")
    name = input("Enter Full Name: ")
    email = str(getEmail())
    password = setPassword()
    print("Passwords Match.")
    print("User Registered.*********")

    #Randomized 32-byte (256 bits) salt text string used to
    #salt and hash the user's password
    salt = secrets.token_hex(32)
    salt_hashp = crypt.crypt(password, salt)

    data = {}
    data["Accounts"] = []
    data["Accounts"].append({email: {"name": name, "password": salt_hashp, "salt": salt, "contact_cnt": 0}})
    dumpRegisterToTextFile(data, "users.json")

    
def dumpRegisterToTextFile(data, fileName):

    with open(fileName, "w") as outfile:
        json.dump(data, outfile)

    key = Fernet.generate_key()

    with open('key.key', 'wb') as filekey:
        filekey.write(key)

    encrypt_user_file()

def encrypt_user_file():
    with open('key.key', 'rb') as file_key:
        key = file_key.read()
    fernet = Fernet(key)

    with open('users.json', 'rb') as f:
        users = f.read()
    encrypt = fernet.encrypt(users)

    with open('users.json', 'wb') as enc_f:
        enc_f.write(encrypt)

def decrypt_user_file():
    with open('key.key', 'rb') as f:
        key = f.read()
    fernet = Fernet(key)

    with open('users.json', 'rb') as enc_f:
        encrypt = enc_f.read()
    
    decrypt = fernet.decrypt(encrypt)

    with open ('users.json', 'wb') as dec_f:
        dec_f.write(decrypt)


def login():
    global email
    try:
        email = str(getEmail())

        data = open("./users.json")
        jdata = json.load(data)
        acc_data = jdata["Accounts"]

        # Checking if the entered email in the database
        if email in acc_data[0]:
            password = getpass.getpass('Enter Password: ')
            temp_pass = ""
            salt = ""
        # Parsing the database for the email's salted+hashed password
            for x in jdata["Accounts"]:
                salt = x[email]["salt"]
                temp_pass = x[email]["password"]
            entered_pass = crypt.crypt(password, salt)
        # Checking if the salted+hashed password in the database matches the one the user entered
            if temp_pass == entered_pass:
                data.close()
                return email
            else:
                print("Incorrect password, exiting.")
                #client.send(f'EXIT'.encode('ascii'))
                exit()
        else:
            print("Email doesn't exist, exiting.")
    except:
        print('\nError or keyboard interrupt detected. Exiting.')
        encrypt_user_file()
        exit()
