"""
Cryptographic utilities for the DevSecOps Deployment Gatekeeper.
"""

import hashlib
import hmac
import base64
from typing import Union


def generate_hmac_signature(
    secret: str, message: str, algorithm: str = "sha256"
) -> str:
    """Generate HMAC signature for message authentication."""
    key = secret.encode("utf-8")
    msg = message.encode("utf-8")

    if algorithm.lower() == "sha256":
        hash_algorithm = hashlib.sha256
    elif algorithm.lower() == "sha1":
        hash_algorithm = hashlib.sha1
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    signature = hmac.new(key, msg, hash_algorithm).hexdigest()
    return signature


def verify_hmac_signature(
    secret: str, message: str, signature: str, algorithm: str = "sha256"
) -> bool:
    """Verify HMAC signature for message authentication."""
    expected_signature = generate_hmac_signature(secret, message, algorithm)
    return hmac.compare_digest(expected_signature, signature)


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """Generate hash of a string."""
    if algorithm.lower() == "sha256":
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    elif algorithm.lower() == "sha1":
        return hashlib.sha1(text.encode("utf-8")).hexdigest()
    elif algorithm.lower() == "md5":
        return hashlib.md5(text.encode("utf-8")).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def encode_base64(data: Union[str, bytes]) -> str:
    """Encode data to base64."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.b64encode(data).decode("utf-8")


def decode_base64(encoded_data: str) -> bytes:
    """Decode base64 data."""
    return base64.b64decode(encoded_data)
