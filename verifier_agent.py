import os
import sys
import json
import time
import re
import requests
from datetime import datetime
from dotenv import load_dotenv

# Ensure UTF-8 stdout encoding on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class NewsVerifierAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("groq_api") or os.getenv("GROQ_API_KEY") or os.getenv("ngroq_api")
        if not self.api_key:
            raise ValueError("Groq API key ('groq_api') not found in environment variables.")
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "openai/gpt-oss-120b"

        self.system_prompt = (
            "You are the Senior Executive Fact-Checking & Verification Agent for Ashwanth Karibindi's Executive LinkedIn Analysis Series.\n\n"
            "Your responsibility is to verify the factual integrity, accuracy, and credible attribution of a proposed executive LinkedIn post before publishing.\n\n"
            "==================================================\n"
            "VERIFICATION METHODOLOGY\n"
            "==================================================\n"
            "Evaluate the claims in the supplied post against verified real-world knowledge across global enterprise tech, cloud compute, Indian government policies, and macroeconomic data:\n"
            "• Tier 1 Primary Sources: PIB India, MeitY, RBI, ISRO, NITI Aayog, Ministry of Finance, official company regulatory filings.\n"
            "• Tier 2 Secondary Sources: Reuters, Bloomberg Intelligence, Gartner, IDC, Financial Times.\n\n"
            "RULES:\n"
            "1. If claims represent recognized real-world developments, authentic policy initiatives (e.g. IndiaAI Mission, Semicon India, PLI schemes, GIFT City, RBI policy), and cite reputable institutions, assign VERIFICATION_STATUS: PASS.\n"
            "2. If the claims are substantively accurate but minor metric nuances, projections, or wording refinements are suggested, assign VERIFICATION_STATUS: PASS_WITH_CORRECTIONS.\n"
            "3. Assign REQUIRES_RESEARCH or REJECT only if there are flagrantly fabricated, ungrounded, contradictory, or defamatory assertions.\n"
            "4. Never hallucinate that an existing official program does not exist.\n"
            "5. Strip any reasoning tags automatically.\n\n"
            "OUTPUT FORMAT:\n"
            "Return ONLY the following structured report:\n\n"
            "VERIFICATION_STATUS:\n"
            "[PASS / PASS_WITH_CORRECTIONS / REQUIRES_RESEARCH / REJECT]\n\n"
            "CONFIDENCE:\n"
            "[VERY_HIGH / HIGH / MEDIUM / LOW]\n\n"
            "SUMMARY:\n"
            "[2-3 concise sentences evaluating factual accuracy and source attribution]\n\n"
            "CLAIM_VERIFICATION:\n"
            "[Brief verification of each major claim with source evaluation]\n\n"
            "NUMERICAL_VERIFICATION:\n"
            "[Verification of key metrics, GDP figures, budget allocations]\n\n"
            "CORRECTIONS_OR_NOTES:\n"
            "[Constructive refinement notes, or 'None required']\n\n"
            "PUBLISHING_RECOMMENDATION:\n"
            "[PUBLISH / PUBLISH_AFTER_CORRECTION / DO_NOT_PUBLISH]\n\n"
            "REASON:\n"
            "[Concise concluding rationale]"
        )

    def verify_news_content(self, headline, article_text, source_urls=None):
        """Execute strict fact-checking verification on proposed news story."""
        pub_date = datetime.now().strftime("%B %d, %Y")

        user_input = f"""
PROPOSED POST FOR VERIFICATION:

1. Topic / Headline: {headline}
2. Date: {pub_date}
3. Post Content:
{article_text}

4. Stated / Primary Sources: {source_urls or "Official Press Information Bureau (PIB) India, Reserve Bank of India (RBI), ISRO, MeitY, Reuters, Bloomberg, Gartner"}

Please perform claim-by-claim verification, numerical verification, source tiering, and return the structured VERIFICATION REPORT.
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ],
            "reasoning_format": "hidden",
            "temperature": 0.2,
            "max_tokens": 3500
        }

        print("🔍 Senior Fact-Checking Agent verifying news content...")
        response = None
        for attempt in range(5):
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
            if response.status_code == 429:
                print(f"⏳ Groq Rate limit reached (attempt {attempt + 1}/5). Waiting 15 seconds...")
                time.sleep(15)
                continue
            break

        if not response or response.status_code != 200:
            raise Exception(f"Groq API call failed: {response.status_code if response else 'No response'} - {response.text if response else ''}")

        report = response.json()["choices"][0]["message"]["content"].strip()
        report = re.sub(r'<think>.*?</think>', '', report, flags=re.DOTALL).strip()
        print("✅ Fact-Checking Verification Complete!")

        # Parse Verification Status robustly
        status = "PASS"
        status_match = re.search(r'VERIFICATION_STATUS[:\*\s]+(PASS_WITH_CORRECTIONS|REQUIRES_RESEARCH|REJECT|PASS)', report, re.IGNORECASE)
        if status_match:
            status = status_match.group(1).upper()
        elif "VERIFICATION_STATUS" in report:
            for s in ["PASS_WITH_CORRECTIONS", "REQUIRES_RESEARCH", "REJECT", "PASS"]:
                if s in report:
                    status = s
                    break

        # Reconcile if status was labeled as REQUIRES_RESEARCH but recommendation is explicitly approved for publish
        if status == "REQUIRES_RESEARCH" and ("PUBLISH_AFTER_CORRECTION" in report or "PUBLISHING_RECOMMENDATION:\nPUBLISH" in report):
            status = "PASS_WITH_CORRECTIONS"

        return {
            "status": status,
            "report": report
        }


if __name__ == "__main__":
    verifier = NewsVerifierAgent()
    sample_headline = "AI, Gen AI & Enterprise Compute Deep Dive"
    sample_text = """
    Agentic AI workflows are scaling enterprise compute deployment. (Source: Bloomberg Intelligence)
    MeitY is expanding India AI mission GPU compute access. (Source: Press Information Bureau India)
    """
    res = verifier.verify_news_content(sample_headline, sample_text)
    print("STATUS:", res["status"])
    print("\nREPORT:\n", res["report"][:400])
