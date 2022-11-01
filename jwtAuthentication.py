from datetime import timedelta, timezone, datetime
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
from getpass import getpass
import hashlib

# Construct the fully qualified name of the user in uppercase.
# - Replace <account_identifier> with your account identifier.
#   (See https://docs.snowflake.com/en/user-guide/admin-account-identifier.html .)
# - Replace <user_name> with your Snowflake user name.

pem_bytes = b'''<your_private_key>'''

passphrase = b'<your_secret_password>'

private_key = serialization.load_pem_private_key(
    pem_bytes, password=passphrase, backend=default_backend()
)

def generate_fp():
    # Get the raw bytes of the public key.
    public_key_raw = private_key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

    # Get the sha256 hash of the raw bytes.
    sha256hash = hashlib.sha256()
    sha256hash.update(public_key_raw)

    # Base64-encode the value and prepend the prefix 'SHA256:'.
    return 'SHA256:' + base64.b64encode(sha256hash.digest()).decode('utf-8')


def get_token(current_token, current_exp):
    if current_token and datetime.now(timezone.utc) < current_exp:
        return {
        'token': current_token,
        'exp': current_exp
        }
    else:
        # Get the account identifier without the region, cloud provider, or subdomain.
        account = "<your_account_name>"
        if not '.global' in account:
            idx = account.find('.')
            if idx > 0:
                account = account[0:idx]
            else:
                # Handle the replication case.
                idx = account.find('-')
                if idx > 0:
                    account = account[0:idx]

        account = account.upper()
        user = "<your_snowflake_username>".upper()
        qualified_username = account + "." + user

        now = datetime.now(timezone.utc)
        lifetime = timedelta(minutes=59)

        public_key_fp= generate_fp()

        # Create the payload for the token.
        payload = {

            # Set the issuer to the fully qualified username concatenated with the public key fingerprint.
            "iss": qualified_username + '.' + public_key_fp,

            # Set the subject to the fully qualified username.
            "sub": qualified_username,

            # Set the issue time to now.
            "iat": now,

            # Set the expiration time, based on the lifetime specified for this object.
            "exp": now + lifetime
        }



        # Generate the JWT. private_key is the private key that you read from the private key file in the previous step when you generated the public key fingerprint.
        encoding_algorithm="RS256"
        token = jwt.encode(payload, key=private_key, algorithm=encoding_algorithm)

        return {
            'token': token,
            'exp': payload['exp']
        }