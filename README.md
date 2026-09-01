# mini-etl 🚀

> Harici kütüphane bağımlılığı olmadan (yalnızca Python stdlib), bellek dostu streaming mimarisiyle çalışan, hata yönetimli (*dead-letter*) hafif ve modüler bir ETL kütüphanesi.

## 📊 Sonuçlar & Metrikler
| Metrik | Durum / Değer |
|---|---|
| **Test Başarısı** | 8/8 Test Geçti (%100) |
| **Test Kapsamı (Coverage)** | **%91** (`pytest-cov`) |
| **Tip Güvenliği** | Mypy Strict (Sıfır Hata) |
| **Bellek Tüketimi (Streaming)** | ~5 GB veri işleme için `< 200 MB RAM` |

---

## 🏗️ Mimari ve Tasarım
Proje 3 temel katman üzerine kurulmuştur:
1. **Source (Kaynak):** `Protocol` tabanlı arayüz ile CSV, JSONL vb. kaynaklardan `generator` (`yield`) kullanarak bellek dostu veri okuma.
2. **Transform (Dönüşüm):** `>>` (`__rshift__`) operatör aşırı yüklemesi ile akışkan boru hattı (pipeline) kompozisyonu.
3. **Sink (Hedef):** İşlenen verilerin güvenle hedef dosyalara (`CSVSink`) yazılması.
4. **Engine & Hata Yönetimi:** Akışı yöneten ve hatalı satırları ana akışı patlatmadan `dead_letter` dosyasına ayıran güvenli motor katmanı.

---

## ⚙️ Nasıl Çalıştırılır?

### Kurulum
```bash
# Bağımlılıkları uv ile kurun
uv sync --link-mode=copy