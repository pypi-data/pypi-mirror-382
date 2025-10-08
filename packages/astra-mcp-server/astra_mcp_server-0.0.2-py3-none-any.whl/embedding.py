import os
import requests

EMBEDDING_PROVIDER = {
    "text-embedding-3-small": "openai",
    "text-embedding-3-large": "openai",
    "text-embedding-ada-002": "openai",
    "all-minilm-l6-v2": "ibm-watsonx",
    "granite-embedding-107m-multilingual": "ibm-watsonx",
    "granite-embedding-278m-multilingual": "ibm-watsonx",
    "ms-marco-minilm-l-12-v2": "ibm-watsonx",
    "multilingual-e5-large": "ibm-watsonx",
    "slate-30m-english-rtrvr-v2": "ibm-watsonx",
    "slate-30m-english-rtrvr": "ibm-watsonx",
    "slate-125m-english-rtrvr-v2": "ibm-watsonx",
    "slate-125m-english-rtrvr": "ibm-watsonx"
}

def generate_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    if EMBEDDING_PROVIDER[model] == "openai":
        return generate_embedding_openai(text, model)
    elif EMBEDDING_PROVIDER[model] == "ibm-watsonx":
        return generate_embedding_ibm_watsonx(text, model)
    else:
        raise ValueError(f"Unsupported embedding model: {model}")

def generate_embedding_ibm_watsonx(text: str, model: str = "granite-embedding-278m-multilingual") -> list[float]:
    """ 
    Generate an embedding using the IBM Watsonx REST API without using the SDK.
    Environment variables required:
      - IBM_WATSONX_BASE_URL: the base URL of the IBM Watsonx endpoint (e.g., https://{cluster_url}/ml/v1/text/embeddings?version=2023-10-25)
      - IBM_WATSONX_API_KEY: your API key
      - IBM_WATSONX_PROJECT_ID: your project ID
    """
    base_url = os.getenv("IBM_WATSONX_BASE_URL")
    api_key = os.getenv("IBM_WATSONX_API_KEY")
    project_id = os.getenv("IBM_WATSONX_PROJECT_ID")

    if not base_url or not api_key or not project_id:
        raise EnvironmentError("Missing IBM_WATSONX_BASE_URL or IBM_WATSONX_API_KEY or IBM_WATSONX_PROJECT_ID environment variables.")

    url = f"{base_url.rstrip('/')}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model_id": model,
        "inputs": [text],
        "project_id": os.getenv("IBM_WATSONX_PROJECT_ID")
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    return data["results"][0]["embedding"]

def generate_embedding_openai(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """
    Generate an embedding using the OpenAI REST API without using the SDK.

    Environment variables required:
      - OPENAI_API_KEY: your API key
      - OPENAI_BASE_URL: the base URL of the OpenAI endpoint (e.g., https://api.openai.com/v1)
    """
    base_url = os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    api_key = os.getenv("OPENAI_API_KEY")

    if not base_url or not api_key:
        raise EnvironmentError("Missing OPENAI_BASE_URL or OPENAI_API_KEY environment variables.")

    url = f"{base_url.rstrip('/')}/embeddings"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": model,
        "input": text,
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    return data["data"][0]["embedding"]


