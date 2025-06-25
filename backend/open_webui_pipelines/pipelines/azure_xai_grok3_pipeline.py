from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import requests
import os
import structlog


logger = structlog.get_logger(__name__)


class Pipeline:
    class Valves(BaseModel):
        XAI_GROK3_API_KEY: str
        XAI_GROK3_API_URL: str
        AZURE_OPENAI_API_VERSION: str

    def __init__(self):
        logger.info("Initializing pipeline")

        self.name = "Grok 3"
        self.valves = self.Valves(
            **{
                "XAI_GROK3_API_KEY": os.getenv(
                    "XAI_GROK3_API_KEY", "your-xai-grok3-api-key-here"
                ),
                "XAI_GROK3_API_URL": os.getenv(
                    "XAI_GROK3_API_URL", "your-xai-grok3-url-here"
                ),
                "AZURE_OPENAI_API_VERSION": os.getenv(
                    "AZURE_OPENAI_API_VERSION", "2024-02-01"
                ),
            }
        )
        pass

    async def on_startup(self):
        # This function is called when the server is started.
        logger.info("on_startup")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        logger.info("on_shutdown")
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        logger.info("xAI Grok3 pipe method called")

        headers = {
            "api-key": self.valves.XAI_GROK3_API_KEY,
            "Content-Type": "application/json",
        }

        url = (
            f"{self.valves.XAI_GROK3_API_URL}/chat/completions"
            + f"?api-version={self.valves.AZURE_OPENAI_API_VERSION}"
        )

        allowed_params = {
            "messages",
            "temperature",
            "role",
            "content",
            "contentPart",
            "contentPartImage",
            "enhancements",
            "dataSources",
            "n",
            "stream",
            "stop",
            "max_tokens",
            "presence_penalty",
            "frequency_penalty",
            "logit_bias",
            "user",
            "function_call",
            "functions",
            "tools",
            "tool_choice",
            "top_p",
            "log_probs",
            "top_logprobs",
            "response_format",
            "seed",
        }

        # remap user field
        if "user" in body and not isinstance(body["user"], str):
            body["user"] = (
                body["user"]["id"] if "id" in body["user"] else str(body["user"])
            )

        filtered_body = {k: v for k, v in body.items() if k in allowed_params}

        # log fields that were filtered out as a single line
        if len(body) != len(filtered_body):
            logger.info(
                "Dropped params", params=(set(body.keys()) - set(filtered_body.keys()))
            )
        r = None
        generic_error_msg = f"## Oops! 🤖💔\n\n ### GSA Chat is having some trouble.\n\nPlease try another model _or_ wait a minute and try again."  # noqa E501
        rate_limit_error_msg = f"## Oops! 🤖💔\n\n ### Looks like GSA Chat has hit a service limit.\n\nPlease try another model _or_ wait a minute and try again."  # noqa E501

        try:
            r = requests.post(
                url=url,
                json=filtered_body,
                headers=headers,
                stream=True,
            )

            r.raise_for_status()
            if body["stream"]:
                return r.iter_lines()
            else:
                return r.json()

        except Exception as e:
            exception_name = type(e).__name__
            error_str = str(e).lower()
            logger.error(error_str)

            # Check for rate limiting patterns
            is_rate_limit_exception = exception_name in [
                "ThrottlingException",
                "ServiceQuotaExceededException",
            ]
            has_rate_limit_keywords = any(
                keyword in error_str
                for keyword in ["throttl", "rate", "quota", "limit"]
            )

            if is_rate_limit_exception or has_rate_limit_keywords:
                yield rate_limit_error_msg
            else:
                yield generic_error_msg
