# import datetime
import time
import json
import os
from typing import Generator, Iterator, List, Optional, Union

# import requests
from pydantic import BaseModel
from utils.pipelines.aws import bedrock_client
from botocore.exceptions import BotoCoreError

import random
import re

paterson = "I am load-testing bot, I only have one response. Please enjoy this poem by William Carlos Williams.\n\nPaterson lies in the valley under the Passaic Falls\nits spent waters forming the outline of his back. He\nlies on his right side, head near the thunder\nof the waters filling his dreams! Eternally asleep,\nhis dreams walk about the city where he persists\nincognito. Butterflies settle on his stone ear.\nImmortal he neither moves nor rouses and is seldom\nseen, though he breathes and the subtleties of his machinations\ndrawing their substance from the noise of the pouring river\nanimate a thousand automations. Who because they\nneither know their sources nor the sills of their\ndisappointments walk outside their bodies aimlessly\n    for the most part,\nlocked and forgot in their desires-unroused.\n\n  —Say it, no ideas but in things—\n  nothing but the blank faces of the houses\n  and cylindrical trees\n  bent, forked by preconception and accident—\n  split, furrowed, creased, mottled, stained—\n  secret—into the body of the light!\n\nFrom above, higher than the spires, higher\neven than the office towers, from oozy fields\nabandoned to gray beds of dead grass,\nblack sumac, withered weed-stalks,\nmud and thickets cluttered with dead leaves-\nthe river comes pouring in above the city\nand crashes from the edge of the gorge\nin a recoil of spray and rainbow mists-\n\n  (What common language to unravel?\n  . . .combed into straight lines\n  from that rafter of a rock's\n  lip.)\n\nA man like a city and a woman like a flower\n—who are in love. Two women. Three women.\nInnumerable women, each like a flower.\n\nBut\nonly one man—like a city.\n"  # noqa: E501


class Pipeline:
    class Valves(BaseModel):
        AWS_REGION: Optional[str]
        BEDROCK_CLAUDE_HAIKU_ARN: Optional[str]

    def __init__(self):
        self.name = "Load-test Mock Model"
        self.valves = self.Valves(
            **{
                "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
                "BEDROCK_CLAUDE_HAIKU_ARN": os.getenv("BEDROCK_CLAUDE_HAIKU_ARN", None),
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

        model_id = self.valves.BEDROCK_CLAUDE_HAIKU_ARN

        print(f"model_id: {model_id}")
        if "messages" in body:
            # remove messages with system role and insert content into body
            new_msgs = []
            for message in body["messages"]:
                if message["role"] == "user":
                    user_msg = message["content"]
                    # check if the request is for a title
                    if user_msg.startswith("Create a concise, 3-5 word title"):
                        yield "🖋Poem about New Jersey"
                        return ""
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

        # Claude likes a different format for images than OpenAI
        for message in filtered_body["messages"]:
            if message["role"] == "user":
                if isinstance(message["content"], list):
                    for content in message["content"]:
                        if content["type"] == "image_url":
                            content["type"] = "image"
                            image_type = (
                                content["image_url"]["url"].split(";")[0].split("/")[1]
                            )
                            data = content["image_url"]["url"].split(",")[1]
                            content["source"] = {
                                "type": "base64",  # base64
                                "media_type": f"image/{image_type}",  # i.e. image/jpeg
                                "data": data,
                            }
                            del content["image_url"]

        try:
            # r = self.bedrock_client.invoke_model_with_response_stream(
            #     body=json.dumps(filtered_body), modelId=model_id
            # )
            words = re.split(
                r"(\s+)", paterson
            )  # Split by spaces but keep the delimiters
            index = 0
            delays = [1, 1, 1, 5, 5, 5, 25, 25, 75, 300]
            while index < len(words):
                delay = random.choice(delays) / 1000
                time.sleep(delay)
                chunk_size = random.randint(1, 4)
                chunk = " ".join(words[index : index + chunk_size])
                yield chunk
                index += chunk_size

            # for event in r["body"]:
            #     event_type = list(event.keys())[0]  # Extract the first key in the event
            #     if event_type == "chunk":
            #         chunk = json.loads(event["chunk"]["bytes"])
            #         if chunk["type"] == "content_block_delta":
            #             yield chunk["delta"].get("text", "")
            #     else:
            #         # Handle different failure events
            #         error_message = event[event_type].get("message", "Unknown error")
            #         if event_type == "internalServerException":
            #             raise RuntimeError(f"Internal Server Error: {error_message}")
            #         elif event_type == "modelStreamErrorException":
            #             original_status = event[event_type].get(
            #                 "originalStatusCode", "Unknown"
            #             )
            #             original_message = event[event_type].get(
            #                 "originalMessage", "Unknown"
            #             )
            #             raise RuntimeError(
            #                 f"Model Stream Error ({original_status}): {original_message}"
            #             )
            #         elif event_type == "validationException":
            #             raise ValueError(f"Validation Error: {error_message}")
            #         elif event_type == "throttlingException":
            #             raise RuntimeError(f"Throttling Error: {error_message}")
            #         elif event_type == "modelTimeoutException":
            #             raise TimeoutError(f"Model Timeout: {error_message}")
            #         elif event_type == "serviceUnavailableException":
            #             raise RuntimeError(f"Service Unavailable: {error_message}")
            #         else:
            #             raise RuntimeError(
            #                 f"Unknown Event Type {event_type}: {error_message}"
            #             )

        except self.bedrock_client.exceptions.AccessDeniedException as e:
            print("Access Denied Exception:", e)
            raise e
        except self.bedrock_client.exceptions.ResourceNotFoundException as e:
            print("Resource Not Found Exception:", e)
            raise e
        except self.bedrock_client.exceptions.ThrottlingException as e:
            print("Throttling Exception:", e)
            raise e
        except self.bedrock_client.exceptions.ModelTimeoutException as e:
            print("Model Timeout Exception:", e)
            raise e
        except self.bedrock_client.exceptions.InternalServerException as e:
            print("Internal Server Exception:", e)
            raise e
        except self.bedrock_client.exceptions.ServiceUnavailableException as e:
            print("Service Unavailable Exception:", e)
            raise e
        except self.bedrock_client.exceptions.ModelStreamErrorException as e:
            print("Model Stream Error Exception:", e)
            raise e
        except self.bedrock_client.exceptions.ValidationException as e:
            print("Validation Exception:", e)
            raise e
        except self.bedrock_client.exceptions.ModelNotReadyException as e:
            print("Model Not Ready Exception:", e)
            raise e
        except self.bedrock_client.exceptions.ServiceQuotaExceededException as e:
            print("Service Quota Exceeded Exception:", e)
            raise e
        except self.bedrock_client.exceptions.ModelErrorException as e:
            print("Model Error Exception:", e)
            raise e
        except BotoCoreError as e:
            print(f"AWS BotoCoreError: {e}")
            raise e
        except Exception as e:
            print(f"General Error: {e}")
            raise e
