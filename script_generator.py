import openai
import os

def generate_script(reddit_data, style_profile):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set.")

    client = openai.OpenAI(api_key=api_key)

    post = reddit_data["post"]
    comments = reddit_data["comments"]
    hook = style_profile.get("hook_formula", "Bhai ye dekho...")
    writing_prompt = style_profile.get("writing_prompt", "")

    comments_text = "\n".join(
        f"- {c['body']}" for c in comments[:15]
    )

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
