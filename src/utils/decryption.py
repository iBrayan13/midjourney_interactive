import json
import traceback
from typing import Dict, List, Union

from cryptography.fernet import Fernet


def generate_key() -> str:
    """
    Generate a secure encryption key.
    
    Returns:
        A base64-encoded key (str).
    """
    return Fernet.generate_key().decode('utf-8')

def encrypt_data(data: Union[List, Dict], key: str) -> str:
    """
    Encrypt data using Fernet (AES-128-CBC with HMAC-SHA256).
    
    Args:
        data: Data to encrypt (list or dictionary).
        key: Base64-encoded encryption key.
    
    Returns:
        Base64-encoded encrypted string.
    """
    # Convert data to JSON
    json_data = json.dumps(data).encode('utf-8')
    
    # Encrypt the data
    fernet = Fernet(key.encode('utf-8'))
    encrypted_data = fernet.encrypt(json_data)
    
    return encrypted_data.decode('utf-8')

def decrypt_data(encrypted_str: str, key: str) -> Union[List, Dict]:
    """
    Decrypt data that was encrypted using Fernet.
    
    Args:
        encrypted_str: Base64-encoded encrypted string.
        key: Base64-encoded encryption key.
    
    Returns:
        Decrypted data (list or dictionary).
    """
    try:

        # Decrypt the data
        fernet = Fernet(key.encode('utf-8'))
        decrypted_data = fernet.decrypt(encrypted_str.encode('utf-8'))
        
        # Parse JSON
        data = json.loads(decrypted_data.decode('utf-8'))
        #print(f"Decrypted data({type(data)}): {data}")
        return data
    except Exception as e:
        print(f"Error decrypting data {e}: {traceback.format_exc()}")
        return None