"""
Saithonanen Symmetric Encryption Module
Advanced symmetric encryption with multiple algorithms and security features
"""

import os
import hashlib
import hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import secrets


class AdvancedSymmetricEncryption:
    """
    Advanced symmetric encryption class with multiple algorithms and security features
    """
    
    def __init__(self, algorithm='AES-256-GCM', key_derivation='PBKDF2'):
        """
        Initialize the encryption object
        
        Args:
            algorithm (str): Encryption algorithm ('AES-256-GCM', 'AES-256-CBC', 'ChaCha20-Poly1305')
            key_derivation (str): Key derivation function ('PBKDF2', 'Scrypt')
        """
        self.algorithm = algorithm
        self.key_derivation = key_derivation
        self.backend = default_backend()
        
    def _derive_key(self, password: bytes, salt: bytes) -> bytes:
        """
        Derive encryption key from password using specified KDF
        
        Args:
            password (bytes): Password to derive key from
            salt (bytes): Salt for key derivation
            
        Returns:
            bytes: Derived key
        """
        if self.key_derivation == 'PBKDF2':
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=self.backend
            )
        elif self.key_derivation == 'Scrypt':
            kdf = Scrypt(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                n=2**14,
                r=8,
                p=1,
                backend=self.backend
            )
        else:
            raise ValueError(f"Unsupported key derivation function: {self.key_derivation}")
            
        return kdf.derive(password)
    
    def encrypt(self, plaintext: bytes, password: str) -> dict:
        """
        Encrypt plaintext using the specified algorithm
        
        Args:
            plaintext (bytes): Data to encrypt
            password (str): Password for encryption
            
        Returns:
            dict: Encrypted data with metadata
        """
        # Generate random salt and IV
        salt = secrets.token_bytes(32)
        password_bytes = password.encode('utf-8')
        key = self._derive_key(password_bytes, salt)
        
        if self.algorithm == 'AES-256-GCM':
            iv = secrets.token_bytes(12)  # GCM uses 96-bit IV
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            auth_tag = encryptor.tag
            
            return {
                'algorithm': self.algorithm,
                'key_derivation': self.key_derivation,
                'salt': salt,
                'iv': iv,
                'ciphertext': ciphertext,
                'auth_tag': auth_tag
            }
            
        elif self.algorithm == 'AES-256-CBC':
            iv = secrets.token_bytes(16)  # CBC uses 128-bit IV
            # Add PKCS7 padding
            padded_plaintext = self._add_padding(plaintext, 16)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
            
            # Add HMAC for authentication
            hmac_key = hashlib.sha256(key + b'hmac').digest()
            auth_tag = hmac.new(hmac_key, iv + ciphertext, hashlib.sha256).digest()
            
            return {
                'algorithm': self.algorithm,
                'key_derivation': self.key_derivation,
                'salt': salt,
                'iv': iv,
                'ciphertext': ciphertext,
                'auth_tag': auth_tag
            }
            
        elif self.algorithm == 'ChaCha20-Poly1305':
            nonce = secrets.token_bytes(12)  # ChaCha20 uses 96-bit nonce
            cipher = Cipher(algorithms.ChaCha20(key, nonce), None, backend=self.backend)
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            # ChaCha20-Poly1305 provides built-in authentication
            return {
                'algorithm': self.algorithm,
                'key_derivation': self.key_derivation,
                'salt': salt,
                'nonce': nonce,
                'ciphertext': ciphertext
            }
            
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    
    def decrypt(self, encrypted_data: dict, password: str) -> bytes:
        """
        Decrypt encrypted data
        
        Args:
            encrypted_data (dict): Encrypted data with metadata
            password (str): Password for decryption
            
        Returns:
            bytes: Decrypted plaintext
        """
        algorithm = encrypted_data['algorithm']
        key_derivation = encrypted_data['key_derivation']
        salt = encrypted_data['salt']
        
        password_bytes = password.encode('utf-8')
        
        # Temporarily set the algorithm and key derivation for this decryption
        original_algorithm = self.algorithm
        original_key_derivation = self.key_derivation
        self.algorithm = algorithm
        self.key_derivation = key_derivation
        
        try:
            key = self._derive_key(password_bytes, salt)
            
            if algorithm == 'AES-256-GCM':
                iv = encrypted_data['iv']
                ciphertext = encrypted_data['ciphertext']
                auth_tag = encrypted_data['auth_tag']
                
                cipher = Cipher(algorithms.AES(key), modes.GCM(iv, auth_tag), backend=self.backend)
                decryptor = cipher.decryptor()
                plaintext = decryptor.update(ciphertext) + decryptor.finalize()
                
            elif algorithm == 'AES-256-CBC':
                iv = encrypted_data['iv']
                ciphertext = encrypted_data['ciphertext']
                auth_tag = encrypted_data['auth_tag']
                
                # Verify HMAC
                hmac_key = hashlib.sha256(key + b'hmac').digest()
                expected_auth_tag = hmac.new(hmac_key, iv + ciphertext, hashlib.sha256).digest()
                if not hmac.compare_digest(auth_tag, expected_auth_tag):
                    raise ValueError("Authentication failed")
                
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
                decryptor = cipher.decryptor()
                padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
                plaintext = self._remove_padding(padded_plaintext)
                
            elif algorithm == 'ChaCha20-Poly1305':
                nonce = encrypted_data['nonce']
                ciphertext = encrypted_data['ciphertext']
                
                cipher = Cipher(algorithms.ChaCha20(key, nonce), None, backend=self.backend)
                decryptor = cipher.decryptor()
                plaintext = decryptor.update(ciphertext) + decryptor.finalize()
                
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
                
            return plaintext
            
        finally:
            # Restore original settings
            self.algorithm = original_algorithm
            self.key_derivation = original_key_derivation
    
    def _add_padding(self, data: bytes, block_size: int) -> bytes:
        """Add PKCS7 padding to data"""
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _remove_padding(self, data: bytes) -> bytes:
        """Remove PKCS7 padding from data"""
        padding_length = data[-1]
        return data[:-padding_length]


class MultiLayerEncryption:
    """
    Multi-layer encryption for enhanced security
    """
    
    def __init__(self, layers=3):
        """
        Initialize multi-layer encryption
        
        Args:
            layers (int): Number of encryption layers
        """
        self.layers = layers
        self.algorithms = ['AES-256-GCM', 'ChaCha20-Poly1305', 'AES-256-CBC']
        self.key_derivations = ['PBKDF2', 'Scrypt', 'PBKDF2']
    
    def encrypt(self, plaintext: bytes, password: str) -> dict:
        """
        Apply multiple layers of encryption
        
        Args:
            plaintext (bytes): Data to encrypt
            password (str): Base password
            
        Returns:
            dict: Multi-layer encrypted data
        """
        current_data = plaintext
        encryption_metadata = []
        
        for i in range(self.layers):
            # Use different algorithms and derive different passwords for each layer
            algorithm = self.algorithms[i % len(self.algorithms)]
            key_derivation = self.key_derivations[i % len(self.key_derivations)]
            layer_password = f"{password}_layer_{i}"
            
            encryptor = AdvancedSymmetricEncryption(algorithm, key_derivation)
            encrypted_result = encryptor.encrypt(current_data, layer_password)
            
            encryption_metadata.append({
                'layer': i,
                'metadata': encrypted_result
            })
            
            # Prepare data for next layer
            current_data = self._serialize_encrypted_data(encrypted_result)
        
        return {
            'layers': self.layers,
            'encryption_metadata': encryption_metadata,
            'final_data': current_data
        }
    
    def decrypt(self, multi_layer_data: dict, password: str) -> bytes:
        """
        Decrypt multi-layer encrypted data
        
        Args:
            multi_layer_data (dict): Multi-layer encrypted data
            password (str): Base password
            
        Returns:
            bytes: Decrypted plaintext
        """
        layers = multi_layer_data['layers']
        encryption_metadata = multi_layer_data['encryption_metadata']
        current_data = multi_layer_data['final_data']
        
        # Decrypt in reverse order
        for i in range(layers - 1, -1, -1):
            layer_metadata = encryption_metadata[i]['metadata']
            layer_password = f"{password}_layer_{i}"
            
            algorithm = layer_metadata['algorithm']
            key_derivation = layer_metadata['key_derivation']
            
            decryptor = AdvancedSymmetricEncryption(algorithm, key_derivation)
            
            if i == layers - 1:
                # For the last layer, use the final_data directly
                encrypted_data = layer_metadata
                encrypted_data['ciphertext'] = current_data
            else:
                # For other layers, deserialize the data
                encrypted_data = self._deserialize_encrypted_data(current_data, layer_metadata)
            
            current_data = decryptor.decrypt(encrypted_data, layer_password)
        
        return current_data
    
    def _serialize_encrypted_data(self, encrypted_data: dict) -> bytes:
        """Serialize encrypted data to bytes for next layer"""
        import pickle
        return pickle.dumps(encrypted_data)
    
    def _deserialize_encrypted_data(self, data: bytes, metadata: dict) -> dict:
        """Deserialize encrypted data from bytes"""
        import pickle
        return pickle.loads(data)
