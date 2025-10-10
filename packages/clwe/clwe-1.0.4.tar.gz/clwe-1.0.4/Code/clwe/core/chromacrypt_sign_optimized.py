import secrets
import hashlib
import numpy as np
from typing import Tuple, Union
from .parameters import get_params, CLWEParameters
from .ntt_engine import create_optimized_ntt_engine
from .transforms import ColorTransformEngine

class OptimizedChromaCryptSignPublicKey:
    def __init__(self, public_vector: np.ndarray, params: CLWEParameters):
        self.public_vector = public_vector
        self.params = params

    def to_bytes(self) -> bytes:
        return self.public_vector.tobytes()

class OptimizedChromaCryptSignPrivateKey:
    def __init__(self, secret_vector: np.ndarray, params: CLWEParameters):
        self.secret_vector = secret_vector
        self.params = params

    def to_bytes(self) -> bytes:
        return self.secret_vector.tobytes()

class OptimizedChromaCryptSignature:
    def __init__(self, signature_vector: np.ndarray, commitment: np.ndarray):
        self.signature_vector = signature_vector
        self.commitment = commitment

    def to_bytes(self) -> bytes:
        return self.signature_vector.tobytes() + self.commitment.tobytes()

class OptimizedChromaCryptSign:
    """Vector-based signature implementation for optimal storage efficiency"""

    def __init__(self, security_level: int = 128, optimized: bool = True):
        self.security_level = security_level
        self.params = get_params(security_level, optimized=optimized)
        self.ntt_engine = create_optimized_ntt_engine(security_level)
        self.color_engine = ColorTransformEngine(self.params)

    def keygen(self) -> Tuple[OptimizedChromaCryptSignPublicKey, OptimizedChromaCryptSignPrivateKey]:
        """Generate vector-based keys (same size as KEM keys)"""
        # Use vector approach like KEM for optimal storage
        secret_vector = np.random.randint(-self.params.error_bound, self.params.error_bound + 1,
                                        size=self.params.lattice_dimension, dtype=np.int32)

        # Generate random matrix for public key computation
        random_matrix = np.random.randint(0, self.params.modulus,
                                        size=(self.params.lattice_dimension, self.params.lattice_dimension),
                                        dtype=np.int32)

        # Public vector: matrix × secret_vector (same as KEM)
        public_vector = (np.dot(random_matrix, secret_vector)) % self.params.modulus

        public_key = OptimizedChromaCryptSignPublicKey(public_vector, self.params)
        private_key = OptimizedChromaCryptSignPrivateKey(secret_vector, self.params)

        return public_key, private_key

    def sign(self, private_key: OptimizedChromaCryptSignPrivateKey, message: Union[str, bytes]) -> OptimizedChromaCryptSignature:
        """Optimized signing with vector operations - matches KEM approach"""
        if isinstance(message, str):
            message = message.encode('utf-8')

        message_hash = hashlib.sha256(message).digest()

        # Commitment randomness (vector like KEM)
        commitment_randomness = np.random.randint(-self.params.error_bound, self.params.error_bound + 1,
                                                size=self.params.lattice_dimension, dtype=np.int32)

        # Commitment: Simple dot product (like KEM)
        commitment = np.sum(commitment_randomness * private_key.secret_vector) % self.params.modulus
        commitment = np.array([commitment], dtype=np.int32)

        # Challenge generation
        challenge_input = commitment.tobytes() + message_hash
        challenge_hash = hashlib.sha256(challenge_input).digest()
        challenge = int.from_bytes(challenge_hash[:4], 'big') % self.params.modulus

        # Signature vector: commitment_randomness + challenge * secret_vector
        signature_vector = (commitment_randomness + challenge * private_key.secret_vector) % self.params.modulus

        return OptimizedChromaCryptSignature(signature_vector, commitment)

    def verify(self, public_key: OptimizedChromaCryptSignPublicKey, message: Union[str, bytes], signature: OptimizedChromaCryptSignature) -> bool:
        """Optimized verification with vector operations - matches KEM approach"""
        if isinstance(message, str):
            message = message.encode('utf-8')

        message_hash = hashlib.sha256(message).digest()

        # Recompute challenge
        challenge_input = signature.commitment.tobytes() + message_hash
        challenge_hash = hashlib.sha256(challenge_input).digest()
        challenge = int.from_bytes(challenge_hash[:4], 'big') % self.params.modulus

        try:
            # Verify signature: signature_vector • public_vector ≟ commitment + challenge
            left_side = np.sum(signature.signature_vector * public_key.public_vector) % self.params.modulus
            right_side = (signature.commitment[0] + challenge) % self.params.modulus

            return left_side == right_side
        except:
            return False

    def sign_simple(self, private_key: OptimizedChromaCryptSignPrivateKey, message: Union[str, bytes]) -> bytes:
        """Simple signing interface"""
        signature = self.sign(private_key, message)
        return signature.to_bytes()

    def verify_simple(self, public_key: OptimizedChromaCryptSignPublicKey, message: Union[str, bytes], signature_bytes: bytes) -> bool:
        """Simple verification interface"""
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

            signature = OptimizedChromaCryptSignature(signature_vector, commitment)
            return self.verify(public_key, message, signature)
        except:
            return False