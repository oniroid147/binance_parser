import asyncio
import httpx
import time

URL = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Origin": "https://www.binance.com",
    "Referer": "https://www.binance.com/"
}
PARAMS = {
    "type": 1,
    "catalogId": "48",
    "pageNo": 1,
    "pageSize": 1
}

async def fetch_once(client, i):
    t0 = time.time()
    try:
        resp = await client.get(URL, headers=HEADERS, params=PARAMS, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", {}).get("catalogs", [])
        if data and data[0].get("articles"):
            title = data[0]["articles"][0]["title"]
            print(f"[{i}] 🟢 Ответ за {time.time() - t0:.3f} сек: {title}")
            return title
    except Exception as e:
        print(f"[{i}] ❌ Ошибка: {e}")
    return ""

async def flood_loop():
    async with httpx.AsyncClient(http2=True) as client:
        last = await fetch_once(client, "init")
        if not last:
            print("[!] Не получили начальный заголовок.")
            return

        print("▶ Запускаем параллельный мониторинг…")
        while True:
            tasks = [fetch_once(client, i) for i in range(5)]  # 5 запросов параллельно
            results = await asyncio.gather(*tasks)
            for r in results:
                if r and r != last:
                    print("🚨 УРААА! НОВАЯ НОВОСТЬ:", r)
                    last = r

if __name__ == "__main__":
    asyncio.run(flood_loop())
