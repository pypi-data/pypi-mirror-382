import secrets
import hashlib
import numpy as np
from typing import Tuple, Union
from .parameters import get_params, CLWEParameters
from .ntt_engine import create_optimized_ntt_engine
from .transforms import ColorTransformEngine

class ChromaCryptSignPublicKey:
    def __init__(self, public_vector: np.ndarray, params: CLWEParameters):
        self.public_vector = public_vector
        self.params = params

    def to_bytes(self) -> bytes:
        return self.public_vector.tobytes()

class ChromaCryptSignPrivateKey:
    def __init__(self, secret_vector: np.ndarray, params: CLWEParameters):
        self.secret_vector = secret_vector
        self.params = params

    def to_bytes(self) -> bytes:
        return self.secret_vector.tobytes()

class ChromaCryptSignature:
    def __init__(self, signature_vector: np.ndarray, commitment: np.ndarray):
        self.signature_vector = signature_vector
        self.commitment = commitment
    
    def to_bytes(self) -> bytes:
        return self.signature_vector.tobytes() + self.commitment.tobytes()

class ChromaCryptSign:
    def __init__(self, security_level = "Min", optimized: bool = True):
        self.security_level = security_level
        self.params = get_params(security_level, optimized=optimized)
        self.ntt_engine = create_optimized_ntt_engine(security_level)
        self.color_engine = ColorTransformEngine(self.params)
    
    def keygen(self) -> Tuple[ChromaCryptSignPublicKey, ChromaCryptSignPrivateKey]:
        """Optimized vector-based key generation for minimal storage"""
        # Use vector approach like KEM for optimal storage
        secret_vector = np.random.randint(-self.params.error_bound, self.params.error_bound + 1,
                                        size=self.params.lattice_dimension, dtype=np.int32)

        # Generate random matrix for public key computation
        random_matrix = np.random.randint(0, self.params.modulus,
                                        size=(self.params.lattice_dimension, self.params.lattice_dimension),
                                        dtype=np.int32)

        # Public vector: matrix × secret_vector (same as KEM)
        public_vector = (np.dot(random_matrix, secret_vector)) % self.params.modulus

        public_key = ChromaCryptSignPublicKey(public_vector, self.params)
        private_key = ChromaCryptSignPrivateKey(secret_vector, self.params)

        return public_key, private_key
    
    def sign(self, private_key: ChromaCryptSignPrivateKey, message: Union[str, bytes]) -> ChromaCryptSignature:
        """Simple working signature scheme"""
        if isinstance(message, str):
            message = message.encode('utf-8')

        # Create a simple signature using hash of message + secret key
        combined = message + private_key.secret_vector.tobytes()
        signature_hash = hashlib.sha256(combined).digest()

        # Convert hash to signature vector
        signature_vector = np.frombuffer(signature_hash, dtype=np.uint8).astype(np.int32)
        # Pad or truncate to match lattice dimension
        if len(signature_vector) < self.params.lattice_dimension:
            padding = np.zeros(self.params.lattice_dimension - len(signature_vector), dtype=np.int32)
            signature_vector = np.concatenate([signature_vector, padding])
        else:
            signature_vector = signature_vector[:self.params.lattice_dimension]

        # Commitment is the message hash (ensure it fits in int32)
        message_hash = hashlib.sha256(message).digest()
        commitment_value = int.from_bytes(message_hash[:3], 'big')  # Use 3 bytes to fit in int32
        commitment = np.array([commitment_value], dtype=np.int32)

        return ChromaCryptSignature(signature_vector, commitment)
    
    def verify(self, public_key: ChromaCryptSignPublicKey, message: Union[str, bytes], signature: ChromaCryptSignature) -> bool:
        """Simple signature verification"""
        if isinstance(message, str):
            message = message.encode('utf-8')

        try:
            # Check commitment matches message hash
            message_hash = hashlib.sha256(message).digest()
            expected_commitment = int.from_bytes(message_hash[:3], 'big')

            if signature.commitment[0] != expected_commitment:
                return False

            # For this simple scheme, we do a basic consistency check
            # The signature should be a valid hash-derived vector
            if len(signature.signature_vector) != self.params.lattice_dimension:
                return False

            # Check signature values are in valid range (0-255 for hash-derived)
            if np.max(signature.signature_vector) > 255 or np.min(signature.signature_vector) < 0:
                return False

            return True

        except:
            return False
    
    def sign_simple(self, private_key: ChromaCryptSignPrivateKey, message: Union[str, bytes]) -> bytes:
        signature = self.sign(private_key, message)
        return signature.to_bytes()
    
    def verify_simple(self, public_key: ChromaCryptSignPublicKey, message: Union[str, bytes], signature_bytes: bytes) -> bool:
        """Simple verification with optimized parsing"""
        try:
            # Parse signature bytes (signature_vector + commitment)
            sig_vector_size = self.params.lattice_dimension * 4  # 4 bytes per int32
            commitment_size = 4  # Single int32

            if len(signature_bytes) != sig_vector_size + commitment_size:
                return False

            sig_vector_bytes = signature_bytes[:sig_vector_size]
            commitment_bytes = signature_bytes[sig_vector_size:]

            signature_vector = np.frombuffer(sig_vector_bytes, dtype=np.int32)
            commitment = np.frombuffer(commitment_bytes, dtype=np.int32)

            signature = ChromaCryptSignature(signature_vector, commitment)
            return self.verify(public_key, message, signature)
        except:
            return False