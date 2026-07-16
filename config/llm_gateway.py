import os
from dotenv import load_dotenv
load_dotenv()

from threading import Semaphore

from litellm import completion
from output_val.structured_outputs import queryDecompose, sectionOutput
from prompts.query_prompt import query_prompt
from langchain_openai import OpenAIEmbeddings

MODEL1 = "groq/openai/gpt-oss-20b"
EMBEDDING_MODEL = OpenAIEmbeddings(model="text-embedding-3-small")
llm_semaphore = Semaphore(2)

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
    with llm_semaphore:
        response = completion(
            model = MODEL1,
            max_completion_tokens=800,
            temperature=0.3,
            messages=[
                {"role":"system",
                "content": """
                You are a financial expert analysis assistant tasked to write a grounded analysis based on financial SEC filings and financial statements
                Respond ONLY with valid JSON.
                """},
                {"role":"user",
                "content": f"""
                {section_prompt}
                Write a report section on topic {section} for {company} given provided context:

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
