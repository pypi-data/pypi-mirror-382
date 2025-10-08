import json
import os
from urllib.parse import urlencode

import boto3
import requests

REDSHIFT_QUERY_BASE_URL = os.environ.get("REDSHIFT_QUERY_BASE_URL")


def query_dc_api(metric: str, query_params: dict = None) -> dict:
    if not REDSHIFT_QUERY_BASE_URL:
        raise EnvironmentError("Missing REDSHIFT_QUERY_BASE_URL env variable")

    url = f"{REDSHIFT_QUERY_BASE_URL.rstrip('/')}/{metric}"

    token = get_secrets()

    headers_auth = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "secretsaccesstoken": token,
    }

    payload = query_params or {}
    query_string = urlencode(payload, safe=":")

    response = requests.request(
        "GET", url, headers=headers_auth, params=query_string, verify=False
    )

    if response.status_code != 200:
        if response.status_code == 401:
            token_old = token
            # Refresh token
            token = get_secrets()
            if token_old == token:
                raise Exception(
                    f"Could not send message to DC API! Error: {str(response)} - Token was updated!"
                    + f" URL: {url}"
                )
            else:
                return query_dc_api(metric, query_params)
        raise Exception(
            f"Could not send message to DC API! Error: {str(response)}" + f" URL: {url}"
        )
    return response


def get_secrets():
    REDSHIFT_SECRET = os.environ.get("REDSHIFT_SECRET")
    if not REDSHIFT_SECRET:
        raise EnvironmentError("Missing REDSHIFT_SECRET env variable")

    REDSHIFT_ROLE_ARN = os.environ.get("REDSHIFT_ROLE_ARN")
    client_sts = boto3.client("sts")
    credentials = client_sts.assume_role(
        RoleArn=REDSHIFT_ROLE_ARN, RoleSessionName="be-another-me"
    )["Credentials"]

    SECRETS_CLIENT = boto3.client(
        "secretsmanager",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    try:
        current_secrets = SECRETS_CLIENT.get_secret_value(
            SecretId=REDSHIFT_SECRET, VersionStage="AWSCURRENT"
        )
        current_dict = json.loads(current_secrets["SecretString"])
        return current_dict["token"]
    except Exception as e:
        raise Exception(e)
