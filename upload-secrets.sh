# Define your repository
REPO="GSA-TTS/temp-10x-ai-sandbox"

# Upload secrets
gh secret set OLLAMA_BASE_URL -b"$(grep OLLAMA_BASE_URL .env | cut -d '=' -f2-)" --repo $REPO
gh secret set WEBUI_NAME -b"$(grep WEBUI_NAME .env | cut -d '=' -f2-)" --repo $REPO
gh secret set SCARF_NO_ANALYTICS -b"$(grep SCARF_NO_ANALYTICS .env | cut -d '=' -f2-)" --repo $REPO
gh secret set DO_NOT_TRACK -b"$(grep DO_NOT_TRACK .env | cut -d '=' -f2-)" --repo $REPO
gh secret set ANONYMIZED_TELEMETRY -b"$(grep ANONYMIZED_TELEMETRY .env | cut -d '=' -f2-)" --repo $REPO
gh secret set GITHUBLOCAL_CLIENT_ID -b"$(grep GITHUBLOCAL_CLIENT_ID .env | cut -d '=' -f2-)" --repo $REPO
gh secret set GITHUBLOCAL_CLIENT_SECRET -b"$(grep GITHUBLOCAL_CLIENT_SECRET .env | cut -d '=' -f2-)" --repo $REPO
gh secret set AWS_ACCESS_KEY_ID -b"$(grep AWS_ACCESS_KEY_ID .env | cut -d '=' -f2-)" --repo $REPO
gh secret set AWS_SECRET_ACCESS_KEY -b"$(grep AWS_SECRET_ACCESS_KEY .env | cut -d '=' -f2-)" --repo $REPO
gh secret set AWS_DEFAULT_REGION -b"$(grep AWS_DEFAULT_REGION .env | cut -d '=' -f2-)" --repo $REPO
gh secret set AZURE_OPENAI_API_KEY -b"$(grep AZURE_OPENAI_API_KEY .env | cut -d '=' -f2-)" --repo $REPO
gh secret set AZURE_OPENAI_ENDPOINT -b"$(grep AZURE_OPENAI_ENDPOINT .env | cut -d '=' -f2-)" --repo $REPO
gh secret set AZURE_OPENAI_GPT35TURBO_DEPLOYMENT_NAME -b"$(grep AZURE_OPENAI_GPT35TURBO_DEPLOYMENT_NAME .env | cut -d '=' -f2-)" --repo $REPO
gh secret set AZURE_OPENAI_GPT4OMNI_DEPLOYMENT_NAME -b"$(grep AZURE_OPENAI_GPT4OMNI_DEPLOYMENT_NAME .env | cut -d '=' -f2-)" --repo $REPO
gh secret set WEBUI_SECRET_KEY -b"$(grep WEBUI_SECRET_KEY .env | cut -d '=' -f2-)" --repo $REPO
gh secret set ADMIN_USER_EMAIL -b"$(grep ADMIN_USER_EMAIL .env | cut -d '=' -f2-)" --repo $REPO
gh secret set ADMIN_USER_PASSWORD -b"$(grep ADMIN_USER_PASSWORD .env | cut -d '=' -f2-)" --repo $REPO
