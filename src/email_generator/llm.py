import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_openai import AzureChatOpenAI


load_dotenv()


azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
azure_deployment = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]


credential = DefaultAzureCredential()

token_provider = get_bearer_token_provider(
    credential,
    "https://cognitiveservices.azure.com/.default",
)


llm = AzureChatOpenAI(
    azure_endpoint=azure_endpoint,
    azure_deployment=azure_deployment,
    api_version="2025-04-01-preview",
    azure_ad_token_provider=token_provider,
    temperature=1,
)


if __name__ == "__main__":
    response = llm.invoke(
        "Say hello in one sentence."
    )

    print(response.content)
