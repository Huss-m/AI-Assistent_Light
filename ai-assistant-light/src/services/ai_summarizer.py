# src/services/ai_summarizer.py
from __future__ import annotations
import os
from typing import List, Dict, Any

from openai import OpenAI


def summarize_day(emails: List[Dict[str, Any]], events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Försök göra en AI-sammanfattning. Faller tillbaka till enkel logik om inget API-key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return simple_fallback_priorities(emails, events)

    try:
        client = OpenAI()

        email_lines = [
            f"- {e['subject']} (från {e['from']})"
            for e in emails
        ]
        event_lines = [
            f"- {ev['summary']} ({ev['start']} - {ev['end']})"
            for ev in events
        ]

        prompt = f"""
Du är en assistent som skriver en kort svensk sammanfattning av användarens dag.

Olästa mejl:
{chr(10).join(email_lines) or 'Inga'}

Dagens kalender:
{chr(10).join(event_lines) or 'Inga'}

Skriv:
1) En kort översikt.
2) 3 viktigaste sakerna att fokusera på.
3) Eventuella risker eller deadlines att hålla koll på.
"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.4,
        )

        text = resp.choices[0].message.content.strip()
        return {
            "summary_text": text,
            "source": "openai",
        }
    except Exception:
        return simple_fallback_priorities(emails, events)


def simple_fallback_priorities(emails: List[Dict[str, Any]], events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Enkel, offline fallback om ingen AI finns."""
    lines = []
    lines.append(f"Sammanfattning:")
    lines.append(f"📬 Olästa mejl: {len(emails)}")
    lines.append(f"📅 Händelser idag: {len(events)}")
    lines.append("")
    if emails:
        lines.append("Viktigaste mejlen:")
        for e in emails[:3]:
            lines.append(f"- {e['subject']} (från {e['from']})")
        lines.append("")
    if events:
        lines.append("Dagens händelser:")
        for ev in events[:3]:
            lines.append(f"- {ev['summary']} ({ev['start']})")
    return {
        "summary_text": "\n".join(lines),
        "source": "fallback",
    }