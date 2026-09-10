"""
AI Integration Layer for HydroMediate using Groq Cloud (llama-3.3-70b-versatile).
Provides AI-enhanced mediator responses, non-deference institutional resistance,
evidence probing, and dynamic negotiation synthesis.
Falls back to heuristic mediator responses if GROQ_API_KEY is unconfigured.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

try:
    if GROQ_API_KEY:
        from groq import Groq
        ai_client = Groq(api_key=GROQ_API_KEY)
        HAS_GROQ = True
    else:
        ai_client = None
        HAS_GROQ = False
except Exception as e:
    print(f"[HydroMediate AI] Failed to initialize Groq SDK: {e}")
    ai_client = None
    HAS_GROQ = False

# Keep legacy alias so main.py import of HAS_GEMINI still works
HAS_GEMINI = HAS_GROQ

SYSTEM_PROMPT_MEDIATOR = """
You are HydroMediate AI, a neutral, evidence-driven, high-stakes natural resource mediator.
You facilitate a binding multi-stakeholder dispute over a shrinking community borehole.

STAKEHOLDERS INVOLVED:
1. Village Households (200 families) - Human rights priority (drinking/sanitation).
2. St. Jude New Community School (400 pupils) - Essential health/sanitation. ZERO historical precedent, but MUST NOT be dismissed for being new.
3. Subsistence Farmers - Growing staple maize/cassava for household food security.
4. Cash-Crop Commercial Farmers - High-value export avocado/macadamia growers (demanding priority based on economic output).
5. District Commissioner / Local Govt Official - Demanding water diversion for a "Future Industrial Zone", using institutional rank & a fabricated usage report.

YOUR MEDIATION RULES:
1. RESIST INSTITUTIONAL DEFERENCE: Do not defer to government titles, executive decrees, or political rank. Treat all stakeholders under equal evidence & human rights standards.
2. PROBE FABRICATED CLAIMS: When official or commercial claims lack physical feasibility (e.g. pipe limits or fake historical precedent), challenge line-item math.
3. BALANCE INTRA-FARMER RIFT: Separate staple food crop security from commercial cash-crop surplus allocations.
4. PROTECT THE NEW SCHOOL: Never allow the school to be zeroed or dismissed just because it lacks a historical allocation.
5. RESPOND TO YIELD SHOCK: When borehole capacity drops by 40% (from 50k to 30k L/day), enforce emergency priority tiering.
6. ENFORCEABLE ACCORD: Focus on producing measurable L/day quotas, hourly pumping windows, smart metering, and 3-tier penalties.

Keep responses authoritative, structured, concise, and focused on equitable consensus building.
"""

def generate_mediator_turn_response(
    state_summary: Dict[str, Any],
    user_prompt: Optional[str] = None
) -> str:
    """
    Generates an AI mediator response for the current negotiation turn using Groq.
    """
    if not HAS_GROQ or not ai_client:
        return ""  # System will use heuristic engine response

    user_content = f"""
Current Negotiation Turn: {state_summary.get('current_turn')}
Borehole Capacity: {state_summary.get('borehole_capacity')} Liters/day (Shocked: {state_summary.get('is_shocked')})
Report Probed: {state_summary.get('report_probed')}

Latest User / Delegate Input: {user_prompt or 'Advance turn negotiations'}

Generate the Mediator's response addressing active stakeholder claims, maintaining institutional non-deference, and guiding stakeholders toward the enforceable accord.
"""

    try:
        completion = ai_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_MEDIATOR},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as err:
        print(f"[HydroMediate Groq Error] {err}")
        return ""
