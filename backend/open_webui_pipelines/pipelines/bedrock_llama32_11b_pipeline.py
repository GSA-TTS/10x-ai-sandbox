import json
import os
from typing import Generator, Iterator, List, Optional, Union
import time

from pydantic import BaseModel
from utils.pipelines.aws import bedrock_client
from botocore.exceptions import BotoCoreError
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def format_llama_prompt(body):
    messages = body.get("messages", [])
    formatted_prompt = "<|begin_of_text|>"

    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")
        formatted_prompt += (
            f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>"
        )

    formatted_prompt += "<|start_header_id|>assistant<|end_header_id|>"

    return formatted_prompt


class Pipeline:
    class Valves(BaseModel):
        AWS_REGION: Optional[str]
        BEDROCK_LLAMA3211B_ARN: Optional[str]

    def __init__(self):
        self.name = "Meta LLaMa 3.2 (11B)"
        self.valves = self.Valves(
            **{
                "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
                "BEDROCK_LLAMA3211B_ARN": os.getenv("BEDROCK_LLAMA3211B_ARN", None),
            }
        )
        self.bedrock_client = bedrock_client

    async def on_startup(self):
        logger.info(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        logger.info(f"on_shutdown:{__name__}")
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:

        formatted_prompt = format_llama_prompt(body)

        allowed_params = {"prompt", "temperature", "top_p", "max_gen_len"}

        if "user" in body and not isinstance(body["user"], str):
            body["user"] = (
                body["user"]["id"] if "id" in body["user"] else str(body["user"])
            )

        filtered_body = {k: v for k, v in body.items() if k in allowed_params}

        if len(body) != len(filtered_body):
            logger.info(
                f"Dropped params: {', '.join(set(body.keys()) - set(filtered_body.keys()))}"
            )

        if "max_gen_len" not in filtered_body:
            filtered_body["max_gen_len"] = 2048

        filtered_body["prompt"] = formatted_prompt

        request = json.dumps(filtered_body)

        model_id = self.valves.BEDROCK_LLAMA3211B_ARN

        generic_error_msg = f"## Oops! 🤖💔\n\n ### GSA Chat is having some trouble.\n\nPlease try another model _or_ wait a minute and try again."  # noqa E501
        rate_limit_error_msg = f"## Oops! 🤖💔\n\n ### Looks like GSA Chat has hit a service limit.\n\nPlease try another model _or_ wait a minute and try again."  # noqa E501

        try:
            r = self.bedrock_client.invoke_model_with_response_stream(
                body=request,
                modelId=model_id,
            )

            for event in r["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                if "generation" in chunk:
                    tokens = chunk["generation"]
                    yield tokens

        except self.bedrock_client.exceptions.AccessDeniedException as e:
            logger.error("Access Denied Exception:", e)
            yield generic_error_msg
        except self.bedrock_client.exceptions.ResourceNotFoundException as e:
            logger.error("Resource Not Found Exception:", e)
            yield generic_error_msg
        except self.bedrock_client.exceptions.ThrottlingException as e:
            logger.error("Throttling Exception:", e)
            yield rate_limit_error_msg
        except self.bedrock_client.exceptions.ModelTimeoutException as e:
            logger.error("Model Timeout Exception:", e)
            yield generic_error_msg
        except self.bedrock_client.exceptions.InternalServerException as e:
            logger.error("Internal Server Exception:", e)
            yield generic_error_msg
        except self.bedrock_client.exceptions.ServiceUnavailableException as e:
            logger.error("Service Unavailable Exception:", e)
            yield generic_error_msg
        except self.bedrock_client.exceptions.ModelStreamErrorException as e:
            logger.error("Model Stream Error Exception:", e)
            yield generic_error_msg
        except self.bedrock_client.exceptions.ValidationException as e:
            logger.error("Validation Exception:", e)
            yield generic_error_msg
        except self.bedrock_client.exceptions.ModelNotReadyException as e:
            logger.error("Model Not Ready Exception:", e)
            yield generic_error_msg
        except self.bedrock_client.exceptions.ServiceQuotaExceededException as e:
            logger.error(f"Service Quota Exceeded Exception: {e}")
            yield rate_limit_error_msg
        except self.bedrock_client.exceptions.ModelErrorException as e:
            logger.error("Model Error Exception:", e)
            yield generic_error_msg
        except BotoCoreError as e:
            logger.error(f"AWS BotoCoreError: {e}")
            yield generic_error_msg
        except Exception as e:
            logger.error(f"General Error: {e}")
            yield generic_error_msg
