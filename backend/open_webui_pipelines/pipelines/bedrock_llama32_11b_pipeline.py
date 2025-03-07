import json
import os
from typing import Generator, Iterator, List, Optional, Union

import requests
from pydantic import BaseModel
from utils.pipelines.aws import bedrock_client


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
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
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
            print(
                f"Dropped params: {', '.join(set(body.keys()) - set(filtered_body.keys()))}"
            )

        if "max_gen_len" not in filtered_body:
            filtered_body["max_gen_len"] = 2048

        filtered_body["prompt"] = formatted_prompt

        request = json.dumps(filtered_body)

        model_id = self.valves.BEDROCK_LLAMA3211B_ARN

        try:
            r = self.bedrock_client.invoke_model_with_response_stream(
                body=request,
                modelId=model_id,
            )

        except requests.exceptions.HTTPError as e:
            if r.status_code == 400:
                print(f"400 Bad Request received: {r.text}")
            else:
                print(f"HTTP Error: {e} Response: {r.text}")
            return f"Error with r: {e} ({r.text}) for body:\n{body}\nand filtered_body:\n{filtered_body}"
        except requests.exceptions.HTTPError as e:
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

        try:
            for event in r["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                if "generation" in chunk:
                    yield chunk["generation"]

        except Exception as e:
            if r:
                print(f"Error iterating r: {e} for r:\n{r}")
            print(f"Error iterating r: {e} for filtered_body:\n{filtered_body}")
            return f"Error iterating r: {e} for filtered_body:\n{filtered_body}"
