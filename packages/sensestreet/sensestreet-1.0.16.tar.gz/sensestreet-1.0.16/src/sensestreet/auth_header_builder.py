from datetime import datetime, timedelta
from authlib.jose import jwt
from cryptography.hazmat.primitives import serialization



class AuthHeaderBuilder:
    __version__ = "1.0.16"

    def __init__(
        self,
        app_id,
        priv_key_path=None,
        pub_key_id="default.pub",
        server_id="default",
        pub_key_path=None,
        extra_headers=None,
    ):
        self.app_id = app_id
        self.server_id = server_id
        self.pub_key_id = pub_key_id
        self.auth_key = (
            self._load_rsa_private_key(priv_key_path) if priv_key_path else None
        )
        self.last_token_meta = None
        self.last_token = None
        self.extra_headers = extra_headers
        self.pub_key = self._get_pub_key(pub_key_path)

    def get_headers(self, is_not_json=False):
        start_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        head = {}
        if self.auth_key:
            token = self._get_token()
            head["Authorization"] = "Bearer {}".format(token)
        if not is_not_json:
            head["Content-Type"] = "application/json"
        if self.pub_key:
            head["X-key"] = self.pub_key
        head["X-client-version"] = str(self.__version__)
        head["Date"] = start_time
        if isinstance(self.extra_headers, dict):
            for key, value in self.extra_headers.items():
                head[key] = value
        return head

    def _get_token(self):
        if self.last_token:
            safe_time = datetime.now() + timedelta(minutes=1)
            if self.last_token_meta["exp"] > int(safe_time.timestamp()):
                return self.last_token
        self.last_token, self.last_token_meta = self._generate_token(self.auth_key)
        return self.last_token

    def _generate_token(self, private_key):
        token_payload = {
            # JWT claim
            "exp": datetime.utcnow() + timedelta(minutes=15),  # expiry
            "nbf": datetime.utcnow() - timedelta(minutes=5),
            "aud": "api.sensestreet.com",  # audience
            # Custom fields
            "application_id": self.app_id,
            "public_key_id": self.pub_key_id,
            "server_id": self.server_id,
            "server_role": "default",
        }
        
        token = jwt.encode({"alg": "RS256"}, token_payload, private_key).decode("utf-8")
        return token, token_payload

    def _get_pub_key(self, pub_key_path):
        if pub_key_path:
            try:
                return self._load_rsa_public_key(pub_key_path)
            except FileNotFoundError:
                raise FileNotFoundError("Please provide a valid path to the public key")

    @staticmethod
    def _load_rsa_public_key(path):
        """
        Load public key in pem format.
        """
        with open(path, "rb") as f:
            public_key = f.read()
            decoded_key = public_key.decode()
            if decoded_key[-1] == "\n":
                public_key = public_key[:-1]
        return public_key

    @staticmethod
    def _load_rsa_private_key(path):
        """Load private key in pem format"""
        with open(path, "rb") as f:
            private_key = f.read()
        if (
            b"BEGIN OPENSSH PRIVATE" in private_key
            and b"END OPENSSH PRIVATE" in private_key
        ):
            private_key_openssh = serialization.load_ssh_private_key(private_key, None)
            private_key_rsa = private_key_openssh.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
            return private_key_rsa
        elif b"BEGIN RSA PRIVATE" in private_key and b"END RSA PRIVATE" in private_key:
            return private_key
        raise RuntimeError(
            f"Key in '{path}' is not stored in supported format. Must be either RSA (.pem) or OPENSSH format. "
        )


