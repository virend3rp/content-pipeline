import asyncio
import os
import re
from twikit import Client

COOKIES_FILE = "x_cookies.json"

async def _scrape(url):
    client = Client("en-US")

    if os.path.exists(COOKIES_FILE):
        client.load_cookies(COOKIES_FILE)
    else:
        await client.login(
            auth_info_1=os.environ["X_USERNAME"],
            auth_info_2=os.environ["X_EMAIL"],
            password=os.environ["X_PASSWORD"],
        )
        client.save_cookies(COOKIES_FILE)

    tweet_id = re.search(r"/status/(\d+)", url).group(1)
    tweet = await client.get_tweet_by_id(tweet_id)

    post = {
        "text": tweet.text,
        "author": tweet.user.name,
        "username": tweet.user.screen_name,
    }

    replies_result = await client.search_tweet(f"conversation_id:{tweet_id}", "Latest")
    comments = []
    for reply in replies_result:
        if reply.id != tweet_id and reply.text:
            comments.append({
                "body": reply.text,
                "score": reply.favorite_count or 0,
            })

    comments.sort(key=lambda x: x["score"], reverse=True)
    return {"post": post, "comments": comments[:20]}

def scrape_x_post(url):
    return asyncio.run(_scrape(url))
