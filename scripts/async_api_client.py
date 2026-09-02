import time
import asyncio
import requests
import httpx

API_BASE_URL = "https://jsonplaceholder.typicode.com/photos/"
NUM_RECORDS = 1000
SEMAPHORE_LIMIT = 10
MAX_RETRIES = 3

# (a) Senkron İstek (requests)
def fetch_sync():
    print(f"[Senkron] {NUM_RECORDS} istek 'requests' ile sırayla atılıyor...")
    start_time = time.perf_counter()
    success_count = 0
    
    # Session kullanarak bağlantıyı sürekli açık tutuyoruz (daha performanslı)
    with requests.Session() as session:
        for i in range(1, NUM_RECORDS + 1):
            url = f"{API_BASE_URL}{i}"
            try:
                response = session.get(url)
                if response.status_code == 200:
                    success_count += 1
            except requests.RequestException:
                pass 

    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f"[Senkron] Bitti! Süre: {elapsed:.2f} saniye | Başarılı: {success_count}/{NUM_RECORDS}")
    return elapsed

# (b) Asenkron İstek (asyncio + httpx + semaphore + retry)
async def fetch_single_async(client, semaphore, i):
    url = f"{API_BASE_URL}{i}"
    
    # Semaphore ile aynı anda maksimum 10 isteğe izin veriyoruz
    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get(url, timeout=10.0)
                
                # Rate limit (429) veya sunucu hatası (50x) durumunda Retry mantığı
                if response.status_code in [429, 500, 502, 503, 504]:
                    print(f"[{url}] Rate limit/Hata ({response.status_code}). Deneme ({attempt + 1}/{MAX_RETRIES})...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff (1s, 2s, 4s bekleme)
                    continue
                
                response.raise_for_status()
                return True
                
            except httpx.RequestError as e:
                print(f"[{url}] İstek hatası: {e}. Yeniden deneniyor...")
                await asyncio.sleep(2 ** attempt)
                
        return False 

async def fetch_async_main():
    print(f"\n[Asenkron] {NUM_RECORDS} istek 'httpx' (Semaphore: {SEMAPHORE_LIMIT}) ile atılıyor...")
    start_time = time.perf_counter()
    
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
    
    # httpx.AsyncClient ile asenkron connection pooling (bağlantı havuzu)
    async with httpx.AsyncClient() as client:
        tasks = [fetch_single_async(client, semaphore, i) for i in range(1, NUM_RECORDS + 1)]
        results = await asyncio.gather(*tasks)
    
    success_count = sum(results)
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f"[Asenkron] Bitti! Süre: {elapsed:.2f} saniye | Başarılı: {success_count}/{NUM_RECORDS}")
    return elapsed

if __name__ == "__main__":
    print("--- ÖDEV 2.4: ASYNC API İSTEMCİSİ PERFORMANS TESTİ ---")
    
    # Senkron test
    sync_time = fetch_sync()
    
    # Asenkron test
    async_time = asyncio.run(fetch_async_main())
    
    # Karşılaştırma Sonucu
    print("\n" + "="*50)
    print(f"{'Yöntem':<20} | {'Süre (sn)':<15}")
    print("-" * 50)
    print(f"{'(a) Senkron (requests)':<20} | {sync_time:<15.2f}")
    print(f"{'(b) Asenkron (httpx)':<20} | {async_time:<15.2f}")
    print("="*50)
    print(f"Sonuç: Asenkron yöntem {sync_time / async_time:.1f} kat daha hızlı!")