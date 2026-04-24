import feedparser
import pandas as pd
import requests
import io
from datetime import datetime

# 1. 定義 RSS 來源
RSS_SOURCES = {
    "聯合新聞網": {"url": "https://udn.com/rssfeed/news/2/6638?ch=news", "lang": "zh"},
    "自由時報": {"url": "https://news.ltn.com.tw/rss/all.xml", "lang": "zh"},
    "MyGoPen": {"url": "https://www.mygopen.com/feeds/posts/default", "lang": "zh"},
    "TFC台灣事實查核": {"url": "https://tfc-taiwan.org.tw/feed", "lang": "zh"},
    "Snopes": {"url": "https://www.snopes.com/feed/", "lang": "en"},
    "PolitiFact": {"url": "https://www.politifact.com/rss/all/", "lang": "en"}
}

def update_knowledge_base():
    all_articles = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    print(f"🚀 啟動抓取任務...")

    # --- 步驟 A: 抓取資料 (絕對不可以在這裡寫 df.to_csv) ---
    for name, info in RSS_SOURCES.items():
        try:
            resp = requests.get(info["url"], headers=headers, timeout=20)
            if resp.status_code == 200:
                feed = feedparser.parse(io.BytesIO(resp.content))
                for entry in feed.entries[:30]:
                    all_articles.append({
                        "source": name,
                        "lang": info["lang"],
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "fetched_at": datetime.now().strftime("%Y-%m-%d")
                    })
        except Exception as e:
            print(f"❌ {name} 連線失敗")

    # --- 步驟 B: 資料全抓完，才建立 df ---
    df = pd.DataFrame(all_articles)

    # --- 步驟 C: 最後才存檔 ---
    if not df.empty:
        df.drop_duplicates(subset=["url"], inplace=True)
        # 存成帶日期的檔案
        df.to_csv(f"kb_raw_{timestamp}.csv", index=False, encoding="utf-8-sig")
        df.to_json(f"nemo_raw_{timestamp}.jsonl", orient="records", lines=True, force_ascii=False)
        print(f"✅ 成功儲存 {len(df)} 筆資料至 kb_raw_{timestamp}.csv")
    else:
        print("⚠️ 沒抓到任何資料")

if __name__ == "__main__":
    update_knowledge_base()
