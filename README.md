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

---

## 🏎️ Ödev 2.3: Performans Yarışması Sonuçları
~500.000 satırlık (~25 MB) log dosyası üzerinde 4 farklı agregasyon yönteminin süre ve bellek karşılaştırması:

| Yöntem | Süre (sn) | Peak Bellek (MB) | Teknik Açıklama |
|---|---|---|---|
| **a) Naive Line Loop** | 1.9998 | 105.90 | Tüm dosya `.readlines()` ile belleğe liste olarak yüklendiği için yüksek bellek harcar. |
| **b) Generator + Counter** | 1.6035 | **0.05** | `yield` tabanlı akış (`streaming`) kullanıldığı için RAM tüketimi sıfıra yakındır. |
| **c) Multiprocessing Chunk** | 3.4399 | 153.20 | Süreçler arası veri aktarımı (`IPC`) ek yükü ve chunk maliyeti nedeniyle bu veri boyutunda dezavantajlıdır. |
| **d) Polars** | **0.1314** | **0.02** | Rust tabanlı vektörel motoru sayesinde en hızlı ve en verimli sonuçları verir. |