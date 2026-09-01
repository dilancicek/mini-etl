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