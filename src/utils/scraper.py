import requests
import json
import csv
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Cấu hình Supabase
SUPABASE_URL = "https://mlkqujqhrzvibontqatq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1sa3F1anFocnp2aWJvbnRxYXRxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MTYyNDMwMiwiZXhwIjoyMDU3MjAwMzAyfQ.9GKUKNB2qqFiH6pn_f6NBZqdJsuVHtNjUNhQZy5IEBE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def write_log(message):
    with open("scraper_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def upsert_to_supabase(title):
    try:
        data = {"name": title}
        response = supabase.table("WebScrapData").upsert([data]).execute()
        print(f"✅ Upsert thành công: {title}. Response: {response}")
        write_log(f"✅ Upsert thành công: {title}. Response: {response}")
    except Exception as e:
        print(f"❌ Lỗi upsert Supabase: {e}")
        write_log(f"❌ Lỗi upsert Supabase: {e}")

def scrape_website(offset, size, section):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Referer": "https://www.reuters.com/",
            "Accept-Language": "en-US,en;q=0.9",
        }

        api_url = "https://www.reuters.com/pf/api/v3/content/fetch/articles-by-section-alias-or-id-v1"

        params = {
            "query": json.dumps({
                "arc-site": "reuters",
                "fetch_type": "collection",
                "offset": offset,
                "section_id": section,
                "size": size,
                "uri": section,
                "website": "reuters"
            }),
            "d": "269",
            "mxId": "00000000",
            "_website": "reuters"
        }

        response = requests.get(api_url, headers=headers, params=params)
        if "result" in response.json() and "articles" in response.json()["result"]:
            all_titles = [response.json()["result"]["articles"][i]["title"] for i in range(len(response.json()["result"]["articles"]))]
        else:
            all_titles = []
        return all_titles
    except requests.RequestException as e:
        print(f"❌ Lỗi khi scrape website: {e}")
        write_log(f"❌ Lỗi khi scrape website: {e}")

filedir = "D:\\HUST\\20242\\IT3930 - Project 2\\SearchEngineHUST\\SearchEngineBE\\sections.txt"
sections = []
with open(filedir, "r", encoding="utf-8") as file:
    sections = [line.strip() for line in file.readlines() if line.strip()]
    print(sections)
if sections:
    for section in sections:
        write_log(f"🚀 Bắt đầu scrape section: {section}")
        dem = 0
        for i in range(0,1000):
            all_titles = scrape_website(20*i, 100, section)
            if not all_titles:
                print (f"❌ Đã hết dữ liệu cho section: {section}. Section này đã thu được {dem} bài viết.")
                write_log(f"❌ Đã hết dữ liệu cho section: {section}. Section này đã thu được {dem} bài viết.")
                break
            else:

                for title in all_titles:
                    upsert_to_supabase(title)
                    dem += 1

# print(scrape_website(100, 21, "/business/aerospace-defense/"))
print("✅ Hoàn thành scrape và upsert vào Supabase!")
write_log("✅ Hoàn thành scrape và upsert vào Supabase!")