from pathlib import Path
import json
import base64
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def _load_public_key(key_path):
    # Make sure key_path is a Path
    key_path = Path(key_path).expanduser()

    with open(key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read()
        )
    return public_key


def verify_license_file(license_file_path, public_key_path):
    """
    Load data from a license file, and verify two things:
    - that it was generated using the specified public key's private key match
    - that the name, email, license type and expiration date in the file are correct
    :param license_file_path: Path or str
    :param public_key_path: Path or str
    :return: bool
    """
    # Load the contents of the file
    license_dict = load_data_from_license_file(license_file_path)

    # Verify the data
    try:
        return _verify_signature(name=license_dict['name'], email=license_dict['email'],
                                 license_type=license_dict['license_type'],
                                 expiration_date=license_dict['expiration_date'],
                                 signature=base64.b64decode(license_dict['signature']),
                                 public_key_path=public_key_path)

    except Exception as e:
        print(e)

        return False


def load_data_from_license_file(license_file_path):
    """
    Load name, email, license_type, expiration_date and signature
    from a license file
    :param license_file_path: Path or str
    :return: dict
    """
    # Make sure licence_file_path is a Path
    license_file_path = Path(license_file_path).expanduser()

    # Load the contents of the file
    with open(license_file_path, 'r') as file:
        return json.load(file)


def _verify_signature(name, email, license_type, expiration_date,
                      signature, public_key_path):
    """
    Verify that the supplied signature was generated
    using the private key which matches the supplied
    public key, and that the signature contains the
    correct hash for the supplied name, email,
    license type and expiration date
    :param name: str. Not case-sensitive. Leading and trailing whitespace will be stripped away.
    :param email: str. Not case-sensitive. Leading and trailing whitespace will be stripped away.
`   :param license_type: str. Not case-sensitive. Leading and trailing whitespace will be stripped away.
    :param expiration_date: str or None. Should be formatted as YYYY-MM-DD. Leading and trailing whitespace will be stripped away.
    :param signature: bytes
    :param public_key_path: Path or str
    :return: bool
    """
    public_key = _load_public_key(key_path=public_key_path)

    # Generate a code string from the name, email, license_type and expiration date
    code_string = _generate_license_string(name=name,
                                           email=email,
                                           license_type=license_type,
                                           expiration_date=expiration_date)

    # Generate a hash
    code_hash = _hash_from_string(code_string=code_string)

    try:
        public_key.verify(
            signature,
            code_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True

    except Exception:
        return False


def _generate_license_string(name, email, license_type, expiration_date):
    """
    Combine name, email, license_type and expiration date into a single string.
    All strings will be stripped and converted to lowercase.
    :param name: str
    :param email: str
    :param license_type: str
    :param expiration_date: str or None. Should be formatted as YYYY-MM-DD
    :return: str
    """
    return str(name).strip().lower() + str(email).strip().lower() + str(license_type).strip().lower() + str(expiration_date).strip().lower()


def _hash_from_string(code_string):
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
