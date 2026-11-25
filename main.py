import io
import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

load_dotenv()

app = FastAPI(title="Hahow 課程查詢 API")


def fetch_hahow_courses(limit: int = 24, page: int = 0, sort: str = "TRENDING"):
    """共用的抓取函式"""
    url = "https://api.hahow.in/api/products/search"
    params = {
        "category": "COURSE",
        "filter": "PUBLISHED",
        "limit": limit,
        "page": page,
        "sort": sort,
    }
    # 若 .env 沒設定 USER_AGENT，給予一個預設值避免失敗
    headers = {
        "User-Agent": os.getenv("USER_AGENT", "Mozilla/5.0")
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"無法取得 Hahow 資料: {e}")

    data = response.json()
    products = data.get("data", {}).get("courseData", {}).get("products", [])

    course_list = []
    for product in products:
        course_list.append({
            "課程名稱": product.get("title"),
            "評價": product.get("averageRating"),
            "價格": product.get("price"),
            "購買人數": product.get("numSoldTickets"),
        })
    return course_list


# 回傳 JSON 格式（適合前端網頁或 App 串接）
@app.get("/courses")
def get_courses(
    limit: int = Query(24, ge=1, le=100, description="抓取筆數"),
    page: int = Query(0, ge=0, description="頁碼（從 0 開始）"),
    sort: str = Query("TRENDING", description="排序方式，例如 TRENDING、CREATED_TIME"),
):
    courses = fetch_hahow_courses(limit=limit, page=page, sort=sort)
    return {"count": len(courses), "courses": courses}