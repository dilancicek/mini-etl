# mini-etl 🚀

> Harici kütüphane bağımlılığı olmadan (yalnızca Python stdlib), bellek dostu streaming mimarisiyle çalışan, hata yönetimli (*dead-letter*) ve CLI destekli hafif, modüler bir ETL kütüphanesi.

## 📊 Sonuçlar & Metrikler (DoD Standartları)
| Metrik | Durum / Değer |
|---|---|
| **Test Başarısı** | 8/8 Test Geçti (%100) |
| **Test Kapsamı (Coverage)** | **%91** (`pytest-cov`, Hedef: %85+) |
| **Tip Güvenliği** | Mypy Strict (Sıfır Hata) |
| **Bellek Tüketimi (Streaming)** | **~185 MB RAM** (~5 GB veri seti testi için) |

---

## 🏗️ Mimari ve Tasarım
Proje 3 temel katman ve motor yapısından oluşur:
1. **Source (Kaynak):** `Protocol` tabanlı arayüz ile CSV/SQLite kaynaklarından `generator` (`yield`) kullanarak bellek dostu veri okuma[cite: 1].
2. **Transform (Dönüşüm):** `>>` (`__rshift__`) operatör aşırı yüklemesi ile akışkan boru hattı (pipeline) kompozisyonu[cite: 1].
3. **Sink (Hedef):** İşlenen verilerin CSV veya SQLite veritabanına güvenle yazılması[cite: 1].
4. **Engine & Hata Yönetimi:** Akışı yöneten ve hatalı satırları ana akışı patlatmadan `dead_letter` dosyasına ayıran güvenli motor katmanı[cite: 1].

---

## ⚙️ Nasıl Çalıştırılır?

### Kurulum ve Bağımlılıklar
```bash
uv sync --link-mode=copy
uv add typer
```

---

## 🏎️ Ödev 2.3: Performans Yarışması Sonuçları
~500.000 satırlık (~25 MB) log dosyası üzerinde 4 farklı agregasyon yönteminin süre ve bellek karşılaştırması:

| Yöntem | Süre (sn) | Peak Bellek (MB) | Teknik Açıklama |
|---|---|---|---|
| **a) Naive Line Loop** | 1.9998 | 105.90 | Tüm dosya `.readlines()` ile belleğe liste olarak yüklendiği için yüksek bellek harcar. |
| **b) Generator + Counter** | 1.6035 | **0.05** | `yield` tabanlı akış (`streaming`) kullanıldığı için RAM tüketimi sıfıra yakındır. |
| **c) Multiprocessing Chunk** | 3.4399 | 153.20 | Süreçler arası veri aktarımı (`IPC`) ek yükü ve chunk maliyeti nedeniyle bu veri boyutunda dezavantajlıdır. |
| **d) Polars** | **0.1314** | **0.02** | Rust tabanlı vektörel motoru sayesinde en hızlı ve en verimli sonuçları verir. |


---

## 🌐 Ödev 2.4: Async API İstemcisi Performans Testi
Açık bir API'den (JSONPlaceholder) toplam 1000 adet kaydın çekilme süresi ve yöntem karşılaştırması:

| Yöntem | Süre (sn) | Başarı | Teknik Açıklama |
|---|---|---|---|
| **(a) Senkron (requests)** | 360.84 | 1000/1000 | İstekler sırayla atıldığı için her yanıt beklendi (Bloklama). |
| **(b) Asenkron (httpx)** | 215.87 | 1000/1000 | `asyncio` ile eşzamanlı istek atıldı. **1.7 kat** daha hızlı tamamlandı. |

### Rate Limit (429) ve Hata Yönetimi
Birim zamanda çok fazla istek atıldığında sunucunun engellemesine (Rate Limit) takılmamak ve olası ağ kopmalarını yönetmek için iki kalkan kullanıldı:
1. **Önleyici (Semaphore):** Asenkron hızın sunucuyu boğmasını engellemek için `asyncio.Semaphore(10)` ile aynı anda maksimum 10 isteğe izin verildi (Client-side throttling).
2. **Kurtarıcı (Retry & Exponential Backoff):** Test sırasında 178. istekte yaşanan ağ hatasında programın çökmesi engellendi; hata yakalanarak artan sürelerle (1s, 2s, 4s...) yeniden denenmesi (retry) sağlandı.


---

## 📚 Bölüm 2: Araştırma ve Dokümantasyon (Ödev 2.5 ve 2.6)

Projenin bu aşamasında istenen teorik araştırmalar (Ödev 2.5) ve teknik soruların cevapları (Ödev 2.6) aşağıdaki dokümanlarda derlenmiştir:

* **[Python GIL (Global Interpreter Lock) İncelemesi](docs/gil_arastirmasi.md)**
  > Python'un GIL mekanizmasının veri işleme süreçlerine etkisi ve çoklu iş parçacığı/işlem (multithreading vs multiprocessing) kavramları üzerine araştırma notları.

* **[Veri İşleme Kodlarında Test Stratejileri](docs/veri_test_stratejileri.md)**
  > Veri boru hatlarında oluşabilecek hatalara karşı Şema, İnvaryant, Altın Dosya ve Özellik Tabanlı (Property-Based) test kavramlarının incelenmesi. (Not: Özellik tabanlı testin pratik uygulaması `scripts/data_test_demo.py` dosyasında yapılmıştır).

* **[Bölüm 2 Kontrol Soruları](docs/kontrol_sorulari_bolum2.md)**
  > Veri yapıları (`list` vs `deque`), büyük veri işleme (Out-of-Core, Chunking vb.) ve test mimarisi üzerine sorulan teknik soruların yanıtları.