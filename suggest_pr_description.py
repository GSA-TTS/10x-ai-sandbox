#!/usr/bin/env python3
import subprocess
import json
import sys
import os

from backend.open_webui_pipelines.utils.pipelines.aws import bedrock_client


def get_latest_commit():
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error getting the latest commit", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def get_diff():
    result = subprocess.run(
        ["git", "diff", "main", "HEAD"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error getting the diff", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def get_json_diff():
    latest_commit = get_latest_commit()
    diff_output = get_diff()
    data = {"latest_commit": latest_commit, "diff": diff_output}
    json_diff = json.dumps(data, indent=4)
    return json_diff


def get_pr_template():
    # load pr template from file
    with open("./.github/pull_request_template.md", "r") as f:
        pr_template = f.read()
    return pr_template


def get_pr_description_prompt():
    return f"""
Take a look at the following diff and suggest a well-formatted PR description that abides by my PR template. I'll give you the dif and then the template. Here's the dif as json:
<diff_json>
{get_json_diff()}
</diff_json>
And here's the template:
<pr_template>
{get_pr_template()}
</pr_template>
Please provide your response in the following format:
<pr_description>
...description
</pr_description>
Do not include any other text or explanations. Just the description between the tags.
"""  # noqa: E501


def get_pr_description():
    filtered_body = {
        "messages": [
            {
                "role": "user",
                "content": get_pr_description_prompt(),
            }
        ],
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
    }

    model_id = os.getenv("BEDROCK_CLAUDE_ARN", None)
    r = bedrock_client.invoke_model_with_response_stream(
        body=json.dumps(filtered_body), modelId=model_id
    )

    pr_description = ""
    for event in r["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk["type"] == "content_block_delta":
            pr_description += chunk["delta"].get("text", "")

    pr_description = pr_description.split("<pr_description>")[1].split(
        "</pr_description>"
    )[0]
    return pr_description


def main():
    print("Generating PR description...")
    print(get_pr_description())
    print("✨ Check out the suggested PR description above ✨")
    print("🚀 If you like it, feel free to copy and paste it into your PR! 🎉")


if __name__ == "__main__":
    main()
