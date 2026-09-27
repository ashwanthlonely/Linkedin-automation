import os
import sys
import re
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

def to_unicode_bold(text):
    """Convert standard ASCII alphanumeric text into Unicode Sans-Serif Bold characters for native LinkedIn bolding."""
    res = []
    for c in text:
        if 'A' <= c <= 'Z':
            res.append(chr(ord(c) - ord('A') + 0x1D5D4))
        elif 'a' <= c <= 'z':
            res.append(chr(ord(c) - ord('a') + 0x1D5EE))
        elif '0' <= c <= '9':
            res.append(chr(ord(c) - ord('0') + 0x1D7EC))
        else:
            res.append(c)
    return ''.join(res)


WEEKLY_TOPICS = {
    "Monday": {
        "title": "AI, GEN AI & ENTERPRISE COMPUTE",
        "emoji": "🤖",
        "theme": "AI, Gen AI & Enterprise Compute (Global + India updates)",
        "scope": (
            "Frontier foundational LLMs, autonomous agentic workflows, enterprise compute clusters, "
            "data center infrastructure, sovereign AI initiatives in India, GPU availability, and "
            "enterprise AI integration architectures."
        ),
        "benchmarks": (
            "Real-world anchors to cite:\n"
            "- Global: Autonomous agentic multi-model orchestration platforms scaling enterprise productivity (Source: Gartner / Bloomberg Intelligence)\n"
            "- Global: Enterprise compute data center hyperscaler investments and GPU cluster optimization (Source: IDC / Reuters)\n"
            "- India: Cabinet-approved ₹10,372 Crore IndiaAI Mission funding 10,000+ GPUs sovereign compute capacity under MeitY (Source: Press Information Bureau India)\n"
            "- India: Enterprise GenAI solution architectures integrating foundation models into ERP/enterprise systems (Source: MeitY / NASSCOM)"
        ),
        "hashtags": "#AshwanthKaribindi #Bristlecone #GenAI #SAP #EnterpriseAI #Innovation #Leadership #GlobalEconomy #India #ArtificialIntelligence #CloudCompute"
    },
    "Tuesday": {
        "title": "AUTO, EV & MOBILITY INNOVATION",
        "emoji": "🚗",
        "theme": "Auto, EV & Mobility Innovation (Global + India updates)",
        "scope": (
            "Solid-state battery tech, commercial EV scaling, Battery-as-a-Service (BaaS), "
            "autonomous driving stacks, OEM transformation (Tata Motors, Mahindra, global OEMs), "
            "charging infrastructure, and auto supply chains."
        ),
        "benchmarks": (
            "Real-world anchors to cite:\n"
            "- Global: Solid-state battery prototype pilots by Toyota, Samsung SDI, and QuantumScape progressing toward commercial production (Source: BloombergNEF / Reuters)\n"
            "- Global: Pack-level lithium-ion battery costs trending toward $100/kWh benchmark driving commercial fleet electrification (Source: BloombergNEF)\n"
            "- Global: Level-2+ and Level-3 ADAS commercial rollout (Mercedes-Benz Drive Pilot, Waymo autonomous fleet scaling) (Source: Reuters / Gartner)\n"
            "- India: Cabinet-approved PM E-DRIVE scheme with ₹10,900 Crore outlay supporting electric 2W/3W adoption and establishing over 72,000 public charging stations (Source: Ministry of Heavy Industries / PIB India)\n"
            "- India: Tata Motors (Nexon.ev, Curvv.ev) and Mahindra accelerating commercial & passenger EV adoption under the Auto PLI scheme (Source: SIAM / Ministry of Heavy Industries)\n"
            "- India: Battery-as-a-Service (BaaS) and battery swapping network expansion across urban logistics fleets (Source: NITI Aayog / PIB India)\n"
            "- NEGATIVE CONSTRAINT: DO NOT invent joint ventures between competing automakers (e.g. no VW-GM joint venture). Only cite actual OEM programs."
        ),
        "hashtags": "#AshwanthKaribindi #Bristlecone #GenAI #SAP #EnterpriseAI #Innovation #Leadership #GlobalEconomy #India #EV #Automotive #Mobility"
    },
    "Wednesday": {
        "title": "R&D, SPACETECH & SEMICONDUCTORS",
        "emoji": "🚀",
        "theme": "R&D, SpaceTech & Semiconductor Gigafactories (Global + India updates)",
        "scope": (
            "Commercial LEO satellite constellations, nuclear fusion baseload milestones, "
            "semiconductor fab construction and packaging (DLI/PLI, Micron, Tata Electronics), "
            "deep-tech research breakthroughs, and space economy expansion (ISRO, IN-SPACe)."
        ),
        "benchmarks": (
            "Real-world anchors to cite:\n"
            "- Global: Commercial LEO broadband satellite constellations and international nuclear fusion baseload research milestones (Source: Financial Times / Nature)\n"
            "- India: ₹76,000 Crore Semicon India program with Tata Electronics (Dholera & Morigaon) and Micron (Sanand) fabs under construction (Source: Press Information Bureau India)\n"
            "- India: ISRO commercial LEO launches via NewSpace India Limited (NSIL) and IN-SPACe private ecosystem expansion (Source: ISRO / PIB India)"
        ),
        "hashtags": "#AshwanthKaribindi #Bristlecone #GenAI #SAP #EnterpriseAI #Innovation #Leadership #GlobalEconomy #India #SpaceTech #Semiconductors #DeepTech"
    },
    "Thursday": {
        "title": "FINANCE, MACROECONOMICS & GIFT CITY",
        "emoji": "💰",
        "theme": "Finance, Macroeconomics & GIFT City (Global + India updates)",
        "scope": (
            "Global central bank interest rate pivots, inflation dynamics, India's GDP growth benchmarks, "
            "GST collections, capital capex expenditure, GIFT City IFSC international capital flows, "
            "and fintech innovation."
        ),
        "benchmarks": (
            "Real-world anchors to cite:\n"
            "- Global: Central bank monetary policy pivots amid moderating global headline inflation (Source: IMF / Reuters)\n"
            "- India: 7.2% GDP growth trajectory and resilient macroeconomic fundamentals (Source: Reserve Bank of India)\n"
            "- India: Robust monthly GST collections consistently exceeding ₹1.8 Lakh Crore (Source: Ministry of Finance)\n"
            "- India: GIFT City IFSC scaling international banking, aircraft leasing, and cross-border fund inflows (Source: IFSCA / PIB India)"
        ),
        "hashtags": "#AshwanthKaribindi #Bristlecone #GenAI #SAP #EnterpriseAI #Innovation #Leadership #GlobalEconomy #India #Finance #Macroeconomics #GIFTCity"
    },
    "Friday": {
        "title": "GEOPOLITICS, ENERGY & TRADE CORRIDORS",
        "emoji": "🌍",
        "theme": "Geopolitics, Energy & Trade Corridors (Global + India updates)",
        "scope": (
            "IMEC (India-Middle East-Europe Economic Corridor), critical mineral supply chain pacts, "
            "green hydrogen and renewable energy transitions, Indo-Pacific maritime logistics, "
            "and bilateral strategic trade partnerships."
        ),
        "benchmarks": (
            "Real-world anchors to cite:\n"
            "- Global: Critical mineral supply chain resilience alliances and multilateral clean energy capital deployment (Source: International Energy Agency / World Bank)\n"
            "- India: IMEC (India-Middle East-Europe Economic Corridor) trade and connectivity framework (Source: Ministry of External Affairs / PIB India)\n"
            "- India: National Green Hydrogen Mission and domestic solar manufacturing scale-up under PLI (Source: Ministry of New & Renewable Energy / PIB India)"
        ),
        "hashtags": "#AshwanthKaribindi #Bristlecone #GenAI #SAP #EnterpriseAI #Innovation #Leadership #GlobalEconomy #India #Geopolitics #SupplyChain #TradeCorridors"
    },
    "Saturday": {
        "title": "WEEKLY STRATEGIC INDIA SYNTHESIS",
        "emoji": "🇮🇳",
        "theme": "Weekly Strategic India Synthesis (Macro analysis with Pros/Tailwinds and Cons/Headwinds)",
        "scope": (
            "A comprehensive macro synthesis connecting the week's 5 core pillars (AI/Compute, Auto/EV, "
            "SpaceTech/Semis, Finance/GIFT City, Geopolitics/Energy). Evaluate how these global shifts converge "
            "to impact India, structured with explicit Pros/Tailwinds and Cons/Headwinds, culminating in an executive verdict."
        ),
        "benchmarks": (
            "Real-world anchors to cite:\n"
            "- Tailwinds: Semicon India ₹76,000 Cr PLI, ₹10,372 Cr IndiaAI Mission, ₹1.8L Cr GST monthly benchmark, GIFT City IFSC capital bridge (Sources: PIB India, RBI, MeitY)\n"
            "- Headwinds: Advanced GPU import dependency, baseload green energy demand for compute infrastructure, global trade policy uncertainties (Sources: IEA, Gartner, World Bank)"
        ),
        "hashtags": "#AshwanthKaribindi #Bristlecone #GenAI #SAP #EnterpriseAI #Innovation #Leadership #GlobalEconomy #India #StrategicSynthesis #Macroeconomics"
    }
}

SIGNIFICANT_OCCASIONS = {
    # Key Indian national days, international observances, and historic technology/science milestones
    "01-12": "National Youth Day (Swami Vivekananda Jayanti) 🌟",
    "01-15": "Indian Army Day 🇮🇳",
    "01-26": "Republic Day of India 🇮🇳 (Honoring the Constitution of India)",
    "02-28": "National Science Day (Discovery of the Raman Effect by Sir C.V. Raman) 🔬",
    "03-08": "International Women's Day 🌟 (Celebrating leadership and innovation)",
    "04-14": "Ambedkar Jayanti (Dr. B.R. Ambedkar Remembrance) 📜",
    "04-21": "National Civil Services Day 🏛️",
    "05-11": "National Technology Day (Pokhran-II & Indigenous Tech Capabilities) 💻",
    "06-05": "World Environment Day (Sustainable Tech & Clean Energy) 🌍",
    "06-21": "International Day of Yoga 🧘",
    "07-20": "International Moon Day (Apollo 11 Landing Milestone) 🌕",
    "08-15": "Independence Day of India 🇮🇳 (79th Year of Independence)",
    "08-23": "National Space Day (Commemorating Chandrayaan-3 landing on the Moon's South Pole) 🚀",
    "08-29": "National Sports Day (Major Dhyan Chand Jayanti) 🏆",
    "09-05": "National Teachers' Day (Dr. S. Radhakrishnan Jayanti) 📚",
    "09-15": "National Engineers' Day (Commemorating Sir M. Visvesvaraya) ⚙️",
    "10-02": "Gandhi Jayanti & Lal Bahadur Shastri Jayanti 🕊️",
    "10-08": "Indian Air Force Day ✈️",
    "10-31": "National Unity Day (Rashtriya Ekta Diwas / Sardar Patel Jayanti) 🇮🇳",
    "11-26": "National Constitution Day (Samvidhan Divas) 📜",
    "12-04": "Indian Navy Day ⚓",
    "12-22": "National Mathematics Day (Srinivasa Ramanujan Jayanti) 📐"
}

def get_occasion_context(dt=None):
    """Retrieve occasion context or historic milestone guidance for the given date."""
    if dt is None:
        dt = datetime.now()
    key = dt.strftime("%m-%d")
    known_occasion = SIGNIFICANT_OCCASIONS.get(key)
    if known_occasion:
        return (
            f"🎉 TODAY'S NOTABLE OCCASION / HISTORIC MILESTONE:\n"
            f"Today ({dt.strftime('%B %d')}) is {known_occasion}.\n"
            f"MANDATORY: Open the post right below the author line with a short, dignified 1-sentence executive tribute or greeting acknowledging this occasion before transitioning into the deep dive."
        )
    return (
        f"DATE INTELLIGENCE: Today is {dt.strftime('%B %d')}.\n"
        f"If today coincides with a widely recognized festival, national observance, or pivotal historic event in technology/science/economy, include a tasteful 1-sentence executive tribute below the author line. If there is no specific occasion today, proceed directly to the deep dive without forcing any greeting."
    )


class PostGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("groq_api") or os.getenv("GROQ_API_KEY") or os.getenv("ngroq_api")
        if not self.api_key:
            raise ValueError("Groq API key ('groq_api') not found in environment variables.")
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "openai/gpt-oss-120b"
        self.author_line = "✍️ Author: Ashwanth Karibindi | Principal - SAP Gen AI Solution Architect, Bristlecone, Bangalore"

    def generate_post_for_day(self, day_name=None, max_chars=2600, archived_posts=None):
        """Generate a LinkedIn post tailored to the 6-day single-topic deep dive schedule."""
        if not day_name:
            day_name = datetime.now().strftime("%A")

        if day_name == "Sunday":
            print("☕ Sunday is designated as Rest Day. No post generated.")
            return None

        if day_name not in WEEKLY_TOPICS:
            raise ValueError(f"Invalid day_name: {day_name}. Expected Monday-Saturday.")

        if day_name == "Saturday":
            return self.generate_saturday_synthesis(archived_posts=archived_posts, max_chars=max_chars)
        else:
            return self.generate_weekday_post(day_name=day_name, max_chars=max_chars)

    def generate_weekday_post(self, day_name, max_chars=2600, date_obj=None):
        """Generate a deep-dive LinkedIn post for Monday through Friday."""
        topic_info = WEEKLY_TOPICS[day_name]
        if not date_obj:
            date_obj = datetime.now()
        date_str = date_obj.strftime("%B %d, %Y")
        occasion_context = get_occasion_context(date_obj)

        system_prompt = (
            "You are an elite executive data journalist and enterprise technology solution architect. "
            "Generate authoritative, high-density LinkedIn analysis focusing on a SINGLE deep-dive theme with both Global and India updates. "
            "RULES:\n"
            "1. NO raw markdown symbols: Absolutely NO asterisks (** or *), NO plus signs (+), NO markdown hashes (#) for headings, NO backticks.\n"
            "2. NO URLs or external links.\n"
            "3. MUST include explicit primary source attributions in parentheses (e.g. (Source: Press Information Bureau India), (Source: RBI), (Source: Reuters), (Source: Bloomberg), (Source: Gartner)).\n"
            "4. STRICT FACTUAL ACCURACY: Ground all claims in established real-world industry benchmarks and official government initiatives. Do NOT fabricate specific arbitrary grant amounts (e.g. '$1.4 bn'), exact fictional facility numbers, or ungrounded battery line specs. Use the provided benchmark anchors directly.\n"
            "5. If today corresponds to an occasion, festival, or historic event, open with a respectful 1-sentence executive tribute before the deep dive.\n"
            "6. NEVER mention EarEase Tech or company bios.\n"
            "7. Keep the content strictly factual, credible, and executive."
        )

        user_prompt = f"""
Act as an elite executive data journalist. Write a single-topic deep dive LinkedIn post for {day_name}:

THEME: {topic_info['emoji']} {topic_info['title']}
SCOPE: {topic_info['scope']}
DATE: {date_str}

{occasion_context}

{topic_info['benchmarks']}

STRICT TEMPLATE STRUCTURE:
📰 {date_str} | {topic_info['title']}
{self.author_line}
[If today coincides with a notable occasion, festival, or historic milestone, insert a tasteful 1-sentence executive tribute or greeting right here.]

🌐 GLOBAL DEVELOPMENTS
[Provide 2-3 dense bullet points analyzing global frontier breakthroughs, benchmarks, or market moves with source citations in parentheses. Example: 🔹 Agentic AI workflows are reducing enterprise latency... (Source: Bloomberg Intelligence)]

🇮🇳 INDIA DEVELOPMENTS & ECOSYSTEM
[Provide 2-3 dense bullet points analyzing India-specific adoption, sovereign capabilities, regulatory milestones, or investments with source citations in parentheses. Example: 🔹 India sovereign compute clusters under MeitY... (Source: Press Information Bureau India)]

💡 STRATEGIC TAKEAWAY & ENTERPRISE PERSPECTIVE
[Provide 1-2 impactful paragraphs explaining what enterprise architects, CXOs, and tech leaders must execute now to capitalize on this shift.]

🏷️ HASHTAGS
{topic_info['hashtags']}

CRITICAL CONSTRAINTS:
- STRICT character limit: Total response MUST be under {max_chars} characters (including spaces).
- Do NOT use markdown bolding (** or *). Headers will be converted programmatically.
- Bullet points must start with '🔹 '.
- Explicit source citations in parentheses for all factual claims.
- Do NOT invent ungrounded data.
"""

        raw_text = self._call_groq(system_prompt, user_prompt, max_tokens=3500, temperature=0.45)
        post_text = self._format_and_clean_linkedin_text(raw_text, topic_info['title'])

        if len(post_text) > max_chars:
            print(f"⚠️ Post length ({len(post_text)} chars) exceeds limit ({max_chars}). Condensing...")
            post_text = self._condense_post(post_text, max_chars, is_saturday=False)
            post_text = self._format_and_clean_linkedin_text(post_text, topic_info['title'])

        return post_text

    def generate_saturday_synthesis(self, archived_posts=None, max_chars=2600, date_obj=None):
        """Generate Saturday's Weekly Strategic India Synthesis analyzing the week's themes with Pros/Tailwinds and Cons/Headwinds."""
        if not date_obj:
            date_obj = datetime.now()
        date_str = date_obj.strftime("%B %d, %Y")
        occasion_context = get_occasion_context(date_obj)
        topic_info = WEEKLY_TOPICS["Saturday"]

        # Build context summary from Mon-Fri archived posts
        archive_context = ""
        if archived_posts and len(archived_posts) > 0:
            archive_context = "WEEKLY DIGEST OF MON-FRI POSTS:\n"
            for day, item in archived_posts.items():
                content_snippet = item.get("content", "").replace("\n", " ")[:300]
                archive_context += f"- {day} ({item.get('topic', 'Theme')}): {content_snippet}...\n"
        else:
            archive_context = (
                "FOUNDATIONAL THEMES OF THE WEEK:\n"
                "- Monday: AI, Gen AI & Enterprise Compute (Autonomous agents, sovereign clusters, data centers)\n"
                "- Tuesday: Auto, EV & Mobility Innovation (Battery tech, BaaS, OEM EV transitions)\n"
                "- Wednesday: R&D, SpaceTech & Semiconductor Gigafactories (Commercial LEO, fusion, chip fabs)\n"
                "- Thursday: Finance, Macroeconomics & GIFT City (GDP expansion, GST records, IFSC flows)\n"
                "- Friday: Geopolitics, Energy & Trade Corridors (IMEC, critical minerals, green transition)\n"
            )

        system_prompt = (
            "You are an executive macroeconomic strategist and chief enterprise architect. "
            "Write an authoritative weekly strategic synthesis analyzing how global shifts across tech, mobility, "
            "semiconductors, finance, and geopolitics intersect to impact India. "
            "RULES:\n"
            "1. NO raw markdown symbols: Absolutely NO asterisks (** or *), NO plus signs (+), NO markdown hashes (#), NO backticks.\n"
            "2. NO URLs or external links.\n"
            "3. MUST include explicit primary source attributions in parentheses.\n"
            "4. If today corresponds to an occasion, festival, or historic event, open with a respectful 1-sentence executive tribute before the synthesis.\n"
            "5. NEVER mention EarEase Tech or company bios.\n"
            "6. Structure with clear Tailwinds/Pros and Headwinds/Cons for India."
        )

        user_prompt = f"""
Act as an executive macroeconomic strategist. Write the Saturday Strategic India Synthesis:

{archive_context}

{occasion_context}

{topic_info['benchmarks']}
Key Guidance: Trade corridor must cite IMEC (India-Middle East-Europe Economic Corridor). Economic growth must cite RBI's 7.0%-7.2% GDP projection.

DATE: {date_str}

STRICT TEMPLATE STRUCTURE:
📰 {date_str} | WEEKLY STRATEGIC INDIA SYNTHESIS
{self.author_line}
[If today coincides with a notable occasion, festival, or historic milestone, insert a tasteful 1-sentence executive tribute or greeting right here.]

🌐 EXECUTIVE MACRO SUMMARY
[A high-density 2-paragraph synthesis of how this week's global shifts across AI, EV mobility, semiconductor fabs, macro finance, and geopolitical corridors collectively shape India's geopolitical and tech positioning. Include primary sources (e.g. RBI, IMF, PIB India).]

🚀 STRATEGIC PROS & TAILWINDS
🔹 [Tailwind 1: e.g. Domestic Manufacturing & Semiconductor Fabs via PLI (Source: MeitY / PIB India)]
🔹 [Tailwind 2: e.g. Capital inflows & GIFT City mechanism (Source: Reserve Bank of India)]
🔹 [Tailwind 3: e.g. Sovereign AI & Public Digital Infrastructure scaling (Source: NASSCOM / MeitY)]

⚠️ HEADWINDS & STRATEGIC CHALLENGES
🔹 [Headwind 1: e.g. Hardware & advanced GPU supply chain dependencies (Source: Gartner / Reuters)]
🔹 [Headwind 2: e.g. Power grid & baseload clean energy requirements for data centers (Source: International Energy Agency)]
🔹 [Headwind 3: e.g. Global trade tariff protectionism & export demand sensitivity (Source: World Bank / WTO)]

💡 THE EXECUTIVE VERDICT
[A concise concluding strategic perspective for enterprise leaders, CXOs, and solutions architects on operationalizing these tailwinds while insulating against headwinds.]

🏷️ HASHTAGS
{topic_info['hashtags']}

CRITICAL CONSTRAINTS:
- STRICT character limit: Total response MUST be under {max_chars} characters (including spaces).
- Absolutely NO asterisks (** or *).
- Bullet points must start with '🔹 '.
- Explicit source citations in parentheses.
"""

        raw_text = self._call_groq(system_prompt, user_prompt, max_tokens=3500, temperature=0.45)
        post_text = self._format_and_clean_linkedin_text(raw_text, "WEEKLY STRATEGIC INDIA SYNTHESIS")

        if len(post_text) > max_chars:
            print(f"⚠️ Saturday post length ({len(post_text)} chars) exceeds limit ({max_chars}). Condensing...")
            post_text = self._condense_post(post_text, max_chars, is_saturday=True)
            post_text = self._format_and_clean_linkedin_text(post_text, "WEEKLY STRATEGIC INDIA SYNTHESIS")

        return post_text

    def _call_groq(self, system_prompt, user_prompt, max_tokens=3500, temperature=0.4):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "reasoning_format": "hidden",
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = None
        for attempt in range(4):
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
            if response.status_code == 429:
                print("⏳ Groq Rate limit reached. Retrying in 15 seconds...")
                time.sleep(15)
                continue
            break

        if not response or response.status_code != 200:
            raise Exception(f"Groq API call failed: {response.status_code if response else 'No response'} - {response.text if response else ''}")

        content = response.json()["choices"][0]["message"]["content"].strip()
        # Automatically strip reasoning tags if any remain
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        return content

    def _format_and_clean_linkedin_text(self, text, topic_title):
        # 1. Strip reasoning tags
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

        # 2. Strip EarEase Tech or legacy brand mentions if any model hallucinated it
        text = re.sub(r'(?i)earease\s*tech(\s*pvt\s*ltd)?', 'Bristlecone', text)
        text = re.sub(r'(?i)founder\s*&\s*ceo[,\s]*earease\s*tech', 'Principal - SAP Gen AI Solution Architect, Bristlecone', text)

        # 3. Strip raw markdown bold, italics, headers (require space for headers so hashtags are safe)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*[\*\+]\s+', '🔹 ', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*-\s+', '🔹 ', text, flags=re.MULTILINE)

        # 4. Apply Unicode Bold to standard section headers
        bold_targets = [
            topic_title,
            "WEEKLY STRATEGIC INDIA SYNTHESIS",
            "AI, GEN AI & ENTERPRISE COMPUTE",
            "AUTO, EV & MOBILITY INNOVATION",
            "R&D, SPACETECH & SEMICONDUCTORS",
            "FINANCE, MACROECONOMICS & GIFT CITY",
            "GEOPOLITICS, ENERGY & TRADE CORRIDORS",
            "GLOBAL DEVELOPMENTS",
            "INDIA DEVELOPMENTS & ECOSYSTEM",
            "STRATEGIC TAKEAWAY & ENTERPRISE PERSPECTIVE",
            "STRATEGIC TAKEAWAY",
            "EXECUTIVE MACRO SUMMARY",
            "STRATEGIC PROS & TAILWINDS",
            "HEADWINDS & STRATEGIC CHALLENGES",
            "THE EXECUTIVE VERDICT",
            "EXECUTIVE VERDICT",
            "HASHTAGS"
        ]

        for target in bold_targets:
            pattern = re.compile(re.escape(target), re.IGNORECASE)
            text = pattern.sub(to_unicode_bold(target.upper()), text)

        # Ensure proper hashtags section header
        if "🏷️" in text and to_unicode_bold("HASHTAGS") not in text:
            text = re.sub(r'🏷️\s*(?:HASHTAGS:?)?\s*', f'🏷️ {to_unicode_bold("HASHTAGS")}\n', text)

        # Ensure author line is correct and prominent
        if "Ashwanth Karibindi" not in text:
            # Prepend author line under date line
            lines = text.split("\n")
            if len(lines) > 0 and "📰" in lines[0]:
                lines.insert(1, self.author_line)
                text = "\n".join(lines)
        else:
            # If model generated a variant of author line, normalize to exact line
            text = re.sub(
                r'✍️?\s*(?:Author:)?\s*Ashwanth Karibindi[^\n]*',
                self.author_line,
                text
            )

        return text

    def _condense_post(self, post_text, max_chars, is_saturday=False):
        """Condense post text while retaining critical sections, sources, author, and hashtags."""
        system_prompt = (
            "You are an expert editor. Condense the supplied LinkedIn post to fit strictly under the character limit. "
            "CRITICAL: Keep the exact author line, all source citations in parentheses, and the section structure. "
            "Do NOT use markdown asterisks (** or *)."
        )

        user_prompt = f"""
Condense this LinkedIn post so that its total character count is strictly under {max_chars - 100} characters.
Retain all sections, bullet points, source citations, author line, and hashtags.

ORIGINAL POST:
{post_text}
"""
        condensed = self._call_groq(system_prompt, user_prompt, max_tokens=3500, temperature=0.3)
        return condensed

    def fix_post_with_corrections(self, post_text, verifier_report, day_name, max_chars=2600):
        """Autonomously self-heal post by removing flagged inaccuracies and strictly applying verified benchmarks."""
        topic_info = WEEKLY_TOPICS.get(day_name, WEEKLY_TOPICS["Monday"])
        system_prompt = (
            "You are an executive editor and facts auditor. Your task is to revise the provided LinkedIn post "
            "to completely eliminate any inaccurate claims, fake corporate partnerships, or ungrounded statistics "
            "flagged by the verification agent.\n"
            "RULES:\n"
            "1. Strictly remove or replace any claim flagged as fabricated, unverified, or inaccurate.\n"
            "2. Ground replacement facts strictly in the verified anchors.\n"
            "3. Maintain the exact author line, section structure, and hashtags.\n"
            "4. NO markdown symbols (** or *).\n"
            f"5. Total length MUST be strictly under {max_chars} characters."
        )

        user_prompt = f"""
FACT-CHECKING AUDIT REPORT:
{verifier_report}

VERIFIED BENCHMARK ANCHORS TO USE:
{topic_info.get('benchmarks', '')}

DRAFT POST TO REVISE:
{post_text}

Revise the post now to be 100% factually accurate, compliant with the audit report, and strictly under {max_chars} characters.
"""
        raw_text = self._call_groq(system_prompt, user_prompt, max_tokens=3500, temperature=0.2)
        revised = self._format_and_clean_linkedin_text(raw_text, topic_info['title'])
        if len(revised) > max_chars:
            revised = self._condense_post(revised, max_chars)
            revised = self._format_and_clean_linkedin_text(revised, topic_info['title'])
        return revised


if __name__ == "__main__":
    generator = PostGenerator()
    today_name = datetime.now().strftime("%A")
    print(f"Testing post generation for: {today_name}")
    post = generator.generate_post_for_day(today_name, max_chars=2600)
    print("=== GENERATED POST ===")
    print(post)
    print("======================")
    print(f"Character count: {len(post)} / 2600")
