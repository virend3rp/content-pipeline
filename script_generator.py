import openai
import os

def generate_script(data, style_profile, source="reddit"):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set.")

    client = openai.OpenAI(api_key=api_key)

    hook = style_profile.get("hook_formula", "Bhai ye dekho...")
    writing_prompt = style_profile.get("writing_prompt", "")
    comments = data.get("comments", [])

    comments_text = "\n".join(f"- {c['body']}" for c in comments[:15])

    if source == "x":
        post = data["post"]
        user_message = f"""Tweet by @{post['username']}:
"{post['text']}"

Top Replies:
{comments_text}

Write a 30-60 second Instagram Reel script reacting to this tweet and its replies. Start with "{hook}". Pick the funniest replies and react to them one by one. End on the best line — no outro."""

    else:
        post = data["post"]
        user_message = f"""Reddit Post from r/{post['subreddit']}:
Title: {post['title']}
{f"Body: {post['body']}" if post['body'] else ""}

Top Comments:
{comments_text}

Write a 30-60 second Instagram Reel script reacting to this post and its comments. Start with "{hook}". Pick the funniest comments and react to them one by one. End on the best line — no outro."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": writing_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=1024,
    )

    return response.choices[0].message.content
