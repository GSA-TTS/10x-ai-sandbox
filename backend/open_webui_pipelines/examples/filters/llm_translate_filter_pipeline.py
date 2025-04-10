# from typing import List, Optional
# from schemas import OpenAIChatMessage
# from pydantic import BaseModel
# import requests
# import os

# from utils.pipelines.main import get_last_user_message, get_last_assistant_message


# class Pipeline:
#     class Valves(BaseModel):
#         # List target pipeline ids (models) that this filter will be connected to.
#         # If you want to connect this filter to all pipelines, you can set pipelines to ["*"]
#         # e.g. ["llama3:latest", "gpt-3.5-turbo"]
#         pipelines: List[str] = []

#         # Assign a priority level to the filter pipeline.
#         # The priority level determines the order in which the filter pipelines are executed.
#         # The lower the number, the higher the priority.
#         priority: int = 0

#         OPENAI_API_BASE_URL: str = "https://api.openai.com/v1"
#         OPENAI_API_KEY: str = ""
#         TASK_MODEL: str = "gpt-3.5-turbo"

#         # Source and target languages
#         # User message will be translated from source_user to target_user
#         source_user: Optional[str] = "auto"
#         target_user: Optional[str] = "en"

#         # Assistant languages
#         # Assistant message will be translated from source_assistant to target_assistant
#         source_assistant: Optional[str] = "en"
#         target_assistant: Optional[str] = "es"

#     def __init__(self):
#         # Pipeline filters are only compatible with Open WebUI
#         # You can think of filter pipeline as a middleware that can be used to edit the form data before it is sent to the OpenAI API.
#         self.type = "filter"

#         # Optionally, you can set the id and name of the pipeline.
#         # Best practice is to not specify the id so that it can be automatically inferred from the filename, so that users can install multiple versions of the same pipeline.
#         # The identifier must be unique across all pipelines.
#         # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
#         # self.id = "libretranslate_filter_pipeline"
#         self.name = "LLM Translate Filter"

#         # Initialize
#         self.valves = self.Valves(
#             **{
#                 "pipelines": ["*"],  # Connect to all pipelines
#                 "OPENAI_API_KEY": os.getenv(
#                     "OPENAI_API_KEY", "your-openai-api-key-here"
#                 ),
#             }
#         )

#         pass

#     async def on_startup(self):
#         # This function is called when the server is started.
#         print(f"on_startup:{__name__}")
#         pass

#     async def on_shutdown(self):
#         # This function is called when the server is stopped.
#         print(f"on_shutdown:{__name__}")
#         pass

#     async def on_valves_updated(self):
#         # This function is called when the valves are updated.
#         pass

#     def translate(self, text: str, source: str, target: str) -> str:
#         headers = {}
#         headers["Authorization"] = f"Bearer {self.valves.OPENAI_API_KEY}"
#         headers["Content-Type"] = "application/json"

#         payload = {
#             "messages": [
#                 {
#                     "role": "system",
#                     "content": f"Translate the following text to {target}. Provide only the translated text and nothing else.",
#                 },
#                 {"role": "user", "content": text},
#             ],
#             "model": self.valves.TASK_MODEL,
#         }
#         print(payload)

#         try:
#             r = requests.post(
#                 url=f"{self.valves.OPENAI_API_BASE_URL}/chat/completions",
#                 json=payload,
#                 headers=headers,
#                 stream=False,
#             )

#             r.raise_for_status()
#             response = r.json()
#             print(response)
#             return response["choices"][0]["message"]["content"]
#         except Exception as e:
#             return f"Error: {e}"

#     async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
#         print(f"inlet:{__name__}")

#         messages = body["messages"]
#         user_message = get_last_user_message(messages)

#         print(f"User message: {user_message}")

#         # Translate user message
#         translated_user_message = self.translate(
#             user_message,
#             self.valves.source_user,
#             self.valves.target_user,
#         )

#         print(f"Translated user message: {translated_user_message}")

#         for message in reversed(messages):
#             if message["role"] == "user":
#                 message["content"] = translated_user_message
#                 break

#         body = {**body, "messages": messages}
#         return body

#     async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
#         if "title" in body:
#             return body

#         print(f"outlet:{__name__}")

#         messages = body["messages"]
#         assistant_message = get_last_assistant_message(messages)

#         print(f"Assistant message: {assistant_message}")

#         # Translate assistant message
#         translated_assistant_message = self.translate(
#             assistant_message,
#             self.valves.source_assistant,
#             self.valves.target_assistant,
#         )

#         print(f"Translated assistant message: {translated_assistant_message}")

#         for message in reversed(messages):
#             if message["role"] == "assistant":
#                 message["content"] = translated_assistant_message
#                 break

#         body = {**body, "messages": messages}
#         return body
