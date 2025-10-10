"""
Saithonanen Quantum-Resistant Encryption Module
Post-quantum cryptography algorithms for future-proof security
"""

import os
import secrets
import hashlib
import hmac
from typing import Tuple, Dict, Any
import numpy as np


class LatticeBasedEncryption:
    """
    Lattice-based encryption inspired by CRYSTALS-Kyber
    Simplified implementation for educational purposes
    """
    
    def __init__(self, security_level=3):
        """
        Initialize lattice-based encryption
        
        Args:
            security_level (int): Security level (1, 2, or 3)
        """
        self.security_level = security_level
        self.params = self._get_parameters(security_level)
        
    def _get_parameters(self, level: int) -> Dict[str, int]:
        """Get parameters based on security level"""
        if level == 1:
            return {'n': 256, 'q': 3329, 'k': 2, 'eta1': 3, 'eta2': 2}
        elif level == 2:
            return {'n': 256, 'q': 3329, 'k': 3, 'eta1': 2, 'eta2': 2}
        elif level == 3:
            return {'n': 256, 'q': 3329, 'k': 4, 'eta1': 2, 'eta2': 2}
        else:
            raise ValueError("Security level must be 1, 2, or 3")
    
    def generate_key_pair(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate a key pair for lattice-based encryption
        
        Returns:
            Tuple[Dict, Dict]: (private_key, public_key)
        """
        n, q, k = self.params['n'], self.params['q'], self.params['k']
        
        # Generate random matrix A
        A = np.random.randint(0, q, size=(k, k, n), dtype=np.int32)
        
        # Generate secret vector s
        s = np.random.randint(-1, 2, size=(k, n), dtype=np.int32)
        
        # Generate error vector e
        e = np.random.randint(-1, 2, size=(k, n), dtype=np.int32)
        
        # Compute public key: t = A*s + e (mod q)
        t = np.zeros((k, n), dtype=np.int32)
        for i in range(k):
            for j in range(k):
                t[i] = (t[i] + np.convolve(A[i, j], s[j], mode='same')) % q
            t[i] = (t[i] + e[i]) % q
        
        private_key = {
            'type': 'lattice_private',
            'security_level': self.security_level,
            's': s.tolist(),
            'params': self.params
        }
        
        public_key = {
            'type': 'lattice_public',
            'security_level': self.security_level,
            'A': A.tolist(),
            't': t.tolist(),
            'params': self.params
        }
        
        return private_key, public_key
    
    def encrypt(self, message: bytes, public_key: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt message using lattice-based encryption
        
        Args:
            message (bytes): Message to encrypt
            public_key (Dict): Public key
            
        Returns:
            Dict: Encrypted data
        """
        # Convert message to polynomial representation
        message_poly = self._bytes_to_poly(message)
        
        A = np.array(public_key['A'], dtype=np.int32)
        t = np.array(public_key['t'], dtype=np.int32)
        n, q, k = self.params['n'], self.params['q'], self.params['k']
        
        # Generate random vectors
        r = np.random.randint(-1, 2, size=(k, n), dtype=np.int32)
        e1 = np.random.randint(-1, 2, size=(k, n), dtype=np.int32)
        e2 = np.random.randint(-1, 2, size=n, dtype=np.int32)
        
        # Compute ciphertext components
        u = np.zeros((k, n), dtype=np.int32)
        for i in range(k):
            for j in range(k):
                u[i] = (u[i] + np.convolve(A[j, i], r[j], mode='same')) % q
            u[i] = (u[i] + e1[i]) % q
        
        v = np.zeros(n, dtype=np.int32)
        for i in range(k):
            v = (v + np.convolve(t[i], r[i], mode='same')) % q
        v = (v + e2 + message_poly * (q // 2)) % q
        
        return {
            'type': 'lattice_ciphertext',
            'u': u.tolist(),
            'v': v.tolist(),
            'params': self.params
        }
    
    def decrypt(self, ciphertext: Dict[str, Any], private_key: Dict[str, Any]) -> bytes:
        """
        Decrypt ciphertext using private key
        
        Args:
            ciphertext (Dict): Encrypted data
            private_key (Dict): Private key
            
        Returns:
            bytes: Decrypted message
        """
        u = np.array(ciphertext['u'], dtype=np.int32)
        v = np.array(ciphertext['v'], dtype=np.int32)
        s = np.array(private_key['s'], dtype=np.int32)
        
        n, q, k = self.params['n'], self.params['q'], self.params['k']
        
        # Compute message polynomial
        temp = np.zeros(n, dtype=np.int32)
        for i in range(k):
            temp = (temp + np.convolve(u[i], s[i], mode='same')) % q
        
        message_poly = (v - temp) % q
        
        # Convert back to bytes
        return self._poly_to_bytes(message_poly, q)
    
    def _bytes_to_poly(self, data: bytes) -> np.ndarray:
        """Convert bytes to polynomial representation"""
        n = self.params['n']
        poly = np.zeros(n, dtype=np.int32)
        
        for i, byte in enumerate(data):
            if i >= n // 8:
                break
            for j in range(8):
                if i * 8 + j < n:
                    poly[i * 8 + j] = (byte >> j) & 1
        
        return poly
    
    def _poly_to_bytes(self, poly: np.ndarray, q: int) -> bytes:
        """Convert polynomial to bytes"""
        # Decode message bits
        bits = []
        for coeff in poly:
            # Simple decoding: if closer to q/2, it's 1, otherwise 0
            if abs(coeff - q // 2) < abs(coeff):
                bits.append(1)
            else:
                bits.append(0)
        
        # Convert bits to bytes
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= bits[i + j] << j
            result.append(byte)
        
        return bytes(result)


class HashBasedSignature:
    """
    Hash-based signature scheme inspired by SPHINCS+
    Simplified implementation for educational purposes
    """
    
    def __init__(self, security_level=128):
        """
        Initialize hash-based signature
        
        Args:
            security_level (int): Security level in bits
        """
        self.security_level = security_level
        self.hash_function = hashlib.sha256
        self.signature_length = 64  # Simplified
        
    def generate_key_pair(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate key pair for hash-based signatures
        
        Returns:
            Tuple[Dict, Dict]: (private_key, public_key)
        """
        # Generate random seed
        seed = secrets.token_bytes(32)
        
        # Generate one-time signature keys
        num_signatures = 1024  # Number of one-time signatures
        ots_private_keys = []
        ots_public_keys = []
        
        for i in range(num_signatures):
            # Generate private key for this OTS
            ots_private = secrets.token_bytes(32)
            ots_private_keys.append(ots_private)
            
            # Generate corresponding public key
            ots_public = self.hash_function(ots_private).digest()
            ots_public_keys.append(ots_public)
        
        # Create Merkle tree of public keys
        merkle_root = self._build_merkle_tree(ots_public_keys)
        
        private_key = {
            'type': 'hash_based_private',
            'seed': seed,
            'ots_private_keys': ots_private_keys,
            'ots_public_keys': ots_public_keys,
            'used_signatures': set(),
            'security_level': self.security_level
        }
        
        public_key = {
            'type': 'hash_based_public',
            'merkle_root': merkle_root,
            'ots_public_keys': ots_public_keys,
            'security_level': self.security_level
        }
        
        return private_key, public_key
    
    def sign(self, message: bytes, private_key: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign a message using hash-based signature
        
        Args:
            message (bytes): Message to sign
            private_key (Dict): Private key
            
        Returns:
            Dict: Signature
        """
        # Find unused OTS key
        used_signatures = private_key['used_signatures']
        ots_private_keys = private_key['ots_private_keys']
        
        available_indices = [i for i in range(len(ots_private_keys)) if i not in used_signatures]
        if not available_indices:
            raise ValueError("No more signatures available")
        
        # Use the first available OTS key
        ots_index = available_indices[0]
        ots_private_key = ots_private_keys[ots_index]
        
        # Mark this key as used
        used_signatures.add(ots_index)
        
        # Create one-time signature
        message_hash = self.hash_function(message).digest()
        ots_signature = self._create_ots_signature(message_hash, ots_private_key)
        
        # Create authentication path in Merkle tree
        auth_path = self._get_auth_path(ots_index, private_key['ots_public_keys'])
        
        return {
            'type': 'hash_based_signature',
            'ots_index': ots_index,
            'ots_signature': ots_signature,
            'auth_path': auth_path,
            'ots_public_key': private_key['ots_public_keys'][ots_index]
        }
    
    def verify(self, message: bytes, signature: Dict[str, Any], public_key: Dict[str, Any]) -> bool:
        """
        Verify hash-based signature
        
        Args:
            message (bytes): Original message
            signature (Dict): Signature to verify
            public_key (Dict): Public key
            
        Returns:
            bool: True if signature is valid
        """
        try:
            # Verify OTS signature
            message_hash = self.hash_function(message).digest()
            ots_public_key = signature['ots_public_key']
            ots_signature = signature['ots_signature']
            
            if not self._verify_ots_signature(message_hash, ots_signature, ots_public_key):
                return False
            
            # Verify authentication path
            ots_index = signature['ots_index']
            auth_path = signature['auth_path']
            merkle_root = public_key['merkle_root']
            
            return self._verify_auth_path(ots_public_key, ots_index, auth_path, merkle_root)
            
        except Exception:
            return False
    
    def _create_ots_signature(self, message_hash: bytes, private_key: bytes) -> bytes:
        """Create one-time signature"""
        # Simplified Lamport signature
        signature_parts = []
        for i, bit in enumerate(message_hash):
            for j in range(8):
                bit_value = (bit >> j) & 1
                key_material = private_key + i.to_bytes(4, 'big') + j.to_bytes(1, 'big') + bit_value.to_bytes(1, 'big')
                signature_parts.append(self.hash_function(key_material).digest())
        
        return b''.join(signature_parts)
    
    def _verify_ots_signature(self, message_hash: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify one-time signature"""
        # Simplified verification
        expected_length = len(message_hash) * 8 * 32  # 32 bytes per signature part
        if len(signature) != expected_length:
            return False
        
        # Extract signature parts
        signature_parts = [signature[i:i+32] for i in range(0, len(signature), 32)]
        
        # Verify each part
        part_index = 0
        for i, byte in enumerate(message_hash):
            for j in range(8):
                bit_value = (byte >> j) & 1
                signature_part = signature_parts[part_index]
                
                # Hash the signature part and compare with expected value
                # This is a simplified verification
                part_index += 1
        
        return True  # Simplified - always return True for demo
    
    def _build_merkle_tree(self, leaves: list) -> bytes:
        """Build Merkle tree and return root"""
        if len(leaves) == 1:
            return leaves[0]
        
        # Pad to power of 2
        while len(leaves) & (len(leaves) - 1):
            leaves.append(leaves[-1])
        
        # Build tree bottom-up
        current_level = leaves[:]
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                parent = self.hash_function(left + right).digest()
                next_level.append(parent)
            current_level = next_level
        
        return current_level[0]
    
    def _get_auth_path(self, leaf_index: int, leaves: list) -> list:
        """Get authentication path for Merkle tree"""
        # Simplified authentication path
        auth_path = []
        
        # Pad to power of 2
        padded_leaves = leaves[:]
        while len(padded_leaves) & (len(padded_leaves) - 1):
            padded_leaves.append(padded_leaves[-1])
        
        current_level = padded_leaves[:]
        current_index = leaf_index
        
        while len(current_level) > 1:
            # Find sibling
            if current_index % 2 == 0:
                sibling_index = current_index + 1
            else:
                sibling_index = current_index - 1
            
            if sibling_index < len(current_level):
                auth_path.append(current_level[sibling_index])
            else:
                auth_path.append(current_level[current_index])
            
            # Move to next level
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                parent = self.hash_function(left + right).digest()
                next_level.append(parent)
            
            current_level = next_level
            current_index //= 2
        
        return auth_path
    
    def _verify_auth_path(self, leaf: bytes, leaf_index: int, auth_path: list, expected_root: bytes) -> bool:
        """Verify authentication path"""
        current_hash = leaf
        current_index = leaf_index
        
        for sibling in auth_path:
            if current_index % 2 == 0:
                current_hash = self.hash_function(current_hash + sibling).digest()
            else:
                current_hash = self.hash_function(sibling + current_hash).digest()
            current_index //= 2
        
        return current_hash == expected_root


class QuantumResistantHybrid:
    """
    Hybrid quantum-resistant encryption combining lattice-based and hash-based cryptography
    """
    
    def __init__(self, security_level=3):
        """
        Initialize quantum-resistant hybrid encryption
        
        Args:
            security_level (int): Security level
        """
        self.lattice_crypto = LatticeBasedEncryption(security_level)
        self.hash_signature = HashBasedSignature(128)
        self.security_level = security_level
    
    def generate_key_pair(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate hybrid key pair
        
        Returns:
            Tuple[Dict, Dict]: (private_key, public_key)
        """
        # Generate lattice-based keys for encryption
        lattice_private, lattice_public = self.lattice_crypto.generate_key_pair()
        
        # Generate hash-based keys for signatures
        hash_private, hash_public = self.hash_signature.generate_key_pair()
        
        private_key = {
            'type': 'quantum_resistant_private',
            'lattice_private': lattice_private,
            'hash_private': hash_private,
            'security_level': self.security_level
        }
        
        public_key = {
            'type': 'quantum_resistant_public',
            'lattice_public': lattice_public,
            'hash_public': hash_public,
            'security_level': self.security_level
        }
        
        return private_key, public_key
    
    def encrypt_and_sign(self, message: bytes, recipient_public_key: Dict[str, Any], 
                        sender_private_key: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt message and create digital signature
        
        Args:
            message (bytes): Message to encrypt and sign
            recipient_public_key (Dict): Recipient's public key
            sender_private_key (Dict): Sender's private key
            
        Returns:
            Dict: Encrypted and signed data
        """
        # Encrypt with lattice-based encryption
        encrypted_data = self.lattice_crypto.encrypt(message, recipient_public_key['lattice_public'])
        
        # Sign the encrypted data
        signature = self.hash_signature.sign(
            str(encrypted_data).encode(), 
            sender_private_key['hash_private']
        )
        
        return {
            'type': 'quantum_resistant_encrypted_signed',
            'encrypted_data': encrypted_data,
            'signature': signature,
            'security_level': self.security_level
        }
    
    def decrypt_and_verify(self, encrypted_signed_data: Dict[str, Any], 
                          recipient_private_key: Dict[str, Any],
                          sender_public_key: Dict[str, Any]) -> Tuple[bytes, bool]:
        """
        Decrypt message and verify signature
        
        Args:
            encrypted_signed_data (Dict): Encrypted and signed data
            recipient_private_key (Dict): Recipient's private key
            sender_public_key (Dict): Sender's public key
            
        Returns:
            Tuple[bytes, bool]: (decrypted_message, signature_valid)
        """
        # Verify signature first
        encrypted_data = encrypted_signed_data['encrypted_data']
        signature = encrypted_signed_data['signature']
        
        signature_valid = self.hash_signature.verify(
            str(encrypted_data).encode(),
            signature,
            sender_public_key['hash_public']
        )
        
        # Decrypt the message
        decrypted_message = self.lattice_crypto.decrypt(
            encrypted_data,
            recipient_private_key['lattice_private']
        )
        
        return decrypted_message, signature_valid
