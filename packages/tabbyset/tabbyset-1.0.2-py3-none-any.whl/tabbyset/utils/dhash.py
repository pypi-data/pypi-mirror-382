import hashlib
import pickle

def dhash(input_data) -> int:
    """
    Calculates deterministic hash
    """
    # Serialize the input data to bytes
    serialized_data = pickle.dumps(input_data)

    # Create a new sha256 hash object
    hash_object = hashlib.sha256()

    # Update the hash object with the serialized data
    hash_object.update(serialized_data)

    # Get the hexadecimal representation of the hash
    hash_hex = hash_object.hexdigest()

    # Truncate the hash to 60 bits (15 hex digits)
    truncated_hash_hex = hash_hex[:15]

    # Convert the truncated hexadecimal hash to an integer
    hash_int = int(truncated_hash_hex, 16)

    return hash_int