import feedparser
import pandas as pd
import requests
import io
from datetime import datetime
import os

# 1. 重新定義來源
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
    summary_report = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    # 生成當前的時間戳記
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    print(f"🚀 [START] 任務啟動時間: {datetime.now()}")

    # --- 步驟 A: 先抓資料 (這部分不會用到 df) ---
    for name, info in RSS_SOURCES.items():
        print(f"🔎 正在嘗試連線: {name}...")
        try:
            resp = requests.get(info["url"], headers=headers, timeout=30)
            if resp.status_code == 200:
                feed = feedparser.parse(io.BytesIO(resp.content))
                count = 0
                for entry in feed.entries[:30]:
                    all_articles.append({
                        "source": name,
                        "lang": info["lang"],
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", ""),
                        "url": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "fetched_at": datetime.now().strftime("%Y-%m-%d"),
                    })
                    count += 1
                summary_report.append({"來源": name, "狀態": "成功", "筆數": count})
            else:
                summary_report.append({"來源": name, "狀態": f"HTTP {resp.status_code}", "筆數": 0})
        except Exception as e:
            summary_report.append({"來源": name, "狀態": "異常", "筆數": 0})

    # --- 步驟 B: 資料抓完後，才定義 df ---
    df = pd.DataFrame(all_articles)

    # --- 步驟 C: 最後才執行存檔 ---
    if not df.empty:
        df.drop_duplicates(subset=["url"], inplace=True)
        
        csv_filename = f"kb_raw_{timestamp}.csv"
        jsonl_filename = f"nemo_raw_{timestamp}.jsonl"
        
        # 這裡才執行 to_csv，絕對不會報 referenced before assignment
        df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
        df.to_json(jsonl_filename, orient="records", lines=True, force_ascii=False)
        
        print(f"\n✅ 檔案已成功生成: {csv_filename}")
        return df
    else:
        print("\n😱 本次沒抓到資料。")
        return pd.DataFrame()

if __name__ == "__main__":
    update_knowledge_base()
