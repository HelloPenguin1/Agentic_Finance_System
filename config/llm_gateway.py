import os
from dotenv import load_dotenv
load_dotenv()

from litellm import completion
from output_val.structured_outputs import queryDecompose, sectionOutput
from prompts.query_prompt import query_prompt
from langchain_openai import OpenAIEmbeddings

MODEL1 = "groq/openai/gpt-oss-20b"
EMBEDDING_MODEL = OpenAIEmbeddings(model="text-embedding-3-small")


def querydecomposer(query):
    response = completion(
    model = MODEL1,
    temperature=0,
    messages=[
        {"role":"system","content": query_prompt},
        {"role":"user","content":query}],
    response_format = queryDecompose
    )
    return queryDecompose.model_validate_json(
        response.choices[0].message.content
    )

def generate_section(context, section, company, section_prompt):
    response = completion(
        model = MODEL1,
        temperature=0.3,
        messages=[
            {"role":"system",
             "content": "You are a financial expert analysis assistant tasked to write a detailed but accurate section of a financial report"},
            {"role":"user",
             "content": f"""
             {section_prompt}
             Write a detailed report section on topic {section} for {company} given provided context:

             \n\n
             Context: 
             \n\n 
             {context}

            """}],
        response_format = sectionOutput
        )
    return sectionOutput.model_validate_json(
            response.choices[0].message.content
        )
    
    

def main():
    
    return None

if __name__ == "__main__":
    main()
