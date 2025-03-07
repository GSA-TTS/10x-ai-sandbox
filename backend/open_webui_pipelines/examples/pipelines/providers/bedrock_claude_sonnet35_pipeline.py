# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Helper utilities for working with Amazon Bedrock from Python notebooks"""
# Python Built-Ins:
import os
import json
import requests
from typing import List, Union, Generator, Iterator, Optional
from pydantic import BaseModel

# External Dependencies:
import boto3
from botocore.config import Config

# from botocore.exceptions import (
#     EndpointConnectionError,
#     NoCredentialsError,
#     ParamValidationError,
# )

# import asyncio


def get_bedrock_client(
    assumed_role: Optional[str] = None,
    region: Optional[str] = None,
    runtime: Optional[bool] = True,
):
    """Create a boto3 client for Amazon Bedrock, with optional configuration overrides

    Parameters
    ----------
    assumed_role :
        Optional ARN of an AWS IAM role to assume for calling the Bedrock service. If not
        specified, the current active credentials will be used.
    region :
        Optional name of the AWS Region in which the service should be called (e.g. "us-east-1").
        If not specified, AWS_REGION or AWS_DEFAULT_REGION environment variable will be used.
    runtime :
        Optional choice of getting different client to perform operations with the Amazon Bedrock service.
    """
    if region is None:
        target_region = os.environ.get(
            "AWS_REGION", os.environ.get("AWS_DEFAULT_REGION")
        )
    else:
        target_region = region

    print(f"Create new client\n  Using region: {target_region}")

    # Get the access key and secret key from the environment variables
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

    os.environ.pop("AWS_PROFILE", None)
    os.environ.pop("AWS_DEFAULT_PROFILE", None)

    if not aws_access_key_id or not aws_secret_access_key:
        raise ValueError(
            "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set in environment variables"
        )

    retry_config = Config(
        region_name=target_region,
        retries={
            "max_attempts": 10,
            "mode": "standard",
        },
    )

    if runtime:
        service_name = "bedrock-runtime"
    else:
        service_name = "bedrock"

    print(f"Creating client with region: {target_region}")

    bedrock_client = boto3.client(
        service_name,
        region_name=target_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        config=retry_config,
    )

    print("boto3 Bedrock client successfully created!")
    print(bedrock_client._endpoint)
    return bedrock_client


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
        self.bedrock_client = get_bedrock_client(
            assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
            region=os.environ.get("AWS_DEFAULT_REGION", None),
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
        # print(f"pipe:{__name__}")

        # print(messages)
        # print(user_message)

        # allowed_roles = {"user", "assistant"}

        model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

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

            r = self.bedrock_client.invoke_model_with_response_stream(
                body=json.dumps(filtered_body), modelId=model_id
            )

            for event in r["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                if chunk["type"] == "content_block_delta":
                    yield chunk["delta"].get("text", "")

        except requests.exceptions.HTTPError as e:  # This will catch HTTP errors
            if r.status_code == 400:
                print(f"400 Bad Request received: {r.text}")
            else:
                print(f"HTTP Error: {e} Response: {r.text}")
            return f"Error with r: {e} ({r.text}) for body:\n{body}\nand filtered_body:\n{filtered_body}"
        except Exception as e:
            print(
                f"Error without r: {e} for body:\n{body}\nand filtered_body:\n{filtered_body}"
            )
            return f"Error without r: {e} for body:\n{body}\nand filtered_body:\n{filtered_body}"


# import logging

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)


# async def main():
#     pipeline = Pipeline()

#     await pipeline.on_startup()

#     model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
#     prompt = "Describe the purpose of a 'hello world' program in one line."
#     messages = [
#         {
#             "role": "user",
#             "content": [{"type": "text", "text": prompt}],
#         }
#     ]

#     body = {
#         "anthropic_version": "bedrock-2023-05-31",
#         "max_tokens": 512,
#         "temperature": 0.5,
#         "messages": messages,
#     }

#     r = pipeline.pipe(
#         user_message=prompt, model_id=model_id, messages=messages, body=body
#     )

#     for event in r:
#         print(event)

#     await pipeline.on_shutdown()


# # Run the example
# asyncio.run(main())
