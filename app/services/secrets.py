"""AWS Secrets Manager helper.

On Lambda, call load_secrets() in main.py before the app starts to inject
secrets into os.environ so the rest of the codebase can use os.environ as normal.

For local development, secrets come from .env via python-dotenv — this module
is a no-op when SECRET_NAME is not set.
"""
from __future__ import annotations

import json
import os


def load_secrets() -> None:
    """Pull secrets from AWS Secrets Manager and inject into os.environ.

    Set SECRET_NAME to the name/ARN of your Secrets Manager secret.
    The secret value must be a JSON object whose keys map to env var names, e.g.:
        {"DATABASE_URL": "postgresql://...", "JWT_SECRET": "...", "GEMINI_API_KEY": "..."}
    """
    secret_name = os.environ.get("SECRET_NAME")
    if not secret_name:
        return  # local dev: rely on .env loaded by python-dotenv

    import boto3  # only needed on Lambda

    client = boto3.client("secretsmanager", region_name=os.environ.get("AWS_REGION", "ap-southeast-1"))
    response = client.get_secret_value(SecretId=secret_name)
    secrets: dict = json.loads(response["SecretString"])
    for key, value in secrets.items():
        os.environ.setdefault(key, str(value))
