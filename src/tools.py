import os
import json
import random
from typing import Optional

try:
    from tenacity import retry, stop_after_attempt, wait_exponential
    HAS_TENACITY = True
except ImportError:
    HAS_TENACITY = False
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def stop_after_attempt(*args):
        pass
    def wait_exponential(*args, **kwargs):
        pass

try:
    from tavily import TavilyClient
    HAS_TAVILY = True
except ImportError:
    HAS_TAVILY = False

def real_calculator(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def simulate_tool(ground_truth: str, distractor: str, accuracy: float) -> str:
    import random
    if random.random() <= accuracy:
        return str(ground_truth)
    return str(distractor)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _call_tavily_search(client, query: str, max_results: int = 3) -> str:
    response = client.search(query, max_results=max_results)
    
    results = []
    for result in response.get("results", []):
        content = (
            f"Title: {result.get('title', 'N/A')}\n"
            f"Content: {result.get('content', 'N/A')}\n"
            f"Score: {result.get('score', 0.0)}"
        )
        results.append(content)
    
    return "\n\n---\n\n".join(results) if results else "No results found"

def external_search_tool(query: str, ground_truth: Optional[str] = None, distractor: Optional[str] = None, accuracy: float = 1.0) -> str:
    if not HAS_TAVILY:
        print("Warning: Tavily not installed. Falling back to simulate_tool.")
        if ground_truth is not None and distractor is not None:
            return simulate_tool(ground_truth, distractor, accuracy)
        return "Error: Tavily not installed and no fallback data provided"
    
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        print("Warning: TAVILY_API_KEY not set. Falling back to simulate_tool.")
        if ground_truth is not None and distractor is not None:
            return simulate_tool(ground_truth, distractor, accuracy)
        return "Error: TAVILY_API_KEY not set"
    
    try:
        client = TavilyClient(api_key=tavily_api_key)
        result = _call_tavily_search(client, query)
        
        if ground_truth is not None and distractor is not None and accuracy < 1.0:
            if random.random() > accuracy:
                return distractor
        
        return result
        
    except Exception as e:
        print(f"External search error: {e}")
        if ground_truth is not None and distractor is not None:
            return simulate_tool(ground_truth, distractor, accuracy)
        return f"Error: {str(e)}"

def hybrid_tool(query: str, ground_truth: str, distractor: str, accuracy: float = 1.0, use_external: bool = False) -> str:
    if use_external:
        return external_search_tool(query, ground_truth, distractor, accuracy)
    else:
        return simulate_tool(ground_truth, distractor, accuracy)
