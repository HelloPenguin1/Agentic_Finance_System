import os
from dotenv import load_dotenv
load_dotenv()

from litellm import completion
from output_val.structured_outputs import queryDecompose
from prompts.query_prompt import query_prompt
from langchain_openai import OpenAIEmbeddings

MODEL1 = "groq/openai/gpt-oss-20b"
EMBEDDING_MODEL = OpenAIEmbeddings(model="text-embedding-3-small")


def querydecomposer(query):
    response = completion(
    model = MODEL1,
    temperature=0,
    messages=[
        {"role":"system",
         "content": query_prompt},
        {"role":"user",
         "content":query}],
    response_format = queryDecompose
    )
    return queryDecompose.model_validate_json(
        response.choices[0].message.content
    )
    
def main():
    test_text = "This is a test sentence for embedding."
    try:
        embedding = fin_embedding.embed_query(test_text)
        print(f"Embedding successful for text: {test_text}")
        print(f"Embedding length: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
    except Exception as e:
        print(f"Embedding failed: {e}")


if __name__ == "__main__":
    main()
