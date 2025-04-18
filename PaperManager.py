import tkinter as tk
import requests
import bibtexparser
from datetime import datetime

def process_doi(doi_url):
    prefix = "https://doi.org/"
    if doi_url.startswith(prefix):
        return doi_url[len(prefix):]
    else:
        return doi_url

def Notion_Bib(doi):
    return_text = "状態："
    # ここに自分の情報を入れる
    NOTION_TOKEN = ""
    DATABASE_ID = ""

    # DOIからBibTeXを取得
    bibtex_url = f"https://doi.org/{doi}"
    headers = {"Accept": "application/x-bibtex"}
    response = requests.get(bibtex_url, headers=headers)

    if response.status_code != 200:
        raise Exception("DOIからBibTeXの取得に失敗しました")
        return_text = "DOIからBibTeXの取得に失敗しました" + return_text
    bib_database = bibtexparser.loads(response.text)
    entry = bib_database.entries[0]

    # BibTeXの要素を取り出す
    title = entry.get("title", "No Title")
    authors = entry.get("author", "Unknown").replace("\n", " ")
    journal = entry.get("journal", "Unknown")
    year_str = entry.get("year", "Unknown")

    # 年から日付に変換（YYYY → YYYY-01-01）
    try:
        publication_date = datetime.strptime(year_str, "%Y").strftime("%Y-%m-%d") if year_str else None
    except ValueError:
        publication_date = None


    # BibTeXのauthorからmulti_select形式に変換（カンマ対応）
    def convert_authors_to_multiselect(authors_raw):
        authors = [a.strip() for a in authors_raw.replace("\n", " ").split(" and ")]
        formatted = []

        for name in authors:
            if "," in name:
                last, first = [x.strip() for x in name.split(",", 1)]
                full_name = f"{first} {last}"
            else:
                full_name = name
            formatted.append({"name": full_name})

        return formatted

    multi_select_authors = convert_authors_to_multiselect(authors)

    # ② Notionに登録
    notion_headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    added_date = datetime.now().strftime("%Y-%m-%d")

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "Authors": {"multi_select": multi_select_authors},
            "Publication Date": {"date": {"start":publication_date}},
            "Journal Name": {"rich_text": [{"text": {"content": journal}}]},
            "DOI": {"url": f"https://doi.org/{doi}"},
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"追加日: {added_date}"
                            }
                        }
                    ]
                }
            }
        ]
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=notion_headers, json=data)

    if response.status_code == 200:
        print("✅ Notionに追加成功！")
        return_text = return_text + "✅ Notionに追加成功！"
    else:
        print("❌ 追加失敗:", response.text)
        return_text = return_text + "❌ 追加失敗:"
    return return_text

def send_data():
    doi = edit_box.get()
    doi= process_doi(doi)
    result_label.config(text="受付ました👀")
    return_text = Notion_Bib(doi)
    result_label.config(text=return_text)
    edit_box.delete(0, tk.END)

def close_window():
    root.destroy()

root = tk.Tk()
root.title("Paper Manager")
root.geometry("400x250")

# ウィンドウをフォーカスさせ、アクティブなスペースに表示させる
root.lift()
root.attributes('-topmost', True)
root.after(10, lambda: root.attributes('-topmost', False))

# ラベル
label = tk.Label(root, text="データを入力してください:")
label.pack(pady=10)

# エントリー
edit_box = tk.Entry(root)
edit_box.insert(tk.END, "")
edit_box.pack(pady=5)

# ボタン
send_button = tk.Button(root, text="送信", command=send_data)
send_button.pack(pady=20)

# 結果表示ラベル（空の状態で最初に作成）
result_label = tk.Label(root, text="")
result_label.pack(pady=5)

# 閉じるボタン
close_button = tk.Button(root, text="閉じる", command=close_window)
close_button.pack(pady=10)

root.mainloop()