import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
# .envファイルを読み込む
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"  # 必要に応じてバージョン更新
}

# データ取得
def fetch_database_entries(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    results = []

    has_more = True
    next_cursor = None

    while has_more:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        res = requests.post(url, headers=HEADERS, json=payload)
        data = res.json()
        results.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    return results

# バックアップ保存
def backup_to_file(data, filename_prefix="notion_backup"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    backup_folder = "backup"
    filepath = os.path.join(backup_folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ Backup saved as: {filename}")


print("📥 Fetching data from Notion...")
entries = fetch_database_entries(DATABASE_ID)
print(f"📦 Total entries fetched: {len(entries)}")
backup_to_file(entries)