from .rag_engine import get_db, query_table
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# You would normally load this from env var
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def classify_product(product_description: str, top_k: int = 5):
    """
    1. Retrieve top K candidates from LanceDB.
    2. Format prompt for LLM.
    3. Call LLM to decide and reason.
    """
    db = get_db()
    
    # 1. Retrieval
    # LanceDB query_table returns a list of dictionaries
    # Keys: vector, id, text, ecn_number, etc. + _distance
    results = query_table(db, product_description, n_results=top_k)
    
    candidates = []
    print(f"\n--- RAG Retrieval: Top {top_k} Candidates ---")
    for i, res in enumerate(results):
        print(f"[{i+1}] ECCN: {res['ecn_number']} (Dist: {res.get('_distance', 0.0):.4f})")
        print(f"    Text Preview: {res['text'][:100]}...")
        
        candidates.append({
            "ecn": res['ecn_number'],
            "text": res['text'],
            "distance": res.get('_distance', 0.0), # LanceDB might return _distance
            "id": res['id']
        })
    print("---------------------------------------------\n")
            
    # 2. LLM Prompt Construction
    prompt = f"""
You are an expert in Export Control Classification Numbers (ECCN).
Your task is to classify the following product into the correct ECCN code based on the provided candidates.

Product Description:
"{product_description}"

Candidates (retrieved from database):
"""
    for i, curr in enumerate(candidates):
        prompt += f"\nCandidate {i+1} (ECCN: {curr['ecn']}):\n{curr['text']}\n"
        
    prompt += """
Instructions:
1. Analyze the product description against each candidate's definition and notes.
2. Select the BEST matching ECCN.
3. If none match perfectly, choose the closest or "EAR99" if it strictly doesn't fit any list.
4. Provide a confidence score (0.0 to 1.0).
5. Provide a concise reasoning.
   - **IMPORTANT**: Do NOT refer to "Candidate 1" or "Candidate 2" in your reasoning.
   - Refer directly to the ECCN code (e.g., "3A001") and the product description.
   - Example: "The product has X feature which aligns with the requirements of ECCN 3A001."

Return the output in JSON format:
{
  "ecn_number": "3A001",
  "confidence_score": 0.95,
  "reasoning": "The product matches the specific frequency range and power requirements listed in 3A001..."
}
"""

    # 3. Call LLM (mock or real)
    if not OPENAI_API_KEY:
        # Fallback if no key is present for testing
        print("Warning: No OpenAI API Key found. Returning top candidate as fallback.")
        best_candidate = candidates[0] if candidates else {"ecn": "Unknown"}
        return {
            "ecn_number": best_candidate.get("ecn"),
            "confidence_score": 0.5,
            "reasoning": "API Key missing. Returned top vector match."
        }
        
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o",  # or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Export Control Classification."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        import json
        return json.loads(content)
        
    except Exception as e:
        print(f"LLM Error: {e}")
        # Fallback
        return {
            "ecn_number": candidates[0]['ecn'] if candidates else "Error",
            "confidence_score": 0.0,
            "reasoning": f"LLM failed: {str(e)}"
        }
