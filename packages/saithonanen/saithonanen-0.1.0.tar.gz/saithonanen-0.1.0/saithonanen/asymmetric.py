"""
Saithonanen Asymmetric Encryption Module
Advanced asymmetric encryption with RSA, ECC, and post-quantum algorithms
"""

import os
import secrets
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature, decode_dss_signature


class AdvancedAsymmetricEncryption:
    """
    Advanced asymmetric encryption with multiple algorithms
    """
    
    def __init__(self, algorithm='RSA-4096'):
        """
        Initialize asymmetric encryption
        
        Args:
            algorithm (str): Algorithm type ('RSA-2048', 'RSA-4096', 'ECC-P256', 'ECC-P384', 'ECC-P521')
        """
        self.algorithm = algorithm
        self.backend = default_backend()
        
    def generate_key_pair(self):
        """
        Generate a new key pair
        
        Returns:
            tuple: (private_key, public_key)
        """
        if self.algorithm.startswith('RSA'):
            key_size = int(self.algorithm.split('-')[1])
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=self.backend
            )
            public_key = private_key.public_key()
            
        elif self.algorithm.startswith('ECC'):
            curve_name = self.algorithm.split('-')[1]
            if curve_name == 'P256':
                curve = ec.SECP256R1()
            elif curve_name == 'P384':
                curve = ec.SECP384R1()
            elif curve_name == 'P521':
                curve = ec.SECP521R1()
            else:
                raise ValueError(f"Unsupported ECC curve: {curve_name}")
                
            private_key = ec.generate_private_key(curve, self.backend)
            public_key = private_key.public_key()
            
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
            
        return private_key, public_key
    
    def encrypt(self, plaintext: bytes, public_key) -> bytes:
        """
        Encrypt data using public key
        
        Args:
            plaintext (bytes): Data to encrypt
            public_key: Public key for encryption
            
        Returns:
            bytes: Encrypted data
        """
        if self.algorithm.startswith('RSA'):
            # RSA encryption with OAEP padding
            ciphertext = public_key.encrypt(
                plaintext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return ciphertext
            
        elif self.algorithm.startswith('ECC'):
            # ECC doesn't directly encrypt data, use hybrid encryption
            # Generate ephemeral key pair
            ephemeral_private_key = ec.generate_private_key(
                public_key.curve, self.backend
            )
            ephemeral_public_key = ephemeral_private_key.public_key()
            
            # Perform ECDH
            shared_key = ephemeral_private_key.exchange(
                ec.ECDH(), public_key
            )
            
            # Derive encryption key from shared secret
            from cryptography.hazmat.primitives.kdf.hkdf import HKDF
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'encryption',
                backend=self.backend
            ).derive(shared_key)
            
            # Encrypt using AES-GCM
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            iv = secrets.token_bytes(12)
            cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            # Serialize ephemeral public key
            ephemeral_public_bytes = ephemeral_public_key.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )
            
            # Return combined data
            return ephemeral_public_bytes + iv + encryptor.tag + ciphertext
            
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    
    def decrypt(self, ciphertext: bytes, private_key) -> bytes:
        """
        Decrypt data using private key
        
        Args:
            ciphertext (bytes): Encrypted data
            private_key: Private key for decryption
            
        Returns:
            bytes: Decrypted plaintext
        """
        if self.algorithm.startswith('RSA'):
            # RSA decryption with OAEP padding
            plaintext = private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return plaintext
            
        elif self.algorithm.startswith('ECC'):
            # Extract components from ciphertext
            curve = private_key.curve
            if isinstance(curve, ec.SECP256R1):
                point_size = 65  # Uncompressed point for P-256
            elif isinstance(curve, ec.SECP384R1):
                point_size = 97  # Uncompressed point for P-384
            elif isinstance(curve, ec.SECP521R1):
                point_size = 133  # Uncompressed point for P-521
            else:
                raise ValueError("Unsupported curve")
                
            ephemeral_public_bytes = ciphertext[:point_size]
            iv = ciphertext[point_size:point_size + 12]
            auth_tag = ciphertext[point_size + 12:point_size + 12 + 16]
            encrypted_data = ciphertext[point_size + 12 + 16:]
            
            # Reconstruct ephemeral public key
            ephemeral_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                curve, ephemeral_public_bytes
            )
            
            # Perform ECDH
            shared_key = private_key.exchange(ec.ECDH(), ephemeral_public_key)
            
            # Derive decryption key
            from cryptography.hazmat.primitives.kdf.hkdf import HKDF
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'encryption',
                backend=self.backend
            ).derive(shared_key)
            
            # Decrypt using AES-GCM
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv, auth_tag), backend=self.backend)
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(encrypted_data) + decryptor.finalize()
            
            return plaintext
            
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    
    def sign(self, message: bytes, private_key) -> bytes:
        """
        Sign a message using private key
        
        Args:
            message (bytes): Message to sign
            private_key: Private key for signing
            
        Returns:
            bytes: Digital signature
        """
        if self.algorithm.startswith('RSA'):
            signature = private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature
            
        elif self.algorithm.startswith('ECC'):
            signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
            return signature
            
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    
    def verify(self, message: bytes, signature: bytes, public_key) -> bool:
        """
        Verify a digital signature
        
        Args:
            message (bytes): Original message
            signature (bytes): Digital signature
            public_key: Public key for verification
            
        Returns:
            bool: True if signature is valid
        """
        try:
            if self.algorithm.startswith('RSA'):
                public_key.verify(
                    signature,
                    message,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True
                
            elif self.algorithm.startswith('ECC'):
                public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
                return True
                
            else:
                raise ValueError(f"Unsupported algorithm: {self.algorithm}")
                
        except Exception:
            return False
    
    def serialize_private_key(self, private_key, password: str = None) -> bytes:
        """
        Serialize private key to PEM format
        
        Args:
            private_key: Private key to serialize
            password (str): Optional password for encryption
            
        Returns:
            bytes: Serialized private key
        """
        encryption_algorithm = serialization.NoEncryption()
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
            
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
    
    def serialize_public_key(self, public_key) -> bytes:
        """
        Serialize public key to PEM format
        
        Args:
            public_key: Public key to serialize
            
        Returns:
            bytes: Serialized public key
        """
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def load_private_key(self, key_data: bytes, password: str = None):
        """
        Load private key from PEM data
        
        Args:
            key_data (bytes): PEM encoded private key
            password (str): Optional password for decryption
            
        Returns:
            Private key object
        """
        password_bytes = password.encode() if password else None
        return serialization.load_pem_private_key(
            key_data, password=password_bytes, backend=self.backend
        )
    
    def load_public_key(self, key_data: bytes):
        """
        Load public key from PEM data
        
        Args:
            key_data (bytes): PEM encoded public key
            
        Returns:
            Public key object
        """
        return serialization.load_pem_public_key(key_data, backend=self.backend)


class HybridEncryption:
    """
    Hybrid encryption combining asymmetric and symmetric encryption
    """
    
    def __init__(self, asymmetric_algorithm='RSA-4096', symmetric_algorithm='AES-256-GCM'):
        """
        Initialize hybrid encryption
        
        Args:
            asymmetric_algorithm (str): Asymmetric algorithm for key exchange
            symmetric_algorithm (str): Symmetric algorithm for data encryption
        """
        self.asymmetric = AdvancedAsymmetricEncryption(asymmetric_algorithm)
        from .symmetric import AdvancedSymmetricEncryption
        self.symmetric = AdvancedSymmetricEncryption(symmetric_algorithm)
    
    def encrypt(self, plaintext: bytes, public_key) -> dict:
        """
        Encrypt data using hybrid encryption
        
        Args:
            plaintext (bytes): Data to encrypt
            public_key: Public key for key encryption
            
        Returns:
            dict: Hybrid encrypted data
        """
        # Generate random symmetric key
        symmetric_key = secrets.token_bytes(32)
        symmetric_password = symmetric_key.hex()
        
        # Encrypt data with symmetric encryption
        encrypted_data = self.symmetric.encrypt(plaintext, symmetric_password)
        
        # Encrypt symmetric key with asymmetric encryption
        encrypted_key = self.asymmetric.encrypt(symmetric_key, public_key)
        
        return {
            'encrypted_key': encrypted_key,
            'encrypted_data': encrypted_data,
            'asymmetric_algorithm': self.asymmetric.algorithm,
            'symmetric_algorithm': self.symmetric.algorithm
        }
    
    def decrypt(self, hybrid_data: dict, private_key) -> bytes:
        """
        Decrypt hybrid encrypted data
        
        Args:
            hybrid_data (dict): Hybrid encrypted data
            private_key: Private key for key decryption
            
        Returns:
            bytes: Decrypted plaintext
        """
        # Decrypt symmetric key
        encrypted_key = hybrid_data['encrypted_key']
        symmetric_key = self.asymmetric.decrypt(encrypted_key, private_key)
        symmetric_password = symmetric_key.hex()
        
        # Decrypt data with symmetric encryption
        encrypted_data = hybrid_data['encrypted_data']
        plaintext = self.symmetric.decrypt(encrypted_data, symmetric_password)
        
        return plaintext
