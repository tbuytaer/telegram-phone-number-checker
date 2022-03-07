#!/usr/local/bin/python3
from telethon import TelegramClient, errors, events, sync
from telethon.tl.types import InputPhoneContact
from telethon import functions, types
from dotenv import load_dotenv
import argparse
import os
from getpass import getpass
import json

load_dotenv("../.env")

result = {}

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

def get_names(phone_number):    
    try:
        contact = InputPhoneContact(client_id = 0, phone = phone_number, first_name="", last_name="")
        contacts = client(functions.contacts.ImportContactsRequest([contact]))
        username = contacts.to_dict()['users'][0]['username']
        userid = contacts.to_dict()['users'][0]['id']
        if not username:
            #print("*"*5 + f' Response detected, but no user name returned by the API for the number: {phone_number} ' + "*"*5)
            del_usr = client(functions.contacts.DeleteContactsRequest(id=[userid]))
            return {
                "phone":phone_number,
                "status":"phone-found-no-username",
            }
        else:
            del_usr = client(functions.contacts.DeleteContactsRequest(id=[username]))
            return {
                "phone":phone_number,
                "status":"phone-found",
                "username":username
            }
    except IndexError as e:
        #print(f'ERROR: there was no response for the phone number: {phone_number}')
        return {
            "phone":phone_number,
            "status":"phone-not-found",
        }
    except TypeError as e:
        return f"TypeError: {e}. --> The error might have occured due to the inability to delete the {phone_number} from the contact list."
    except:
        raise


def user_validator(phonenumber):
    '''
    The function uses the get_api_response function to first check if the user exists and if it does, then it returns the first user name and the last user name.
    '''
    #print("valid: " + phonenumber)
    if not (len(phonenumber) > 6):
        phonenumber = input("Phone number: ")
    try:
        return get_names(phonenumber)
    except:
        raise
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check to see if a phone number is a valid Telegram account')
    parser.add_argument('--phonenumber', dest='phonenumber', action='store', help='Enter the phone number to check')
    args = parser.parse_args()

    client = TelegramClient(PHONE_NUMBER, API_ID, API_HASH)
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(PHONE_NUMBER)
        try:
            client.sign_in(PHONE_NUMBER, input('Enter the code (sent on telegram): '))
        except errors.SessionPasswordNeededError:
            pw = getpass('Two-Step Verification enabled. Please enter your account password: ')
            client.sign_in(password=pw)
    
    # Output as JSON
    result = json.dumps(user_validator(args.phonenumber))
    print(result)
