"""
Saithonanen Security Module
Advanced security features including steganography, anti-forensics, and secure deletion
"""

import os
import secrets
import hashlib
import hmac
import time
import threading
from typing import List, Dict, Any, Optional
from PIL import Image
import numpy as np


class Steganography:
    """
    Advanced steganography for hiding encrypted data in images
    """
    
    def __init__(self):
        """Initialize steganography module"""
        self.supported_formats = ['PNG', 'BMP', 'TIFF']
    
    def hide_data_in_image(self, image_path: str, secret_data: bytes, 
                          output_path: str, password: str = None) -> bool:
        """
        Hide encrypted data in an image using LSB steganography
        
        Args:
            image_path (str): Path to cover image
            secret_data (bytes): Data to hide
            output_path (str): Path for output image
            password (str): Optional password for additional encryption
            
        Returns:
            bool: True if successful
        """
        try:
            # Load image
            image = Image.open(image_path)
            if image.format not in self.supported_formats:
                image = image.convert('RGB')
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Encrypt data if password provided
            if password:
                from .symmetric import AdvancedSymmetricEncryption
                encryptor = AdvancedSymmetricEncryption()
                encrypted_result = encryptor.encrypt(secret_data, password)
                import pickle
                secret_data = pickle.dumps(encrypted_result)
            
            # Add length header
            data_length = len(secret_data)
            length_bytes = data_length.to_bytes(4, 'big')
            full_data = length_bytes + secret_data
            
            # Convert data to binary
            binary_data = ''.join(format(byte, '08b') for byte in full_data)
            
            # Check if image can hold the data
            total_pixels = img_array.size
            if len(binary_data) > total_pixels:
                raise ValueError("Image too small to hold the data")
            
            # Hide data in LSBs
            flat_array = img_array.flatten()
            for i, bit in enumerate(binary_data):
                flat_array[i] = (flat_array[i] & 0xFE) | int(bit)
            
            # Reshape and save
            stego_array = flat_array.reshape(img_array.shape)
            stego_image = Image.fromarray(stego_array.astype(np.uint8))
            stego_image.save(output_path)
            
            return True
            
        except Exception as e:
            print(f"Steganography error: {e}")
            return False
    
    def extract_data_from_image(self, image_path: str, password: str = None) -> Optional[bytes]:
        """
        Extract hidden data from an image
        
        Args:
            image_path (str): Path to stego image
            password (str): Optional password for decryption
            
        Returns:
            Optional[bytes]: Extracted data or None if failed
        """
        try:
            # Load image
            image = Image.open(image_path)
            img_array = np.array(image)
            
            # Extract LSBs
            flat_array = img_array.flatten()
            
            # Extract length first (4 bytes = 32 bits)
            length_bits = ''.join(str(pixel & 1) for pixel in flat_array[:32])
            data_length = int(length_bits, 2)
            
            if data_length <= 0 or data_length > len(flat_array) // 8:
                return None
            
            # Extract data
            total_bits = (data_length + 4) * 8  # +4 for length header
            data_bits = ''.join(str(pixel & 1) for pixel in flat_array[32:total_bits])
            
            # Convert to bytes
            extracted_bytes = bytearray()
            for i in range(0, len(data_bits), 8):
                byte_bits = data_bits[i:i+8]
                if len(byte_bits) == 8:
                    extracted_bytes.append(int(byte_bits, 2))
            
            secret_data = bytes(extracted_bytes)
            
            # Decrypt if password provided
            if password:
                import pickle
                from .symmetric import AdvancedSymmetricEncryption
                encrypted_result = pickle.loads(secret_data)
                decryptor = AdvancedSymmetricEncryption()
                secret_data = decryptor.decrypt(encrypted_result, password)
            
            return secret_data
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return None


class SecureDelete:
    """
    Secure file deletion with multiple overwrite passes
    """
    
    def __init__(self):
        """Initialize secure delete module"""
        self.overwrite_patterns = [
            b'\x00',  # Zeros
            b'\xFF',  # Ones
            b'\xAA',  # 10101010
            b'\x55',  # 01010101
        ]
    
    def secure_delete_file(self, file_path: str, passes: int = 7) -> bool:
        """
        Securely delete a file with multiple overwrite passes
        
        Args:
            file_path (str): Path to file to delete
            passes (int): Number of overwrite passes
            
        Returns:
            bool: True if successful
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'r+b') as f:
                for pass_num in range(passes):
                    # Choose overwrite pattern
                    if pass_num < len(self.overwrite_patterns):
                        pattern = self.overwrite_patterns[pass_num]
                    else:
                        # Random data for additional passes
                        pattern = secrets.token_bytes(1)
                    
                    # Overwrite file
                    f.seek(0)
                    for _ in range(file_size):
                        f.write(pattern)
                    f.flush()
                    os.fsync(f.fileno())
            
            # Remove file
            os.remove(file_path)
            return True
            
        except Exception as e:
            print(f"Secure delete error: {e}")
            return False
    
    def secure_delete_memory(self, data: bytearray) -> None:
        """
        Securely clear sensitive data from memory
        
        Args:
            data (bytearray): Data to clear
        """
        if isinstance(data, bytearray):
            # Overwrite with random data
            for i in range(len(data)):
                data[i] = secrets.randbits(8)
            # Overwrite with zeros
            for i in range(len(data)):
                data[i] = 0


class AntiForensics:
    """
    Anti-forensics features to protect against analysis
    """
    
    def __init__(self):
        """Initialize anti-forensics module"""
        self.dummy_operations = []
    
    def add_timing_noise(self, min_delay: float = 0.001, max_delay: float = 0.01) -> None:
        """
        Add random timing delays to operations
        
        Args:
            min_delay (float): Minimum delay in seconds
            max_delay (float): Maximum delay in seconds
        """
        delay = secrets.SystemRandom().uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def create_dummy_operations(self, count: int = 10) -> None:
        """
        Create dummy cryptographic operations to confuse timing analysis
        
        Args:
            count (int): Number of dummy operations
        """
        for _ in range(count):
            # Dummy hash operations
            dummy_data = secrets.token_bytes(secrets.randbelow(1024) + 1)
            hashlib.sha256(dummy_data).digest()
            
            # Add timing noise
            self.add_timing_noise()
    
    def obfuscate_memory_access(self, data: bytes, access_pattern: str = 'random') -> bytes:
        """
        Obfuscate memory access patterns
        
        Args:
            data (bytes): Data to access
            access_pattern (str): Access pattern ('random', 'reverse')
            
        Returns:
            bytes: Data (unchanged, but accessed in obfuscated pattern)
        """
        data_array = bytearray(data)
        
        if access_pattern == 'random':
            # Random access pattern
            indices = list(range(len(data_array)))
            secrets.SystemRandom().shuffle(indices)
            for i in indices:
                _ = data_array[i]  # Dummy read
                
        elif access_pattern == 'reverse':
            # Reverse access pattern
            for i in range(len(data_array) - 1, -1, -1):
                _ = data_array[i]  # Dummy read
        
        return bytes(data_array)


class IntegrityProtection:
    """
    Data integrity protection with checksums and digital signatures
    """
    
    def __init__(self):
        """Initialize integrity protection"""
        self.hash_algorithms = {
            'SHA256': hashlib.sha256,
            'SHA512': hashlib.sha512,
            'SHA3-256': hashlib.sha3_256,
            'BLAKE2b': hashlib.blake2b
        }
    
    def create_checksum(self, data: bytes, algorithm: str = 'SHA256') -> str:
        """
        Create checksum for data integrity
        
        Args:
            data (bytes): Data to checksum
            algorithm (str): Hash algorithm to use
            
        Returns:
            str: Hexadecimal checksum
        """
        if algorithm not in self.hash_algorithms:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        hash_func = self.hash_algorithms[algorithm]()
        hash_func.update(data)
        return hash_func.hexdigest()
    
    def verify_checksum(self, data: bytes, expected_checksum: str, 
                       algorithm: str = 'SHA256') -> bool:
        """
        Verify data integrity using checksum
        
        Args:
            data (bytes): Data to verify
            expected_checksum (str): Expected checksum
            algorithm (str): Hash algorithm used
            
        Returns:
            bool: True if checksum matches
        """
        actual_checksum = self.create_checksum(data, algorithm)
        return hmac.compare_digest(actual_checksum, expected_checksum)
    
    def create_hmac(self, data: bytes, key: bytes, algorithm: str = 'SHA256') -> str:
        """
        Create HMAC for authenticated integrity
        
        Args:
            data (bytes): Data to authenticate
            key (bytes): Secret key
            algorithm (str): Hash algorithm to use
            
        Returns:
            str: Hexadecimal HMAC
        """
        if algorithm not in self.hash_algorithms:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        hash_func = self.hash_algorithms[algorithm]
        mac = hmac.new(key, data, hash_func)
        return mac.hexdigest()
    
    def verify_hmac(self, data: bytes, key: bytes, expected_hmac: str,
                   algorithm: str = 'SHA256') -> bool:
        """
        Verify HMAC for authenticated integrity
        
        Args:
            data (bytes): Data to verify
            key (bytes): Secret key
            expected_hmac (str): Expected HMAC
            algorithm (str): Hash algorithm used
            
        Returns:
            bool: True if HMAC is valid
        """
        actual_hmac = self.create_hmac(data, key, algorithm)
        return hmac.compare_digest(actual_hmac, expected_hmac)


class SecureRandom:
    """
    Cryptographically secure random number generation
    """
    
    def __init__(self):
        """Initialize secure random generator"""
        self.system_random = secrets.SystemRandom()
    
    def generate_bytes(self, length: int) -> bytes:
        """
        Generate cryptographically secure random bytes
        
        Args:
            length (int): Number of bytes to generate
            
        Returns:
            bytes: Random bytes
        """
        return secrets.token_bytes(length)
    
    def generate_password(self, length: int = 32, 
                         include_symbols: bool = True) -> str:
        """
        Generate cryptographically secure password
        
        Args:
            length (int): Password length
            include_symbols (bool): Include special symbols
            
        Returns:
            str: Generated password
        """
        import string
        
        chars = string.ascii_letters + string.digits
        if include_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        return ''.join(self.system_random.choice(chars) for _ in range(length))
    
    def generate_salt(self, length: int = 32) -> bytes:
        """
        Generate cryptographic salt
        
        Args:
            length (int): Salt length in bytes
            
        Returns:
            bytes: Random salt
        """
        return self.generate_bytes(length)


class SecurityAudit:
    """
    Security auditing and logging functionality
    """
    
    def __init__(self, log_file: str = None):
        """
        Initialize security audit
        
        Args:
            log_file (str): Optional log file path
        """
        self.log_file = log_file
        self.audit_log = []
        self.lock = threading.Lock()
    
    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log security event
        
        Args:
            event_type (str): Type of security event
            details (Dict): Event details
        """
        with self.lock:
            timestamp = time.time()
            log_entry = {
                'timestamp': timestamp,
                'event_type': event_type,
                'details': details,
                'iso_time': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp))
            }
            
            self.audit_log.append(log_entry)
            
            # Write to file if specified
            if self.log_file:
                try:
                    with open(self.log_file, 'a') as f:
                        import json
                        f.write(json.dumps(log_entry) + '\n')
                except Exception as e:
                    print(f"Logging error: {e}")
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """
        Get audit log entries
        
        Returns:
            List[Dict]: Audit log entries
        """
        with self.lock:
            return self.audit_log.copy()
    
    def clear_audit_log(self) -> None:
        """Clear audit log"""
        with self.lock:
            self.audit_log.clear()


class AdvancedSecurity:
    """
    Combined advanced security features
    """
    
    def __init__(self, enable_audit: bool = True):
        """
        Initialize advanced security
        
        Args:
            enable_audit (bool): Enable security auditing
        """
        self.steganography = Steganography()
        self.secure_delete = SecureDelete()
        self.anti_forensics = AntiForensics()
        self.integrity = IntegrityProtection()
        self.secure_random = SecureRandom()
        
        self.audit = SecurityAudit() if enable_audit else None
        
    def secure_encrypt_and_hide(self, plaintext: bytes, password: str,
                               cover_image_path: str, output_image_path: str) -> bool:
        """
        Encrypt data and hide in image with full security features
        
        Args:
            plaintext (bytes): Data to encrypt and hide
            password (str): Encryption password
            cover_image_path (str): Cover image path
            output_image_path (str): Output stego image path
            
        Returns:
            bool: True if successful
        """
        try:
            # Log operation
            if self.audit:
                self.audit.log_event('encrypt_and_hide', {
                    'data_size': len(plaintext),
                    'cover_image': cover_image_path,
                    'output_image': output_image_path
                })
            
            # Add anti-forensics measures
            self.anti_forensics.create_dummy_operations()
            self.anti_forensics.add_timing_noise()
            
            # Encrypt data
            from .symmetric import AdvancedSymmetricEncryption
            encryptor = AdvancedSymmetricEncryption('AES-256-GCM', 'Scrypt')
            encrypted_result = encryptor.encrypt(plaintext, password)
            
            # Add integrity protection
            checksum = self.integrity.create_checksum(plaintext, 'SHA3-256')
            encrypted_result['integrity_checksum'] = checksum
            
            # Serialize encrypted data
            import pickle
            serialized_data = pickle.dumps(encrypted_result)
            
            # Hide in image
            success = self.steganography.hide_data_in_image(
                cover_image_path, serialized_data, output_image_path
            )
            
            # Add more timing noise
            self.anti_forensics.add_timing_noise()
            
            return success
            
        except Exception as e:
            if self.audit:
                self.audit.log_event('encrypt_and_hide_error', {'error': str(e)})
            return False
    
    def secure_extract_and_decrypt(self, stego_image_path: str, 
                                  password: str) -> Optional[bytes]:
        """
        Extract and decrypt data from stego image with verification
        
        Args:
            stego_image_path (str): Stego image path
            password (str): Decryption password
            
        Returns:
            Optional[bytes]: Decrypted data or None if failed
        """
        try:
            # Log operation
            if self.audit:
                self.audit.log_event('extract_and_decrypt', {
                    'stego_image': stego_image_path
                })
            
            # Add anti-forensics measures
            self.anti_forensics.create_dummy_operations()
            self.anti_forensics.add_timing_noise()
            
            # Extract data from image
            serialized_data = self.steganography.extract_data_from_image(stego_image_path)
            if not serialized_data:
                return None
            
            # Deserialize
            import pickle
            encrypted_result = pickle.loads(serialized_data)
            
            # Decrypt data
            from .symmetric import AdvancedSymmetricEncryption
            decryptor = AdvancedSymmetricEncryption()
            plaintext = decryptor.decrypt(encrypted_result, password)
            
            # Verify integrity if checksum present
            if 'integrity_checksum' in encrypted_result:
                expected_checksum = encrypted_result['integrity_checksum']
                if not self.integrity.verify_checksum(plaintext, expected_checksum, 'SHA3-256'):
                    if self.audit:
                        self.audit.log_event('integrity_check_failed', {})
                    return None
            
            # Add more timing noise
            self.anti_forensics.add_timing_noise()
            
            return plaintext
            
        except Exception as e:
            if self.audit:
                self.audit.log_event('extract_and_decrypt_error', {'error': str(e)})
            return None
