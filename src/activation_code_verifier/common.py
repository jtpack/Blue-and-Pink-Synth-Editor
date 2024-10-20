import hashlib
from datetime import datetime


valid_app_names = ['Blue and Pink Synth Editor']
valid_license_types = ['Registered User', 'Beta Testing']


def generate_license_string(name, display_name, email, app_name, license_type, expiration_date):
    """
    Combine name, display_name, email, app_name, license_type and expiration date into a single string
    :param name: str
    :param display_name: str
    :param email: str
    :param app_name: str
    :param license_type: str
    :param expiration_date: str or None. Should be formatted as YYYY-MM-DD
    :return: str
    """
    return name + display_name + email + app_name + license_type + str(expiration_date)


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


def validate_activation_code_parameters(name, display_name, email,
                                        app_name, license_type, expiration_date):
    """
    Verify that the supplied parameters are valid.
    Raises an Exception if any are not.
    :param name: str
    :param display_name: str
    :param email: str
    :param app_name: str
    :param license_type: str
    :param expiration_date: None or str
    :return:
    """
    if name is None or len(name) == 0:
        raise Exception('name is empty or None')
    
    if display_name is None or len(display_name) == 0:
        raise Exception('display_name is empty or None')

    if email is None or len(email) == 0:
        raise Exception('email is empty or None')

    if app_name not in valid_app_names:
        raise Exception(f'Invalid app_name: {app_name}')

    if license_type not in valid_license_types:
        raise Exception(f'Invalid license_type: {license_type}')

    if expiration_date is not None:
        # This will raise an Exception if expiration_date is invalid
        datetime.strptime(expiration_date, '%Y-%m-%d')
