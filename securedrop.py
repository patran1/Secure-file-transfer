import json
from os import urandom
import base64
import os
import socket
import sys
import ssl
import getpass
import re
import crypt
import threading
from cryptography.fernet import Fernet
import pickle
from login_utils import getEmail, getName, login, registerNewUser, encrypt_user_file, decrypt_user_file


# Creating the socket connection
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Create a context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

# Load the server's CA
context.load_verify_locations("/home/jhua/comp2300_security/secure_drop/cert.pem")

# Wrapping the socket
client = context.wrap_socket(client, server_hostname="localhost")

host = '127.0.0.1' # localhost
port = 55558


def SDShell():

    # Connect and send data on the new secured socket connection
    try:
        client.connect((host, port))
    except:
        print('\nAn error occurred while connecting. Exiting...')
        encrypt_user_file()
        exit()

    send_login(email)

    print("Welcome to SecureDrop.\n")
    print("Type \"help\" For Commands.\n")

    try:
        while True:
            SDInput = input("secure_drop> ")
            
            if SDInput == "help":
                SDHelp()
                
            elif SDInput == "add":
                SDAdd()
                
            elif SDInput == "list":
                SDList()
                
            elif SDInput == "send":
                SDSend()
                
            elif SDInput == "exit":
                exit_server()
            else:
                print("Command not recognized.")
    except KeyboardInterrupt:
        print('\nKeyboard interrupt detected. Exiting.')
        encrypt_user_file()
        exit()

def SDHelp():
        print('"add"  -> Add a new contact\n \
            "list" -> List all online contacts\n \
            "send" -> Transfer file to contact\n \
            "exit" -> Exit SecureDrop')

def SDAdd():

    # Loading user info for parsing
    f = open("./users.json", "r+")
    data = json.load(f)
    acc_data = data["Accounts"]
    user_email = list(data["Accounts"][0].keys())[0]
    user_info = data["Accounts"][0][user_email]

    # Retrieving the number of contacts of user
    contact_cnt = data["Accounts"][0][user_email]['contact_cnt']
    
    # If the user has never added contact, add a new field called 'Contacts'
    try:
        if contact_cnt == 0:
            data["Accounts"][0][user_email]['contact_cnt'] += 1
            name = getName()
            email = getEmail()

            user_info["Contacts"] = [{"email": email, "name": name}]
            data["Accounts"][0][user_email]  = user_info
            f.seek(0)
            json.dump(data, f)
            f.close()
            print("Contact successfully added.")
            
        # Otherwise just append the new contact normally
        else:
            data["Accounts"][0][user_email]['contact_cnt'] += 1

            name = getName()
            email = getEmail()

            data["Accounts"][0][user_email]["Contacts"].append({"email": email, "name": name})
            f.seek(0)
            json.dump(data, f)
            f.close()
            print("Contact successfully added.")
    except:
        print('\nAn error occurred while adding a contact. Exiting.')
        encrypt_user_file()
        exit()

#
def SDList():
    with open ("./users.json", "r") as f:
        jdata = json.load(f)
    contact_cnt = jdata["Accounts"][0][email]['contact_cnt']
    if contact_cnt == 0:
        print("You do not have any contacts added! Use 'add' to add a new contact.")
    else:
        # Serialize the data using pickle and send it to the server
        client.send(f'LIST'.encode('ascii'))
        data = pickle.dumps(jdata["Accounts"][0][email]["Contacts"])
        client.send(data)
        # Needs a more elegant way to stop receiving contact data from
        # server when finished. Set a sockettimeout maybe?
        while True:
            list = client.recv(1024)
            print(list.decode('ascii'))
            if not list:
                break
            if list.decode('ascii') ==  "stop":
                break

def SDSend():
    contact_email = input("Enter the contact's email to send the file: ")
    
    file_path = input("Enter the file path to send: ")
    if not os.path.isfile(file_path):
        print("File not found. Please check the path and try again.")
        return

    try:
        # Notify server of send request
        client.send("SEND".encode('ascii'))
        
        # Send recipient's email
        client.send(contact_email.encode('ascii'))

        # Send file data
        with open(file_path, "rb") as file:
            file_data = file.read()
            client.sendall(pickle.dumps(file_data))  # Send file data in chunks
            print("File sent successfully.")
            
    except Exception as e:
        print("Error sending file:", e)

def exit_server():
    client.send(f'EXIT'.encode('ascii'))
    # msg = client.recv(1024)
    # print(msg.decode('utf-8'))
    client.close()
    encrypt_user_file()
    exit()

# Sending login details (email) to the server so it can
# append it to the list of online users.
def send_login(email):
    while True:
            message = client.recv(1024).decode('ascii')
            if message == 'CONTACT':
                client.send(email.encode('ascii'))
                return
            else:
                return

def main():

    global contacts
    global new_contact
    global email
    new_contact = {}
    contacts = []
    # The login module is automatically initiated once a user is registered on
    # a client and the secure drop shell is launched.
    if os.path.isfile("./users.json") and os.path.getsize("./users.json") > 0:
        decrypt_user_file()
        email = login()

    else:
        print("\nNo users are registered with this client.")
        resp1 = input("Do you want to register a new user (y/n)?: ")
        if resp1 == "y":
            registerNewUser()
            print('Exiting SecureDrop.')
            exit()
        elif resp1 == "n":
            exit()

    

main()
SDShell()
