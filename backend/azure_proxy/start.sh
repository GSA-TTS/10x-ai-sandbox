uvicorn azure_proxy.proxy:app --host 0.0.0.0 --port 9100 --reload --forwarded-allow-ips '*'
