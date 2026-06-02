import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_reddit_post(url):
    clean_url = url.split("?")[0].rstrip("/")

    # Try old.reddit.com first (less aggressively blocked)
    for base in ["https://old.reddit.com", "https://www.reddit.com"]:
        path = "/" + clean_url.split("reddit.com/", 1)[-1]
        json_url = base + path + ".json?limit=100"
        try:
            response = requests.get(json_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                break
        except Exception:
            continue
    else:
        raise Exception("Reddit blocked the request. Try a different post URL or wait a few minutes.")

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
        if body and body not in ("[deleted]", "[removed]"):
            comments.append({"body": body, "score": c.get("score", 0)})

    comments.sort(key=lambda x: x["score"], reverse=True)
    return {"post": post, "comments": comments[:20]}
