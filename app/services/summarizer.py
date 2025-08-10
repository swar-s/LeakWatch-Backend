import openai
from flask import current_app


def generate_summary(breaches):
    api_key = current_app.config['OPENAI_API_KEY']
    client = openai.OpenAI(api_key=api_key)
    prompt = f"""
    You are a cybersecurity expert. The following list of data breaches has been aggregated from three different sources (HaveIBeenPwned, DeHashed, IntelX). Some breaches may appear more than once if reported by multiple sources. If you notice duplicate or overlapping breaches (same site/service, similar data, or same breach date), treat them as a single leak in your summary and recommendations, not as multiple separate incidents.

    For each unique breach, provide the following fields:
        - criticality: (Critical, Moderate, Low)
        - site: (site/service/domain where data was leaked)
        - date: (breach date)
        - description: (very brief, 1-2 phrases, not full sentences)
        - data_types_exposed: (array of strings, e.g., ["email", "password", "phone"])
        - sources: (array of strings, e.g., ["HIBP", "DeHashed"])

    Also provide:
        - breached: true if any breaches found, false otherwise
        - breach_count: number of unique breaches

    Return a valid JSON object with these fields:
    {{
        "breached": boolean,
        "breach_count": number,
        "breaches": [
            {{
            "criticality": string,
                "site": string,
                "date": string,
                "description": string,
                "data_types_exposed": [string],
                "sources": [string]
            }},
            ...
        ]
    }}

    Breaches:
    {breaches}
    """

    import json
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[
                {"role": "system", "content": "You are a security advisor. Respond in valid JSON only. No explanations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.4,
            timeout=30
        )
        content = response.choices[0].message.content
        # Robustly clean up LLM output: remove all lines with triple backticks and 'json'
        lines = content.strip().splitlines()
        cleaned_lines = []
        for line in lines:
            l = line.strip().lower()
            if l.startswith('```') or l == 'json' or l == '```json' or l.endswith('```'):
                continue
            cleaned_lines.append(line)
        cleaned = '\n'.join(cleaned_lines).strip()
        # Try to parse the cleaned response as JSON
        try:
            return json.loads(cleaned)
        except Exception:
            # If not valid JSON, return as string for debugging
            return {"error": "Invalid JSON from LLM", "raw": content}
    except openai.OpenAIError as oe:
        return {"error": f"GenAI Error: OpenAI API error - {str(oe)}"}
    except Exception as e:
        import logging
        logging.error(f"GenAI Exception: {e}")
        return {"error": "GenAI Error: Unable to generate summary at this time. Please try again later."}
