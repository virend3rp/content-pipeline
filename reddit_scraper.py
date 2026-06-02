import praw
import os

def scrape_reddit_post(url):
    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent="ContentPipeline/1.0",
    )

    submission = reddit.submission(url=url)
    submission.comments.replace_more(limit=0)

    post = {
        "title": submission.title,
        "body": submission.selftext.strip(),
        "subreddit": submission.subreddit.display_name,
        "score": submission.score,
    }

    comments = []
    for comment in submission.comments.list():
        body = comment.body.strip()
        if body and body not in ("[deleted]", "[removed]"):
            comments.append({"body": body, "score": comment.score})

    comments.sort(key=lambda x: x["score"], reverse=True)
    return {"post": post, "comments": comments[:20]}
