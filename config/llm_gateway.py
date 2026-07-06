import os
from dotenv import load_dotenv
load_dotenv()

from litellm import completion
from output_val.structured_outputs import queryDecompose
from prompts.query_prompt import query_prompt

MODEL1 = "groq/openai/gpt-oss-20b"


def querydecomposer(query):
    response = completion(
    model = MODEL1,
    temperature=0,
    messages=[
        {"role":"system",
         "content": query_prompt},
        {"role":"user",
         "content":query}],
    response_format = queryDecompose,
    )
    return queryDecompose.model_validate_json(
        response.choices[0].message.content
    )

def main():
    test_query = "vdbv AAPLE 2008-09-20"
    try:
        response = querydecomposer(test_query)
        print("LLM check succeeded.")
        print(response.choices[0].message.content['company'])
    except Exception as exc:
        print(f"LLM check failed: {exc}")


if __name__ == "__main__":
    main()
