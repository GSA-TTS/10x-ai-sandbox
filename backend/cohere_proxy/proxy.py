import os
import json
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import botocore.exceptions

from utils.aws import bedrock_client


app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model_id = os.getenv("COHERE_EMBED_MODEL_ID", "You forgot to set COHERE_EMBED_MODEL_ID")


@app.post("/embeddings")
async def proxy_embeddings(request: Request):
    """Proxy endpoint for Cohere embeddings.
    This endpoint receives a request with input text and an optional embed_type,
    then forwards the request to the Cohere model on AWS Bedrock to get embeddings.
    For semantic search, the input_type should be search_document when embedding for storage and search_query when embedding for search.

    Args:
        request (Request): The incoming request containing the input text, model and optional embed_type.

    Returns:
        _type_ Response: A JSON response body containing the embeddings and usage information.
    """  # noqa E501
    try:
        body = await request.json()

        logger.debug(f"Cohere request body: {body}")

        body_input = body.get("input")
        input_type = body.get("embed_type", "search_query")

        tokens = 0
        for input in body_input:
            words = input.split(" ")
            tokens += len(words) / 0.75  # we can get accurate token count from tiktoken

        body = json.dumps({"texts": body_input, "input_type": input_type})

        response = bedrock_client.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json",
        )

        response_body = json.loads(response.get("body").read())
        embeddings = response_body.get("embeddings")

        response_obj = {}
        response_obj["model"] = model_id
        response_obj["usage"] = {}
        response_obj["usage"]["prompt_tokens"] = tokens
        response_obj["usage"]["total_tokens"] = tokens
        response_obj["data"] = []
        for e in embeddings:
            response_obj["data"].append(
                {
                    "object": "embedding",
                    "index": 0,
                    "embedding": e,
                }
            )

        return Response(
            content=json.dumps(response_obj),
            status_code=200,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.get("/health")
async def health():
    is_healthy = False
    try:
        model_can_paginate = bedrock_client.can_paginate("invoke_model")
        is_healthy = model_can_paginate is False  # False is the expected response
        return JSONResponse(
            status_code=200 if is_healthy else 500, content={"ok": is_healthy}
        )
    except botocore.exceptions.ClientError as e:
        logger.error(f"Bedrock client error: {e}")
        return False, f"Bedrock client error"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False, f"Unexpected error"
