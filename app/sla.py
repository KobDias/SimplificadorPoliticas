from promptlayer import PromptLayer
import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

# Initialize the PromptLayer client
pl_key = os.getenv("PROMPTLAYER_API_KEY")
ml_key = os.getenv("MISTRAL_API_KEY")
print(f"PromptLayer API Key: {pl_key}")
print(f"Mistral API Key: {ml_key}")
# promptlayer_client = PromptLayer(api_key=pl_key)

from promptlayer import PromptLayer
pl = PromptLayer(api_key=pl_key)
pl.api_key = pl_key

try:
    response = pl.run(
        model="mistral",  # Especifique o modelo aqui, se suportado
        prompt="Quais são as principais características do Mistral?"
    )
    print(response)
except Exception as e:
    print(f"Erro ao executar o prompt: {e}")

# Access the Mistral model
# Mistral = promptlayer_client.mistral.Mistral(api_key=ml_key)

# # Create a client instance for Mistral
# client = Mistral()

# # Example usage of the Mistral client
# response = client.invoke({"question": "What are the key features of Mistral?"})
# print(response)