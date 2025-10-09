from Crypto.Cipher import AES
import binascii
import requests
import re

def decrypt_slowAES(encrypted_hex, key_hex, iv_hex):
            encrypted_bytes = binascii.unhexlify(encrypted_hex)
            key_bytes = binascii.unhexlify(key_hex)
            iv_bytes = binascii.unhexlify(iv_hex)
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
            decrypted_bytes = cipher.decrypt(encrypted_bytes)
            decrypted_cookie_hex = binascii.hexlify(decrypted_bytes).decode()
            return decrypted_cookie_hex
            
class bypass:
    @staticmethod
    def get(url, headers= {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}, cookies=None, **kwargs):    
        r1 = requests.get(url, headers=headers, **kwargs)
        html_content = r1.text    
        a_match = re.search(r'var a=toNumbers\("([a-fA-F0-9]+)"\)', html_content)
        b_match = re.search(r'b=toNumbers\("([a-fA-F0-9]+)"\)', html_content)
        c_match = re.search(r'c=toNumbers\("([a-fA-F0-9]+)"\)', html_content)
        url_match = re.search(r'location\.href="([^"]+)"', html_content)
        aes_key = a_match.group(1) if a_match else None
        aes_iv = b_match.group(1) if b_match else None
        encrypted_data = c_match.group(1) if c_match else None
        redirect_url = url_match.group(1) if url_match else None        
        decrypted_value = decrypt_slowAES(encrypted_data, aes_key, aes_iv)
        payload = {"__test": decrypted_value}
        if cookies:
            payload.update(cookies)
            
        r2 = requests.get(redirect_url, headers=headers, cookies=payload, **kwargs)
        return r2
    
    @staticmethod    
    def post(url, headers= {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}, cookies=None, **kwargs):    
        r1 = requests.get(url, headers=headers, **kwargs)
        html_content = r1.text    
        a_match = re.search(r'var a=toNumbers\("([a-fA-F0-9]+)"\)', html_content)
        b_match = re.search(r'b=toNumbers\("([a-fA-F0-9]+)"\)', html_content)
        c_match = re.search(r'c=toNumbers\("([a-fA-F0-9]+)"\)', html_content)
        url_match = re.search(r'location\.href="([^"]+)"', html_content)
        aes_key = a_match.group(1) if a_match else None
        aes_iv = b_match.group(1) if b_match else None
        encrypted_data = c_match.group(1) if c_match else None
        redirect_url = url_match.group(1) if url_match else None        
        decrypted_value = decrypt_slowAES(encrypted_data, aes_key, aes_iv)
        payload = {"__test": decrypted_value}
        if cookies:
            payload.update(cookies)
        
        r2 = requests.post(redirect_url, headers=headers, cookies=payload, **kwargs)
        return r2
        