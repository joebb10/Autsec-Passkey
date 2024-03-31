import random
import string
import time
import hashlib
import base64
from cryptography.fernet import Fernet
import os

def generate_key():
    key = os.urandom(32)
    return base64.urlsafe_b64encode(key).decode()

class PasskeySaas:
    def __init__(self):
        self.key = generate_key()
        self.db = Fernet(self.key)
        self.passkeys = {}

    def generate_passkey(self, username, email):
       
        passkey = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=16))

       
        salt = hashlib.sha256(os.urandom(64)).hexdigest()

        
        hashed_passkey = hashlib.sha256((passkey + salt).encode('utf-8')).hexdigest()

        
        encrypted_passkey = self.db.encrypt((passkey + salt).encode('utf-8'))

        
        self.passkeys[username] = {
            "email": email,
            "encrypted_passkey": encrypted_passkey,
            "expiration_time": time.time() + 60 * 60 * 1000, # 1 hour
            "used": False,
            "devices": []
        }

        return passkey

    def get_passkey(self, username):
        if username in self.passkeys and self.passkeys[username]["expiration_time"] > time.time():
            return self.passkeys[username]
        else:
            return None

    def use_passkey(self, username, device_id):
        passkey_record = self.get_passkey(username)
        if passkey_record is not None and not passkey_record["used"] and device_id in passkey_record["devices"]:
            passkey_record["used"] = True
            return True
        else:
            return False

    def login(self, username, device_id):
        passkey_record = self.get_passkey(username)
        if passkey_record is not None and not passkey_record["used"] and device_id in passkey_record["devices"]:
            return True
        else:
            return False

    def register_device(self, username, device_id):
        passkey_record = self.get_passkey(username)
        if passkey_record is not None:
            passkey_record["devices"].append(device_id)
            return True
        else:
            return False

if __name__ == '__main__':
    passkey_saas = PasskeySaas()

    
    username = input('Enter your username: ')
    email = input('Enter your email: ')

    
    passkey = passkey_saas.generate_passkey(username, email)

   
    device_id = input('Enter your device ID: ')

    
    passkey_saas.register_device(username, device_id)

    
    login_successful = passkey_saas.login(username, device_id)

    if login_successful:
        print('You have logged in successfully!')
    else:
        print('Login failed.')
