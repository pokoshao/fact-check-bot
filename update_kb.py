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

    # 1. 生成當前的時間戳記 (例如: 20260424_0945)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    print(f"🚀 [START] 任務啟動時間: {datetime.now()}")

    for name, info in RSS_SOURCES.items():
        print(f"🔎 正在嘗試連線: {name}...")
        
        if not isinstance(info, dict):
            continue

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

    # 2. 修改存檔邏輯
    df = pd.DataFrame(all_articles)
    if not df.empty:
        df.drop_duplicates(subset=["url"], inplace=True)
        
        # --- 關鍵修改：使用時間戳記作為檔名 ---
        csv_filename = f"kb_raw_{timestamp}.csv"
        jsonl_filename = f"nemo_raw_{timestamp}.jsonl"
        
        # 存檔
        df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
        df.to_json(jsonl_filename, orient="records", lines=True, force_ascii=False)
        
        print(f"\n✅ 檔案已生成: {csv_filename}")
        print("\n--- 📊 最終統計報告 ---")
        print(pd.DataFrame(summary_report).to_string(index=False))
        return df
    else:
        print("\n😱 仍未抓到任何資料。")
        return pd.DataFrame()

if __name__ == "__main__":
    update_knowledge_base()
