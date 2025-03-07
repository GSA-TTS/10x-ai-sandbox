#!/usr/bin/env python3
import subprocess
import json
import sys
import os

from backend.open_webui_pipelines.utils.pipelines.aws import bedrock_client


def get_latest_commit():
    print("Getting the latest commit...")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error getting the latest commit", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def get_diff():
    print("Getting the diff...")
    result = subprocess.run(
        ["git", "diff", "main", "HEAD"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error getting the diff", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def get_json_diff():
    print("Jsonifying the diff...")
    latest_commit = get_latest_commit()
    diff_output = get_diff()
    data = {"latest_commit": latest_commit, "diff": diff_output}
    json_diff = json.dumps(data, indent=4)
    return json_diff


def get_pr_template():
    with open("./.github/pull_request_template.md", "r") as f:
        pr_template = f.read()
    return pr_template


def get_pr_description_prompt():
    # could enforce a schema response instead of just asking nicely for tags
    return f"""
Take a look at the following diff and suggest a well-formatted PR title and description that abides by my PR template. I'll give you the dif and then the template. Here's the dif as json:
<diff_json>
{get_json_diff()}
</diff_json>
And here's the template:
<pr_template>
{get_pr_template()}
</pr_template>
Please provide your response in the following format:
<pr_title>
...title
</pr_title>
<pr_description>
...description
</pr_description>
Do not include any other text or explanations. Just the title and description between each set of tags.
"""  # noqa: E501


def get_pr_description():
    print("Sending diff to the model for interpretation...")
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

    pr_title = pr_description.split("<pr_title>")[1].split("</pr_title>")[0]
    pr_description = pr_description.split("<pr_description>")[1].split(
        "</pr_description>"
    )[0]
    return pr_title, pr_description


def main():
    pr_title, pr_description = get_pr_description()
    print("Generating PR description...")
    print(pr_description)
    print("✨ Check out the suggested PR description above ✨\n")
    # print("🚀 If you like it, feel free to copy and paste it into your PR! 🎉")
    # create PR from current branch to main
    result = subprocess.run(
        ["gh", "pr", "create", "--title", pr_title, "--body", pr_description],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        try:
            print(f"Error creating PR:\n{result.stderr}", file=sys.stderr)
        except:
            print(f"Error creating PR: {result}", file=sys.stderr)
        finally:
            sys.exit(1)
    print("✨ PR created successfully! ✨")


if __name__ == "__main__":
    main()
