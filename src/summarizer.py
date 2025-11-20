import os
from groq import Groq
from dotenv import load_dotenv
from utils import chunk_text, load_cache, save_cache

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_text(text: str):
    # ----- CHECK CACHE FIRST -----
    cached = load_cache("summary")
    if cached:
        print("Using cached summary...")
        return cached

    # ----- NO CACHE → LLM CALL -----
    chunks = chunk_text(text, max_chars=5000)
    partial_summaries = []

    for i, chunk in enumerate(chunks, start=1):
        print(f"Summarizing chunk {i}/{len(chunks)}...")

        prompt = f"""
Summarize the following legislative text chunk into 3–4 bullet points:

{chunk}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        partial_summaries.append(response.choices[0].message.content)

    combined = "\n".join(partial_summaries)

    final_prompt = f"""
Combine these partial summaries into a final clear 6–8 bullet summary:
{combined}
"""

    final_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0
    )

    final_summary = final_response.choices[0].message.content


    # ----- SAVE CACHE -----
    save_cache("summary", final_summary)

    return final_summary
