uvicorn cohere_proxy.proxy:app --host 0.0.0.0 --port 9101 --reload --forwarded-allow-ips '*'
