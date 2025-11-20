import os
import json
from groq import Groq
from dotenv import load_dotenv
from utils import load_cache, save_cache

load_dotenv()


# Tiny LLM helper (cached explanations)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -----------------------------------------
# RULE DEFINITIONS (what we must evaluate)
# -----------------------------------------
RULES = [
    {
        "id": 1,
        "rule": "Act must define key terms",
        "field": "definitions",
        "keywords": ["means", "defined", "definition", "claimant"]
    },
    {
        "id": 2,
        "rule": "Act must specify eligibility criteria",
        "field": "eligibility",
        "keywords": ["eligible", "eligibility", "claimant", "criteria"]
    },
    {
        "id": 3,
        "rule": "Act must specify responsibilities of administering authority",
        "field": "responsibilities",
        "keywords": ["responsible", "authority", "duties"]
    },
    {
        "id": 4,
        "rule": "Act must include enforcement or penalties",
        "field": "penalties",
        "keywords": ["penalty", "offence", "sanction"]
    },
    {
        "id": 5,
        "rule": "Act must include payment calculation or entitlements",
        "field": "payments",
        "keywords": ["payment", "allowance", "rate", "amount"]
    },
    {
        "id": 6,
        "rule": "Act must include record-keeping or reporting provisions",
        "field": "record_keeping",
        "keywords": ["record", "keep", "retain", "report"]
    }
]


# -----------------------------------------
# Hybrid LLM Helper (Tiny Explanation Call)
# -----------------------------------------
def llm_explain(rule, status, evidence):
    """
    Very tiny Groq LLM call. Each call is < 20 tokens.
    Cached so it runs only once.
    """

    prompt = f"""
Rule: {rule}
Status: {status}
Evidence: {evidence}

Write ONE short sentence explaining why this rule is pass/fail.
"""

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=40,
        temperature=0
    )

    return resp.choices[0].message.content.strip()


# -----------------------------------------
# MAIN RULE CHECKER LOGIC
# -----------------------------------------
def run_rule_checks(sections):

    cached = load_cache("rule_checks")
    if cached:
        print("Using cached rule_checks.json")
        return cached

    results = []

    for rule in RULES:
        field_text = sections.get(rule["field"], "Not found")

        # Offline PASS/FAIL detection
        if field_text == "Not found":
            status = "fail"
            evidence = "No relevant content found."
            confidence = 60
        else:
            # Keyword-based confidence boost
            if any(kw.lower() in field_text.lower() for kw in rule["keywords"]):
                status = "pass"
                confidence = 90
            else:
                status = "partial"
                confidence = 75

            # evidence = first line
            evidence = field_text.split("\n")[0].strip()

        # Hybrid LLM explanation (tiny)
        explanation = llm_explain(rule["rule"], status, evidence)

        results.append({
            "rule_id": rule["id"],
            "rule": rule["rule"],
            "status": status,
            "evidence": evidence,
            "explanation": explanation,
            "confidence": confidence
        })

    save_cache("rule_checks", results)
    return results


# -----------------------------------------
# MAIN (for CLI)
# -----------------------------------------
if __name__ == "__main__":
    print("Loading sections.json...")
    sections = load_cache("sections")

    if not sections:
        raise Exception("ERROR: Run section_extractor.py first.")

    print("Running rule checks...\n")
    results = run_rule_checks(sections)

    print(json.dumps(results, indent=4))
    print("\nSaved → cache/rule_checks.json")
