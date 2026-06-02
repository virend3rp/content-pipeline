import requests

def scrape_reddit_post(url):
    clean_url = url.split("?")[0].rstrip("/")
    json_url = clean_url + ".json"

    headers = {"User-Agent": "ContentPipeline/1.0"}
    response = requests.get(json_url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    post_data = data[0]["data"]["children"][0]["data"]
    comments_raw = data[1]["data"]["children"]

    post = {
        "title": post_data["title"],
        "body": post_data.get("selftext", "").strip(),
        "subreddit": post_data["subreddit"],
        "score": post_data["score"],
    }

    comments = []
    for item in comments_raw:
        if item["kind"] != "t1":
            continue
        c = item["data"]
        body = c.get("body", "").strip()
        if body and body != "[deleted]" and body != "[removed]":
            comments.append({"body": body, "score": c.get("score", 0)})

    comments.sort(key=lambda x: x["score"], reverse=True)

    return {"post": post, "comments": comments[:20]}
