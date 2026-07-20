import json
from dotenv import load_dotenv
load_dotenv()
from threading import Semaphore
from litellm import completion
from output_val.structured_outputs import queryDecompose, sectionOutput
from prompts.query_prompt import query_prompt
from langchain_openai import OpenAIEmbeddings
from langsmith import traceable
import logging

MODEL1 = "groq/openai/gpt-oss-20b"
EMBEDDING_MODEL = OpenAIEmbeddings(model="text-embedding-3-small")

logger = logging.getLogger(__name__)

llm_semaphore = Semaphore(2)


@traceable(run_type='llm')
def invoke_llm(**kwargs):
    response = completion(**kwargs)
    return response

def querydecomposer(query):
    response = invoke_llm(
    model = MODEL1,
    temperature=0.1,
    messages=[
        {"role":"system","content": query_prompt},
        {"role":"user","content":query}],
        response_format = queryDecompose
    )
    return queryDecompose.model_validate_json(  
        response.choices[0].message.content)
    

def generate_section(user_query, context, section, company, section_prompt):

    context_json = json.dumps(context, indent=2)
   
    with llm_semaphore:
        response = invoke_llm(
            model = MODEL1,
            max_completion_tokens=1024,
            temperature=0.3,
            messages=[
                {"role":"system",
                "content": """
                You are an information extraction system for SEC filings.

                Your job is to extract factual financial findings from the provided evidence.

                Do not answer conversationally.
                Do not write paragraphs.
                Do not explain the schema.
                Populate every field required by the response schema.
                Return only valid JSON matching the schema.
                """},
                {"role":"user",
                "content": f"""
                    {section_prompt} 

                    User Question:
                    {user_query}

                    Topic:
                    {section}

                    Company:
                    {company}

                    Context:
                    {context_json}
                    
                    """}],
            response_format = sectionOutput
            )
        
        return sectionOutput.model_validate_json(response.choices[0].message.content)
    
    

def main():
    
    return None

if __name__ == "__main__":
    main()
