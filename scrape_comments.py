import subprocess
import json
import os
import time

with open("urls.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

all_data = []

for i, url in enumerate(urls, 1):
    video_id = url.split("v=")[-1].split("&")[0]
    json_path = f"{video_id}.info.json"

    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-comments",
        "--cookies", "cookies.txt",
        "--extractor-args", "youtube:max_comments=all,all,all,all",
        "--remote-components", "ejs:github",
        "--sleep-requests", "2",
        "-o", "%(id)s.%(ext)s",
        url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as jf:
                info = json.load(jf)

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
            os.remove(json_path)
        else:
            print(f"[{i}/{len(urls)}] FAILED: {url}")
            print(result.stderr[-500:])

    except Exception as e:
        print(f"[{i}/{len(urls)}] FAILED: {url} - {e}")

    with open("comments.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    time.sleep(1)

print(f"Done. Saved {sum(d['comment_count'] for d in all_data)} comments to comments.json")
