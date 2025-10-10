"""
Saithonanen Main API
High-level interface for all encryption and security features
"""

from .symmetric import AdvancedSymmetricEncryption, MultiLayerEncryption
from .asymmetric import AdvancedAsymmetricEncryption, HybridEncryption
from .quantum_resistant import QuantumResistantHybrid
from .security import AdvancedSecurity


class Saithonanen:
    """
    Main entry point for the Saithonanen library.
    Provides access to all major features.
    """

    def __init__(self, enable_audit: bool = True):
        """
        Initialize the Saithonanen library

        Args:
            enable_audit (bool): Enable security auditing and logging
        """
        self.symmetric = AdvancedSymmetricEncryption()
        self.multi_layer = MultiLayerEncryption()
        self.asymmetric = AdvancedAsymmetricEncryption()
        self.hybrid = HybridEncryption()
        self.quantum_resistant = QuantumResistantHybrid()
        self.security = AdvancedSecurity(enable_audit=enable_audit)

    def encrypt_file_symmetric(self, file_path: str, output_path: str, password: str):
        """Encrypt a file using symmetric encryption."""
        with open(file_path, "rb") as f:
            plaintext = f.read()
        encrypted_data = self.symmetric.encrypt(plaintext, password)
        import pickle
        with open(output_path, "wb") as f:
            pickle.dump(encrypted_data, f)

    def decrypt_file_symmetric(self, file_path: str, output_path: str, password: str):
        """Decrypt a file using symmetric encryption."""
        import pickle
        with open(file_path, "rb") as f:
            encrypted_data = pickle.load(f)
        plaintext = self.symmetric.decrypt(encrypted_data, password)
        with open(output_path, "wb") as f:
            f.write(plaintext)

    def encrypt_file_hybrid(self, file_path: str, output_path: str, public_key_path: str):
        """Encrypt a file using hybrid encryption."""
        with open(file_path, "rb") as f:
            plaintext = f.read()
        with open(public_key_path, "rb") as f:
            public_key_data = f.read()
        public_key = self.asymmetric.load_public_key(public_key_data)
        encrypted_data = self.hybrid.encrypt(plaintext, public_key)
        import pickle
        with open(output_path, "wb") as f:
            pickle.dump(encrypted_data, f)

    def decrypt_file_hybrid(self, file_path: str, output_path: str, private_key_path: str, password: str = None):
        """Decrypt a file using hybrid encryption."""
        import pickle
        with open(file_path, "rb") as f:
            encrypted_data = pickle.load(f)
        with open(private_key_path, "rb") as f:
            private_key_data = f.read()
        private_key = self.asymmetric.load_private_key(private_key_data, password)
        plaintext = self.hybrid.decrypt(encrypted_data, private_key)
        with open(output_path, "wb") as f:
            f.write(plaintext)

    def hide_file_in_image(self, file_to_hide: str, cover_image: str, output_image: str, password: str):
        """Hide a file within an image using steganography."""
        with open(file_to_hide, "rb") as f:
            secret_data = f.read()
        self.security.secure_encrypt_and_hide(secret_data, password, cover_image, output_image)

    def extract_file_from_image(self, stego_image: str, output_file: str, password: str):
        """Extract a hidden file from an image."""
        secret_data = self.security.secure_extract_and_decrypt(stego_image, password)
        if secret_data:
            with open(output_file, "wb") as f:
                f.write(secret_data)
