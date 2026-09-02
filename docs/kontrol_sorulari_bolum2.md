# 🎯 Ödev 2.6: Bölüm 2 Kontrol Soruları

### 1. `list` yerine `deque` kullanmam gereken bir senaryo yaz ve big-O ile gerekçelendir.
Veri yapıları dersindeki "dizi" (array) ve "bağlı liste" (linked list) farkından yola çıkarsak: Python'daki standart `list` yapısı aslında arka planda dinamik bir dizidir. Eğer İlk-Giren-İlk-Çıkar (FIFO) mantığıyla çalışan bir görev kuyruğu (queue) sistemi kuruyorsak ve listenin en başından sürekli eleman silmemiz (`pop(0)`) gerekiyorsa, dizideki geri kalan tüm elemanların hafızada birer adım sola kaydırılması gerekir. Bu kaydırma işleminin zaman karmaşıklığı **O(n)**'dir ve veri büyüdükçe sistemi tıkar.

Ancak `collections.deque` çift yönlü bağlı liste (doubly linked list) yapısındadır. Listenin hem başına hem de sonuna müdahale etmek için işaretçileri (pointer) kullanır. Bu yüzden `deque` kullanarak baştan eleman çıkarmak (`popleft()`) veya eklemek (`appendleft()`) her zaman sabit zamanlı yani **O(1)** maliyetindedir. Kuyruk operasyonlarında kesinlikle `deque` tercih edilmelidir.

### 2. Bir decorator'da `functools.wraps` kullanmazsam ne kaybederim?
Asıl fonksiyonumuzun "kimliğini" (metadata) kaybederiz. Bir fonksiyona decorator uyguladığımızda, asıl fonksiyonumuz içteki "wrapper" (sarmalayıcı) fonksiyonun kılığına bürünür. Eğer `functools.wraps` kullanmazsak; fonksiyonumuzun adını (`__name__`) sorguladığımızda asıl ismi yerine "wrapper" sonucunu alırız. Ayrıca yazdığımız docstring (`__doc__`) açıklamaları ve tip bildirimleri (type hints) de tamamen silinir. 
Bu durum özellikle hata ayıklama (debug) yaparken logların anlamsızlaşmasına, kodun dokümantasyon araçlarıyla (Sphinx vb.) otomatik üretilememesine veya FastAPI gibi fonksiyon isimlerine duyarlı modern kütüphanelerin çökmesine neden olur.

### 3. `Protocol` ile `ABC` arasındaki farkı bir örnekle anlat.
İkisi de arayüz (interface) tanımlamak için kullanılır ancak yaklaşımları farklıdır:
*   **ABC (Abstract Base Class):** İsimsel (nominal) alt tipleme yapar. Bir sınıfın ABC kurallarına uyması için, o sınıftan açıkça miras (inherit) alması şarttır. (Örn: `class Kedi(HayvanABC):`)
*   **Protocol:** Yapısal (structural / duck typing) alt tipleme yapar. Miras almaya gerek yoktur. 

**Örnek:** Dışarıdan (örneğin bir pip paketinden) indirdiğimiz ve kaynak kodunu değiştiremediğimiz bir `BankaAPI` sınıfı olsun ve içinde `odeme_yap()` metodu bulunsun. ABC kullansaydık `BankaAPI` koduna müdahale edip kendi ABC sınıfımızdan miras aldırmamız gerekirdi ki bu imkansızdır. Ancak `OdemeSistemi(Protocol)` tanımlarsak, Python `BankaAPI` sınıfına hiç dokunmadan sırf içinde `odeme_yap()` metodu var diye onu otomatik olarak bizim protokolümüze uygun kabul eder.

### 4. 100 GB'lık CSV'yi 8 GB RAM'de nasıl işlerim? 3 farklı strateji.
1.  **Chunking / Generator Mantığı:** Veriyi tek seferde RAM'e yüklemek yerine `pandas.read_csv(chunksize=10000)` kullanarak veya saf Python'da satır satır (`yield` ile) okuyarak işlerim. Akış (streaming) mantığıyla her adımda sadece küçük bir parça RAM'de tutulur.
2.  **Out-of-Core (Disk-Tabanlı) Motorlar:** Veriyi doğrudan belleğe çekmek yerine, disk üzerinde sorgulama yapabilen DuckDB gibi araçlar veya veriyi sadece ihtiyaç anında işleyen "Lazy Evaluation" (Tembel Değerlendirme) yeteneğiyle Polars kütüphanesini kullanırım.
3.  **Dağıtık/Bölümlü İşleme (Partitioning):** Dask veya PySpark gibi büyük veri kütüphaneleri kullanarak veriyi küçük partisyonlara bölerim. Bu araçlar, görevleri çekirdeklere dağıtır ve RAM dolma noktasına geldiğinde veriyi diske taşır (spilling), böylece "Out of Memory" hatası engellenir.

### 5. `pytest` fixture'ının `scope` parametresi ne işe yarar, veritabanı testinde hangisini seçerim?
`scope` parametresi, o fixture'ın (test hazırlık fonksiyonunun) ne kadar süre hayatta kalacağını ve testler boyunca kaç kez baştan çalıştırılacağını belirler (`function`, `class`, `module`, `session`).
Veritabanı testlerinde hibrit bir strateji uygularım:
*   Veritabanı motorunu ayağa kaldırmak ve ilk bağlantı havuzunu (connection pool) kurmak çok ağır bir işlem olduğu için bağlantı fixture'ını **`scope="session"`** yaparım. (Tüm test süresince sadece 1 kez çalışır).
*   Ancak testlerin birbirini etkilememesi (izolasyon) ve her testin temiz bir veritabanıyla başlaması hayati önem taşır. Bu yüzden işlemi başlatan ve test bitince geri alan (transaction/rollback) fixture'ı **`scope="function"`** olarak ayarlarım. Böylece bağlantı sabit kalırken, veri her testte sıfırlanmış olur.