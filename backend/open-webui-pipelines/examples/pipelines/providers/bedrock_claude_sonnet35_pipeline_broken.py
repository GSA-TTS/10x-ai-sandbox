import base64
import os
import json
import re
import datetime
import hashlib
import hmac
import requests
from requests.auth import AuthBase
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel


class AWS4Auth(AuthBase):
    def __init__(self, access_id, secret_key, region, service):
        self.access_id = access_id
        self.secret_key = secret_key
        self.region = region
        self.service = service

    def __call__(self, r):
        aws_headers = self.sign(r)
        r.headers.update(aws_headers)
        return r

    def sign(self, r):
        amz_date = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ"
        )
        date_stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
        canonical_uri = r.path_url
        canonical_querystring = ""
        canonical_headers = (
            f'host:{r.url.split("://")[1].split("/")[0]}\nx-amz-date:{amz_date}\n'
        )
        signed_headers = "host;x-amz-date"
        payload_hash = hashlib.sha256(
            r.body
            if isinstance(r.body, bytes)
            else r.body.encode("utf-8") if r.body else b""
        ).hexdigest()
        canonical_request = (
            f"{r.method}\n{canonical_uri}\n{canonical_querystring}\n"
            + f"{canonical_headers}\n{signed_headers}\n{payload_hash}"
        )

        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.region}/{self.service}/aws4_request"
        string_to_sign = (
            f"{algorithm}\n{amz_date}\n{credential_scope}\n"
            + f'{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'
        )

        signing_key = self.get_signature_key(
            self.secret_key, date_stamp, self.region, self.service
        )
        signature = hmac.new(
            signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        authorization_header = (
            f"{algorithm} Credential={self.access_id}/{credential_scope}, "
            + f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        headers = {
            "x-amz-date": amz_date,
            "Authorization": authorization_header,
            "x-amz-content-sha256": payload_hash,
        }

        return headers

    def get_signature_key(self, key, date_stamp, region_name, service_name):
        k_date = self._sign(("AWS4" + key).encode("utf-8"), date_stamp)
        k_region = self._sign(k_date, region_name)
        k_service = self._sign(k_region, service_name)
        k_signing = self._sign(k_service, "aws4_request")
        return k_signing

    def _sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


class Pipeline:
    class Valves(BaseModel):
        AWS_ACCESS_KEY_ID: str
        AWS_SECRET_ACCESS_KEY: str
        AWS_DEFAULT_REGION: str

    def __init__(self):
        self.name = "FedRamp Moderate AWS Claude Sonnet 3.5"
        self.valves = self.Valves(
            **{
                "AWS_ACCESS_KEY_ID": os.getenv(
                    "AWS_ACCESS_KEY_ID", "your-aws-access-key-id-here"
                ),
                "AWS_SECRET_ACCESS_KEY": os.getenv(
                    "AWS_SECRET_ACCESS_KEY", "your-aws-secret-access-key-here"
                ),
                "AWS_DEFAULT_REGION": os.getenv(
                    "AWS_DEFAULT_REGION", "your-aws-region-here"
                ),
            }
        )
        self.auth = AWS4Auth(
            self.valves.AWS_ACCESS_KEY_ID,
            self.valves.AWS_SECRET_ACCESS_KEY,
            self.valves.AWS_DEFAULT_REGION,
            "bedrock",
        )

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")

        # print(messages)
        # print(user_message)

        # allowed_roles = {"user", "assistant"}

        if "messages" in body:
            # remove messages with system role and insert content into body
            new_msgs = []
            for message in body["messages"]:
                if message["role"] == "system":
                    system_msg = message["content"]
                    body["system"] = system_msg
                else:
                    new_msgs.append(message)
            body["messages"] = new_msgs

        headers = {
            "X-Amzn-Bedrock-Accept": "application/json",
            "Content-Type": "application/json",
        }

        # model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

        # Let's make a pipeline for each model
        url = (
            f"https://bedrock-runtime.{self.valves.AWS_DEFAULT_REGION}.amazonaws.com"
            + f"/model/anthropic.claude-3-haiku-20240307-v1:0/invoke-with-response-stream"
        )

        allowed_params = {
            "anthropic_version",
            "messages",
            "temperature",
            "role",
            "content",
            "contentPart",
            "contentPartImage",
            "enhancements",
            "dataSources",
            "n",
            "stop",
            "max_tokens",
            "presence_penalty",
            "frequency_penalty",
            "logit_bias",
            "function_call",
            "functions",
            "tools",
            "tool_choice",
            "top_p",
            "log_probs",
            "top_logprobs",
            "response_format",
            "seed",
            "system",
        }
        if "user" in body and not isinstance(body["user"], str):
            body["user"] = (
                body["user"]["id"] if "id" in body["user"] else str(body["user"])
            )
        filtered_body = {k: v for k, v in body.items() if k in allowed_params}
        if len(body) != len(filtered_body):
            print(
                f"Dropped params: {', '.join(set(body.keys()) - set(filtered_body.keys()))}"
            )

        if "anthropic_version" not in filtered_body:
            filtered_body["anthropic_version"] = "bedrock-2023-05-31"

        if "max_tokens" not in filtered_body:
            filtered_body["max_tokens"] = 4000

        try:
            r = requests.post(
                url=url,
                json=filtered_body,
                headers=headers,
                auth=self.auth,
                stream=True,
            )
            r.raise_for_status()
            if body.get("stream", False):
                return self._parse_event_stream(r)
            else:
                return r.json()
        except requests.exceptions.HTTPError as e:
            if r.status_code == 400:
                print(f"400 Bad Request received: {r.text}")
            else:
                print(f"HTTP Error: {e} Response: {r.text}")
            return (
                f"Error with r: {e} ({r.text}) for body:\n{body}\n\n"
                + f"Filtered_body:\n{filtered_body}\n\n"
                + f"Auth:\n{self.auth.__dict__}"
            )
        except Exception as e:  # This will catch other errors
            print(f"Error without r: {e} for auth: {self.auth}")
            return f"Error without r: {e} for auth: {self.auth}"

    def _parse_event_stream(self, response):
        for line in response.iter_lines():
            if line:
                try:
                    decoded_line = line.decode("utf-8", errors="ignore")

                    # Regular expression to find the value for the "bytes" key
                    pattern = r'"bytes":"(.*?)"'

                    # Search for the pattern in the input string
                    match = re.search(pattern, decoded_line)

                    if match:
                        bytes_value = match.group(1)
                        decoded_bytes = base64.b64decode(bytes_value)
                        decoded_str = decoded_bytes.decode("utf-8")
                        decoded_dict = json.loads(decoded_str)
                        if decoded_dict and "delta" in decoded_dict:
                            if "text" in decoded_dict["delta"]:
                                yield decoded_dict["delta"]["text"]

                except Exception as e:
                    yield f"Error parsing line: {e}"
