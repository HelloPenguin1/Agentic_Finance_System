from litellm import cost_per_token, completion_cost
from dataclasses import dataclass


@dataclass
class LLM_Metrics:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_cost: float
    completion_cost: float
    total_cost: float


def extract_llm_logs(response, model):
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    prompt_cost, completion_cost_est = cost_per_token(
        model=model, 
        prompt_tokens=prompt_tokens, 
        completion_tokens=completion_tokens)
    
    total_cost = completion_cost(completion_response=response)
    
    return LLM_Metrics(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        prompt_cost=prompt_cost,
        completion_cost=completion_cost_est,
        total_cost=total_cost,
    )