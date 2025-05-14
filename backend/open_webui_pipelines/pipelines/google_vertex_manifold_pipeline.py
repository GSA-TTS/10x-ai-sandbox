import os
import json
from typing import Iterator, List, Union, Optional
import base64
import re
import traceback

from pydantic import BaseModel, Field

# Google Auth
from google.oauth2 import service_account

# Google GenAI SDK deps
from google import genai
from google.genai.types import (
    Content,
    GenerateContentConfig,
    GoogleSearch,
    HarmBlockThreshold,
    HarmCategory,
    Part,
    Image,
    HttpOptions,
    Tool,
)

from utils.pipelines.main import get_last_assistant_message


class Pipeline:
    """Google GenAI pipeline"""

    class Valves(BaseModel):
        """Options to change from the WebUI"""

        GOOGLE_PROJECT_ID: str = "You forgot to set GOOGLE_PROJECT_ID"
        GOOGLE_CLOUD_REGION: str = "You forgot to set GOOGLE_CLOUD_REGION"
        USE_PERMISSIVE_SAFETY: bool = Field(default=False)
        VERTEX_API_KEY_JSON: str = ""
        VERTEX_API_KEY_DICT: dict = {}

    def _clean_json_env(self, json_str: str) -> str:
        """Remove surrounding single quotes if present."""
        try:
            return json.loads(json_str)
        except Exception as e:
            print(
                f"error:\n{e}\nThis error occured parsing vertex api key json, attempting to recover..."
            )

        json_str = json_str.strip()
        if json_str.startswith("'") and json_str.endswith("'"):
            json_str = json_str[1:-1]
        return json.loads(json_str)

    def __init__(self):
        self.type = "manifold"
        self.name = "Google "

        raw_json = os.getenv("VERTEX_API_KEY_JSON", "")
        clean_json = self._clean_json_env(raw_json)

        self.valves = self.Valves(
            **{
                "GOOGLE_PROJECT_ID": os.getenv("GOOGLE_PROJECT_ID", ""),
                "GOOGLE_CLOUD_REGION": os.getenv("GOOGLE_CLOUD_REGION", "us-central1"),
                "USE_PERMISSIVE_SAFETY": False,
                "VERTEX_API_KEY_JSON": os.getenv(
                    "VERTEX_API_KEY_JSON",
                    "",
                ),
                "VERTEX_API_KEY_DICT": clean_json if clean_json else {},
            }
        )
        self.pipelines = [
            {"id": "gemini-2.0-flash", "name": "Gemini 2 Flash"},
            # {
            #     "id": "imagen-3.0-generate-002",
            #     "name": "Imagen 3 (image generation)",
            # },
            {"id": "gemini-2.5-pro-preview-03-25", "name": "Gemini 2.5 Pro"},
        ]
        self.genai_client = None
        self.credentials = None

    async def on_startup(self) -> None:
        """This function is called when the server is started."""

        print(f"on_startup:{__name__}")
        try:
            self.credentials = service_account.Credentials.from_service_account_info(
                self.valves.VERTEX_API_KEY_DICT,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        except KeyError:
            print("Error: VERTEX_API_KEY_JSON environment variable not set.")
            raise
        except json.JSONDecodeError:
            print("Error: VERTEX_API_KEY_JSON contains invalid JSON.")
            raise
        except Exception as e:
            print(f"Unexpected error initializing vertex AI client: {e}")
            raise

        if self.credentials:
            self.genai_client = genai.Client(
                vertexai=True,
                project=self.valves.GOOGLE_PROJECT_ID,
                location=self.valves.GOOGLE_CLOUD_REGION,
                credentials=self.credentials,
                http_options=HttpOptions(api_version="v1"),
            )

            response = self.genai_client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents="Please respond with 'hi' and nothing else.",
                config=GenerateContentConfig(
                    temperature=0.0,
                    top_p=1.0,
                ),
            )
            if "hi" in response.text.lower():
                print("GenAI Vertex client initialized successfully.")

    async def on_shutdown(self) -> None:
        """This function is called when the server is stopped."""
        print(f"on_shutdown:{__name__}")

    async def on_valves_updated(self) -> None:
        """This function is called when the valves are updated."""
        print(f"on_valves_updated:{__name__}")
        try:
            key_json = self.valves.VERTEX_API_KEY_JSON
            key_info = json.loads(key_json)
            self.credentials = service_account.Credentials.from_service_account_info(
                key_info,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        except KeyError:
            print("Error: VERTEX_API_KEY_JSON environment variable not set.")
            raise
        except json.JSONDecodeError:
            print("Error: VERTEX_API_KEY_JSON contains invalid JSON.")
            raise

        self.genai_client = genai.Client(
            vertexai=True,
            project=self.valves.GOOGLE_PROJECT_ID,
            location=self.valves.GOOGLE_CLOUD_REGION,
            credentials=self.credentials,
            http_options=HttpOptions(api_version="v1"),
        )

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Iterator]:
        try:
            self.credentials = service_account.Credentials.from_service_account_info(
                self.valves.VERTEX_API_KEY_DICT,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )

            if self.credentials.expired:
                print("GenAI credentials have expired")
                self.genai_client = genai.Client(
                    vertexai=True,
                    project=self.valves.GOOGLE_PROJECT_ID,
                    location=self.valves.GOOGLE_CLOUD_REGION,
                    credentials=self.credentials,
                    http_options=HttpOptions(api_version="v1"),
                )

            if not model_id.startswith("gemini-"):
                return f"Error: Invalid model name format: {model_id}"

            print(f"Pipe function called for model: {model_id}")

            system_message = next(
                (msg["content"] for msg in messages if msg["role"] == "system"), None
            )

            if body.get("title", False):  # If chat title generation is requested
                contents = [Content(role="user", parts=[Part(text=user_message)])]
            else:
                contents = self.build_conversation_history(messages)

            if self.valves.USE_PERMISSIVE_SAFETY:
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                }
            else:
                safety_settings = body.get("safety_settings")

            generation_config = GenerateContentConfig(
                system_instruction=system_message,
                temperature=body.get("temperature", 0.7),
                top_p=body.get("top_p", 0.9),
                top_k=body.get("top_k", 40),
                max_output_tokens=body.get("max_tokens", 8192),
                stop_sequences=body.get("stop", []),
                safety_settings=safety_settings,
                tools=[
                    Tool(google_search=GoogleSearch()),
                ],
            )

            for chunk in self.genai_client.models.generate_content_stream(
                model=model_id,
                contents=contents,
                config=generation_config,
            ):
                urls = []
                text_index_pairs = []
                for candidate in chunk.candidates:
                    if candidate.grounding_metadata:
                        if candidate.grounding_metadata.grounding_chunks:
                            for i, grounding_chunk in enumerate(
                                candidate.grounding_metadata.grounding_chunks
                            ):
                                web_uri = f"{grounding_chunk.web.uri}"
                                # domain = f"{grounding_chunk.web.domain}"
                                title = f"{grounding_chunk.web.title}"
                                markdown_link = f"[{title}]({web_uri})"
                                urls.append(markdown_link)
                        if candidate.grounding_metadata.grounding_supports:
                            for i, grounding_support in enumerate(
                                candidate.grounding_metadata.grounding_supports
                            ):
                                text_index_pairs.append(
                                    [
                                        grounding_support.segment.text,
                                        grounding_support.grounding_chunk_indices,
                                    ]
                                )

                    str_chunk = chunk.text
                    if text_index_pairs:
                        for text, indices in text_index_pairs:
                            md_links = ""
                            for index in indices:
                                if index < len(urls):
                                    url = urls[index]
                                    md_links += f", {url}" if md_links else f"{url}"

                            # TODO: use something like <ws_cite title=title domain=domain url=url text=text />
                            citation = f"\n<ws_text>{text}<ws_url>{md_links}</ws_url></ws_text>"
                            str_chunk += citation
                    yield str_chunk

        except Exception as e:
            print(f"Error generating content: {e}\n{traceback.print_exc()}")
            return f"An error occurred: {str(e)}"

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"outlet:{__name__}")

        messages = body["messages"]
        assistant_message = get_last_assistant_message(messages)
        new_assistant_message = None

        if "<ws_text>" in assistant_message:
            # find web search citations
            pattern = re.compile(
                r"<ws_text>(?P<text>.*?)<ws_url>(?P<url>.*?)</ws_url></ws_text>",
                re.DOTALL,
            )

            pairs = [
                (m.group("text"), m.group("url"))
                for m in pattern.finditer(assistant_message)
            ]

            # remove web search citations from the assistant message
            new_assistant_message = pattern.sub("", assistant_message)

            sources = []
            for text, url in pairs:
                urls = url.split(", ")

                inline_md_links = []
                for url in urls:
                    if url not in sources:
                        sources.append(url)

                    match = re.match(r"\[(?P<title>.*?)\]\((?P<uri>.*?)\)", url)
                    if match:
                        # title = match.group("title")
                        web_uri = match.group("uri")
                        idx = sources.index(url) + 1
                        inline_md_link = f"[{idx}]({web_uri})"
                        inline_md_links.append(inline_md_link)

                # TODO: unwanted whitespaces after links are added by the md parser on front-end...
                if inline_md_links:
                    inline_md_links = ", ".join(inline_md_links)
                    print(f"inline_md_links: |{inline_md_links}|")
                else:
                    inline_md_links = url

                new_assistant_message = new_assistant_message.replace(
                    text, f"{text} [{inline_md_links}]"
                )
                print(f"new_assistant_message: |{new_assistant_message}|")

            new_assistant_message += f"\nSources:\n"
            for i, url in enumerate(sources):
                new_assistant_message += f"{i+1}. {url}\n"

        if new_assistant_message:
            assistant_message = new_assistant_message

        for message in reversed(messages):
            if message["role"] == "assistant":
                message["content"] = assistant_message
                break

        body = {**body, "messages": messages}
        return body

    def stream_response(self, response):
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def build_conversation_history(self, messages: List[dict]) -> List[Content]:
        contents = []

        for message in messages:
            if message["role"] == "system":
                continue

            parts = []

            if isinstance(message.get("content"), list):
                for content in message["content"]:
                    if content["type"] == "text":
                        parts.append(Part(text=content["text"]))
                    elif content["type"] == "image_url":
                        image_url = content["image_url"]["url"]
                        if image_url.startswith("data:image"):
                            image_data = image_url.split(",")[1]
                            image_bytes = base64.b64decode(image_data)
                            vertex_image = Image.from_bytes(data=image_bytes)
                            parts.append(Part.from_image(vertex_image))
                        else:
                            parts.append(Part.from_uri(image_url))
            else:
                parts = [Part(text=message["content"])]

            role = "user" if message["role"] == "user" else "model"
            contents.append(Content(role=role, parts=parts))

        return contents
