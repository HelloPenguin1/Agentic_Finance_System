import time, random, json, logging
from dotenv import load_dotenv
load_dotenv()
from threading import Semaphore
from litellm import completion
from output_val.structured_outputs import queryDecompose, sectionOutput, final_answer
from prompts.query_prompt import query_prompt
from prompts.system_prompt import SYSTEM_PROMPT1, SYSTEM_PROMPT2
from langsmith import traceable
from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
from litellm.exceptions import RateLimitError

MAX_RETRIES = 5
MODEL1 = "groq/openai/gpt-oss-20b"
MODEL2 = "groq/openai/gpt-oss-120b"
RERANKER_MDOEL = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2",trust_remote_code=True,)

EMBEDDING_MODEL = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    encode_kwargs={'normalize_embeddings': True} # Ensures unit length vectors automatically
)

logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)
llm_semaphore = Semaphore(2)


@traceable(run_type="llm")
def invoke_llm(**kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return completion(**kwargs)

        except RateLimitError:
            if attempt == MAX_RETRIES - 1:
                raise

            delay = (2 ** attempt) + random.uniform(0, 0.5)

            print(
                f"Rate limit reached. "
                f"Retry {attempt + 1}/{MAX_RETRIES} in {delay:.2f}s..."
            )

            time.sleep(delay)
            
            

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
    

def generate_llm_findings(user_query, context, section, company, section_prompt):

    context_json = json.dumps(context, indent=2)
   
    with llm_semaphore:
        response = invoke_llm(
            model = MODEL1,
            max_completion_tokens=1024,
            temperature=0.1,
            messages=[
                {"role":"system",
                "content": SYSTEM_PROMPT1},
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
                {context_json}"""}],
            response_format = sectionOutput
            )
        
        return sectionOutput.model_validate_json(response.choices[0].message.content)
    
    
def aggregate_findings(user_query, completed_sections):
    response = invoke_llm(
        model = MODEL2,
        temperature = 0.3,
        messages = [
            {'role': 'system',
                "content": SYSTEM_PROMPT2 },
            {'role':'user',
                'content': f"""
                User Question:
                {user_query}
                
                Agent outputs:
                {completed_sections}
                
                Your complete response:
                """}],
        response_format = final_answer
    )
    return final_answer.model_validate_json(response.choices[0].message.content)
    

def main():
    return None

if __name__ == "__main__":
    main()
