import hashlib


def generate_license_string(name, email, app_name, license_type, expiration_date):
    """
    Combine name, email, license_type and expiration date into a single string.
    All strings will be stripped and converted to lowercase.
    :param name: str
    :param email: str
    :param app_name: str
    :param license_type: str
    :param expiration_date: str or None. Should be formatted as YYYY-MM-DD
    :return: str
    """
    return str(name).strip().lower() + str(email).strip().lower() + str(app_name).strip().lower() + str(license_type).strip().lower() + str(expiration_date).strip().lower()


def hash_from_string(code_string):
    """
    Generate a hash of the supplied string.
    :param code_string: str
    :return: bytes
    """
    # Encode the code string into bytes
    code_bytes = code_string.encode('utf-8')

    # Hash the bytes
    code_hash = hashlib.sha256(code_bytes)

    # Digest the hash
    code_digest = code_hash.digest()

    return code_digest
