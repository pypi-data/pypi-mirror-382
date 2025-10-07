import os
import json
from typing import Optional
import boto3
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode
from my_aws_helpers.logging import select_powertools_logger

logger = select_powertools_logger("aws-helpers-cognito")


class Cognito:
    client: boto3.client

    def __init__(
        self,
        client: Optional[boto3.client] = None,
        user_pool_id: Optional[str] = None,
    ):
        self.cognito_user_pool_id = (
            user_pool_id if user_pool_id else os.environ["COGNITO_USER_POOL_ID"]
        )
        self.region = os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-2")
        self.client = client if client else self._get_client(region=self.region)

    def _get_client(self, region: str) -> boto3.client:
        return boto3.client("cognito-idp", region_name=region)

    def _verify_signature(self):
        pass

    def _verify_audience(self):
        pass

    def _verify_token_use(self):
        pass

    def validate_token(self, token: str) -> bool:
        try:
            if "Bearer" in token:
                token = token.split(" ")[-1]
            headers = jwt.get_unverified_headers(token)
            key_id = headers["kid"]
            keys = self._get_keys()
            key = next(k for k in keys if k["kid"] == key_id)
            public_key = jwk.construct(key)
            message, encoded_signature = token.rsplit(".", 1)
            decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))
            if not public_key.verify(message.encode("utf-8"), decoded_signature):
                raise Exception("Signature verification failed")
            return True
        except Exception as e:
            logger.exception(f"Failed to validate token due to {e}")
            return False

    def sign_up(self, username: str, password: str, app_client_id: str):
        try:
            response = self.client.sign_up(
                ClientId=app_client_id,
                Username=username,
                Password=password,
                UserAttributes=[
                    {"Name": "email", "Value": username},
                ],
            )
            return response
        except Exception as e:
            logger.exception(f"Failed to sign up due to {e}")
            return None

    def admin_confirm_sign_up(
        self,
        username: str,
        user_pool_id: str,
    ) -> dict:
        try:
            response = self.client.admin_confirm_sign_up(
                UserPoolId=user_pool_id, Username=username
            )
            return response
        except Exception as e:
            logger.exception(
                f"Failed to confirm admin sign up username {username} due to {e}"
            )
            return None

    def refresh_token(self, refresh_token: str, app_client_id: str):
        response = self.client.initiate_auth(
            ClientId=app_client_id,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": refresh_token},
        )
        return response

    def login(self, username: str, password: str, app_client_id: str):
        response = self.client.initiate_auth(
            ClientId=app_client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        return response

    def _get_issuer(self) -> str:
        return f"https://cognito-idp.{self.region}.amazonaws.com/{self.cognito_user_pool_id}"

    def _get_keys(self):
        issuer = self._get_issuer()
        keys_url = f"{issuer}/.well-known/jwks.json"
        with urllib.request.urlopen(keys_url) as f:
            response = f.read()
            keys = json.loads(response.decode("utf-8"))["keys"]
        return keys

    @staticmethod
    def get_policy(allow: bool, method_arn: str = "*") -> dict:
        allow = "Allow" if allow else "Deny"
        return {
            "principalId": "authenticated-user",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [{"Action": "*", "Effect": allow, "Resource": "*"}],
            },
        }
