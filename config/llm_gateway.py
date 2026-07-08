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
    
    return None

if __name__ == "__main__":
    main()
