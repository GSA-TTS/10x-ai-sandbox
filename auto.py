#!/usr/bin/env python3
import subprocess
import json
import sys
import os

from backend.open_webui_pipelines.utils.pipelines.aws import bedrock_client


def get_latest_commit():
    print("Getting the latest commit...\n")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error getting the latest commit", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def get_branch_diff():
    print("Getting the diff that will be merged into main...\n")

    # First, fetch the latest from origin to ensure we have current data
    subprocess.run(["git", "fetch", "origin"], capture_output=True, text=True)

    # Find the merge base (common ancestor) between main and current branch
    merge_base_result = subprocess.run(
        ["git", "merge-base", "origin/main", "HEAD"], capture_output=True, text=True
    )
    if merge_base_result.returncode != 0:
        print("Error finding merge base", file=sys.stderr)
        sys.exit(1)

    merge_base = merge_base_result.stdout.strip()

    # Get the diff between merge-base and current branch HEAD
    # This shows only what your branch adds compared to where it branched from main
    result = subprocess.run(
        ["git", "diff", merge_base, "HEAD"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error getting the diff", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def get_json_diff(diff):
    print("Jsonifying the diff...\n")
    latest_commit = get_latest_commit()
    diff_output = diff
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
{get_json_diff(get_branch_diff())}
</diff_json>
And here's the template:
<pr_template>
{get_pr_template()}
</pr_template>
The PR title should begin with one of the following in all caps: [BUGFIX, FEATURE, TASK, DEVOPS, INFRA, DOCS]. Please provide your response in the following format:
<pr_title>
...title
</pr_title>
<pr_description>
...description
</pr_description>
Do not include any other text or explanations. Just the title and description between each set of tags.
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

    print("Sending diff to the model for interpretation...\n")
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


def get_current_branch():
    print("Getting current branch...\n")
    result = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error getting current branch", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def create_pull_request():
    pr_title, pr_description = get_pr_description()
    pr_description += "\n\n_NOTE:_ This PR description was auto-generated. Please review the changes and ensure the description is accurate before merging."  # noqa: E501
    print("Generating PR title and description...\n")
    print("✨ Check out the suggested PR description below ✨\n")
    print(f"{pr_title}\n")
    print(pr_description)
    print("✨ Check out the suggested PR description above ✨\n")
    current_branch = get_current_branch()
    target_branch = "main"

    print(f"Creating PR from {current_branch} into {target_branch}...\n")

    # Get repo information to be explicit
    repo_url_result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"], capture_output=True, text=True
    )
    repo_url = repo_url_result.stdout.strip()

    # Extract owner/repo format from git URL
    # Works for both SSH (git@github.com:owner/repo.git) and HTTPS (https://github.com/owner/repo.git)
    if "github.com:" in repo_url:
        repo_path = repo_url.split("github.com:")[1].split(".git")[0]
    else:
        repo_path = repo_url.split("github.com/")[1].split(".git")[0]

    result = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            pr_title,
            "--body",
            pr_description,
            "--base",
            target_branch,
            "--head",
            current_branch,
            "--repo",
            repo_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        try:
            print(
                f"Error creating PR from {current_branch} into {target_branch}:\n{result.stderr}",
                file=sys.stderr,
            )
        except Exception as e:
            print(
                f"Error {e} creating PR from {current_branch} into {target_branch}:\n{result}",
                file=sys.stderr,
            )
        finally:
            sys.exit(1)
    print("\n✨ PR created successfully! ✨")


def get_commit_diff():
    print("\nGetting the staged diff...\n")
    result = subprocess.run(
        ["git", "diff", "HEAD", "--cached"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error getting the diff", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def generate_commit_message_prompt():
    commit_diff = get_commit_diff()
    json_diff = get_json_diff(commit_diff)
    # could enforce a schema response instead of just asking nicely for tags
    return f"""
Take a look at the following diff and suggest a clear and meaningful commit message. Here's the dif as json:
<diff_json>
{json_diff}
</diff_json>
And here's the template:
<commit_message>
...commit message
</commit_message>
Do not include any other text or explanations. Just the commit message between the tags.
"""  # noqa: E501


def generate_commit_message():
    filtered_body = {
        "messages": [
            {
                "role": "user",
                "content": generate_commit_message_prompt(),
            }
        ],
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
    }

    print("Sending diff to the model for interpretation...\n")
    model_id = os.getenv("BEDROCK_CLAUDE_ARN", None)
    r = bedrock_client.invoke_model_with_response_stream(
        body=json.dumps(filtered_body), modelId=model_id
    )

    commit_message = ""
    for event in r["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk["type"] == "content_block_delta":
            commit_message += chunk["delta"].get("text", "")

    commit_message = commit_message.split("<commit_message>")[1].split(
        "</commit_message>"
    )[0]
    return commit_message


def create_commit():
    commit_msg = generate_commit_message()
    commit_message = f"{commit_msg.strip()} -autogenerated"
    print("✨ Generating commit message... ✨\n")
    print(commit_message)
    result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        try:
            print(
                f"Error creating commit:\n{result.stderr}",
                file=sys.stderr,
            )
        except Exception as e:
            print(
                f"Error {e} creating commit:\n{result}",
                file=sys.stderr,
            )
        finally:
            sys.exit(1)
    print("\n✨ Commit created successfully! ✨\n")


def push_commit():
    current_branch = get_current_branch()
    print(f"Pushing commit from {current_branch} to remote...\n")
    result = subprocess.run(
        ["git", "push", "origin", current_branch],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        try:
            print(
                f"Error pushing commit:\n{result.stderr}",
                file=sys.stderr,
            )
        except Exception as e:
            print(
                f"Error {e} pushing commit:\n{result}",
                file=sys.stderr,
            )
        finally:
            sys.exit(1)
    print("✨ Commit pushed successfully! ✨\n")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("pr", "commit"):
        print("Usage: auto_pr.py [pr|commit]", file=sys.stderr)
        sys.exit(1)
    mode = sys.argv[1]
    if mode == "pr":
        create_pull_request()
    elif mode == "commit":
        create_commit()
        push_commit()


if __name__ == "__main__":
    main()
