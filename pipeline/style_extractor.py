import openai
import os
from datetime import datetime

def extract_style(profile_name, source_url, hook_formula, transcripts):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set.")

    client = openai.OpenAI(api_key=api_key)

    samples = [t["text"] for t in transcripts[:15]]
    transcripts_text = "\n\n---\n\n".join(samples)

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Analyze these video transcripts from a content creator and write a detailed writing style prompt.

Hook formula they use: "{hook_formula}"

Transcripts:
{transcripts_text}

Write a detailed system prompt (2-3 paragraphs) that captures their exact style — language mix, tone, content format, structure, and what makes their humor work. Someone should be able to write content indistinguishable from theirs using only this prompt."""
        }]
    )

    writing_prompt = response.choices[0].message.content

    return {
        "name": profile_name,
        "source": source_url,
        "hook_formula": hook_formula,
        "writing_prompt": writing_prompt,
        "sample_transcripts": samples,
        "created_at": datetime.now().isoformat(),
    }
