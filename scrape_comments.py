import yt_dlp
import json
import time

with open("urls.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

ydl_opts = {
    "skip_download": True,
    "writecomments": True,
    "getcomments": True,
    "cookiefile": "cookies.txt",
    "extractor_args": {
        "youtube": {
            "max_comments": ["all", "all", "all", "all"],
            "remote_components": ["ejs:github"]
        }
    },
    "sleep_interval_requests": 2,
}

all_data = []

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for i, url in enumerate(urls, 1):
        try:
            info = ydl.extract_info(url, download=False)
            comments = info.get("comments", [])
            clean_comments = [
                {
                    "author": c.get("author"),
                    "text": c.get("text"),
                    "likes": c.get("like_count"),
                    "timestamp": c.get("timestamp"),
                    "is_reply": c.get("parent") != "root"
                }
                for c in comments
            ]
            all_data.append({
                "video_id": info.get("id"),
                "title": info.get("title"),
                "comment_count": len(clean_comments),
                "comments": clean_comments
            })
            print(f"[{i}/{len(urls)}] {info.get('id')} - {len(clean_comments)} comments")
        except Exception as e:
            print(f"[{i}/{len(urls)}] FAILED: {url} - {e}")

        with open("comments.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        time.sleep(1)

print(f"Done. Saved {sum(d['comment_count'] for d in all_data)} comments to comments.json")
