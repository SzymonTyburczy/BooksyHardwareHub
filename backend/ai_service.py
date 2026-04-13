"""
AI service module — Gemini integration for semantic search and inventory audit.

Falls back to keyword-based logic if GEMINI_API_KEY is not set.
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Gemini client ────────────────────────────────────────────────────────────

_gemini_client = None


def _get_api_key() -> str:
    """Read the API key at call time (after dotenv has loaded)."""
    return os.getenv("GEMINI_API_KEY", "")


def _get_gemini_client():
    """Lazy-initialize the Gemini client."""
    global _gemini_client
    api_key = _get_api_key()
    if _gemini_client is None and api_key:
        try:
            from google import genai
            _gemini_client = genai.Client(api_key=api_key)
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini client: {e}")
    return _gemini_client


def is_gemini_available() -> bool:
    return bool(_get_api_key())


# ── Keyword fallback (used when Gemini is unavailable) ─────────────────────

KEYWORD_MAP = {
    "mobile": ["iphone", "galaxy", "ipad", "samsung", "apple"],
    "phone": ["iphone", "galaxy", "samsung", "sony"],
    "laptop": ["macbook", "xps", "dell", "lenovo"],
    "mouse": ["basilisk", "mx master", "logitech", "razer"],
    "headphone": ["sony", "wh-1000", "headphones"],
    "audio": ["sony", "wh-1000"],
    "test": ["iphone", "galaxy", "ipad", "samsung"],
    "develop": ["macbook", "xps", "laptop"],
    "meeting": ["headphone", "sony"],
    "portable": ["iphone", "galaxy", "ipad", "macbook air"],
    "apple": ["apple", "iphone", "ipad", "macbook"],
    "keyboard": ["razer", "logitech"],
    "wireless": ["logitech", "sony", "apple"],
}


def _keyword_search(query: str, items: list[dict]) -> list[dict]:
    """Fallback keyword-based search."""
    q = query.lower()
    matched_terms: list[str] = []
    for keyword, terms in KEYWORD_MAP.items():
        if keyword in q:
            matched_terms.extend(terms)

    if matched_terms:
        return [
            h for h in items
            if any(t in f"{h['name']} {h['brand']}".lower() for t in matched_terms)
        ]
    # Fallback to plain text
    return [
        h for h in items
        if q in h["name"].lower() or q in h["brand"].lower()
    ]


# ── Semantic Search (Gemini) ───────────────────────────────────────────────

def semantic_search(query: str, items: list[dict]) -> list[dict]:
    """
    Use Gemini to interpret a natural language query and find matching hardware.
    Falls back to keyword search if Gemini is unavailable.
    """
    client = _get_gemini_client()
    if not client:
        logger.info("Gemini unavailable, using keyword fallback for search")
        return _keyword_search(query, items)

    try:
        # Build a compact inventory list for the prompt
        inventory_lines = []
        for h in items:
            inventory_lines.append(
                f"ID:{h['id']} | {h['name']} | Brand:{h['brand']} | Status:{h['status']}"
            )
        inventory_text = "\n".join(inventory_lines)

        prompt = f"""You are an IT equipment search assistant for a company hardware hub.
Given the user's natural language query, return the IDs of matching hardware items from the inventory below.

Think about what the user ACTUALLY needs — interpret intent, not just keywords.
For example:
- "I need something to test a mobile app" → return phones and tablets
- "something for a video call" → return headphones/headsets
- "I need a dev machine" → return laptops

INVENTORY:
{inventory_text}

USER QUERY: "{query}"

Respond with ONLY a JSON array of matching item IDs, e.g. [1, 4, 9].
If nothing matches, respond with [].
Do NOT include any explanation, just the JSON array."""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        # Parse the response — extract JSON array from text
        text = response.text.strip()
        # Handle markdown code blocks
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        matched_ids = json.loads(text)
        if not isinstance(matched_ids, list):
            raise ValueError(f"Expected list, got {type(matched_ids)}")

        # Filter items by matched IDs (preserve order from Gemini)
        id_set = set(matched_ids)
        results = [h for h in items if h["id"] in id_set]
        logger.info(f"Gemini search: query='{query}' → {len(results)} results (IDs: {matched_ids})")
        return results

    except Exception as e:
        logger.warning(f"Gemini search failed, falling back to keywords: {e}")
        return _keyword_search(query, items)


# ── Inventory Audit (Gemini) ───────────────────────────────────────────────

def _rule_based_audit(items: list[dict]) -> dict:
    """Fallback rule-based audit."""
    flags = []

    for item in items:
        # Check future purchase dates
        if item.get("purchase_date"):
            try:
                pd = datetime.strptime(item["purchase_date"], "%Y-%m-%d")
                if pd > datetime.now():
                    flags.append({
                        "hardware_id": item["id"],
                        "hardware_name": item["name"],
                        "issue": f"Purchase date is in the future ({item['purchase_date']}). This may be a data entry error.",
                        "severity": "high",
                    })
            except ValueError:
                pass

        # Check for safety notes
        notes = (item.get("notes") or "").lower()
        if "battery swelling" in notes or "battery swell" in notes:
            flags.append({
                "hardware_id": item["id"],
                "hardware_name": item["name"],
                "issue": f"Notes indicate battery swelling — a safety hazard. Device is marked {item['status']} but should be in Repair.",
                "severity": "high",
            })
        elif "liquid damage" in notes or "water damage" in notes:
            flags.append({
                "hardware_id": item["id"],
                "hardware_name": item["name"],
                "issue": f"Notes indicate liquid damage and sticky keyboard. Device is {item['status']} but may need servicing.",
                "severity": "medium",
            })

        # Check unknown status
        if item.get("status") == "Unknown":
            flags.append({
                "hardware_id": item["id"],
                "hardware_name": item["name"],
                "issue": 'Status is "Unknown" — device has no brand or purchase date. Needs identification.',
                "severity": "medium",
            })

        # Check long Repair status
        if item.get("status") == "Repair" and item.get("purchase_date"):
            try:
                pd = datetime.strptime(item["purchase_date"], "%Y-%m-%d")
                years = (datetime.now() - pd).days / 365
                if years > 2:
                    flags.append({
                        "hardware_id": item["id"],
                        "hardware_name": item["name"],
                        "issue": f"Device has been in Repair status since {pd.year}. Consider escalating or writing off.",
                        "severity": "low",
                    })
            except ValueError:
                pass

    high = sum(1 for f in flags if f["severity"] == "high")
    medium = sum(1 for f in flags if f["severity"] == "medium")
    low = sum(1 for f in flags if f["severity"] == "low")

    summary = (
        f"Inventory audit complete. Found {len(flags)} issues: "
        f"{high} high-severity, {medium} medium-severity, {low} low-severity. "
        f"Immediate action recommended for flagged items."
    )

    return {"flags": flags, "summary": summary}


def inventory_audit(items: list[dict]) -> dict:
    """
    Use Gemini to perform an intelligent inventory audit.
    Falls back to rule-based checks if Gemini is unavailable.
    """
    client = _get_gemini_client()
    if not client:
        logger.info("Gemini unavailable, using rule-based fallback for audit")
        return _rule_based_audit(items)

    try:
        # Build inventory details for the prompt
        inventory_lines = []
        for h in items:
            line = f"ID:{h['id']} | {h['name']} | Brand:{h['brand']} | Purchased:{h.get('purchase_date', 'N/A')} | Status:{h['status']}"
            if h.get("notes"):
                line += f" | Notes: {h['notes']}"
            if h.get("assigned_to"):
                line += f" | Assigned to user #{h['assigned_to']}"
            inventory_lines.append(line)
        inventory_text = "\n".join(inventory_lines)

        prompt = f"""You are an IT inventory auditor for a company equipment management system.
Analyze the following inventory and flag any issues. Today's date is {datetime.now().strftime('%Y-%m-%d')}.

Look for:
1. SAFETY HAZARDS: battery swelling, physical damage, liquid damage on available devices
2. DATA ANOMALIES: future purchase dates, missing information, invalid data
3. OPERATIONAL ISSUES: devices stuck in repair too long, unknown status, contradictions between notes and status
4. PROCESS CONCERNS: available devices with damage notes that should be in repair

INVENTORY:
{inventory_text}

Respond with ONLY valid JSON in this exact format:
{{
  "flags": [
    {{
      "hardware_id": <int>,
      "hardware_name": "<string>",
      "issue": "<clear description of the problem>",
      "severity": "high" | "medium" | "low"
    }}
  ],
  "summary": "<1-2 sentence executive summary of findings>"
}}

Be thorough but concise. Only flag genuine issues."""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        text = response.text.strip()
        # Handle markdown code blocks
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        result = json.loads(text)

        # Validate structure
        if "flags" not in result or "summary" not in result:
            raise ValueError("Missing required fields in Gemini response")

        logger.info(f"Gemini audit: found {len(result['flags'])} issues")
        return result

    except Exception as e:
        logger.warning(f"Gemini audit failed, falling back to rule-based: {e}")
        return _rule_based_audit(items)
