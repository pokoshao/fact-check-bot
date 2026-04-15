import feedparser
import pandas as pd
import requests
import io
from datetime import datetime

# 1. 重新定義來源 (確保是 Dict 嵌套 Dict 格式)
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

    print(f"🚀 [START] 任務啟動時間: {datetime.now()}")

    # 關鍵檢查：這裡 name 會拿到 key, info 會拿到 value (即那組小字典)
    for name, info in RSS_SOURCES.items():
        print(f"🔎 正在嘗試連線: {name}...")
        
        # 多加一層檢查，避免 info 還是字串
        if not isinstance(info, dict):
            print(f"❌ 錯誤: {name} 的資料格式不正確，預期是字典但拿到 {type(info)}")
            continue

        try:
            resp = requests.get(info["url"], headers=headers, timeout=20)
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
                print(f"✅ {name}: 成功抓取 {count} 筆")
                summary_report.append({"來源": name, "狀態": "成功", "筆數": count})
            else:
                summary_report.append({"來源": name, "狀態": f"HTTP {resp.status_code}", "筆數": 0})
        except Exception as e:
            print(f"💥 {name} 發生異常: {str(e)}")
            summary_report.append({"來源": name, "狀態": "異常", "筆數": 0})

    df = pd.DataFrame(all_articles)
    if not df.empty:
        df.drop_duplicates(subset=["url"], inplace=True)
        df.to_csv("knowledge_base_raw.csv", index=False, encoding="utf-8-sig")
        print("\n--- 📊 最終統計報告 ---")
        print(pd.DataFrame(summary_report).to_string(index=False))
        return df
    else:
        print("\n😱 仍未抓到任何資料。")
        return pd.DataFrame()

# 執行
df = update_knowledge_base()
