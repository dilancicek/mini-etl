# 🔍 Ödev 2.5 Araştırma: Veri İşleme Kodu Nasıl Test Edilir? Sessiz Hataları Yakalama Sanatı

## 1. Giriş: Veri Kodunu Test Etmek Neden Geleneksel Yazılımdan Farklıdır?

Standart yazılım mühendisliğinde test yazmak, genellikle bir fonksiyonun beklenen girdilere karşı doğru çıktıları üretip üretmediğini kontrol etmekten ibarettir. Örneğin bir web uygulamasında kullanıcı giriş (login) fonksiyonunu test ederken, doğru şifreyle sisteme girilebildiğini, yanlış şifreyle sistemin hata mesajı döndürdüğünü (Exception) doğrularsınız. Geleneksel yazılımda kod ya çalışır ya da çöker. Çöken kodu yakalamak ve düzeltmek nispeten kolaydır.

Ancak veri mühendisliği, ETL (Extract, Transform, Load) süreçleri ve Makine Öğrenmesi (ML) boru hatlarında durum çok daha karmaşık ve sinsidir. Veri işleme kodlarında en büyük kabus, kodun hata vermesi (crash) değil, **hata vermeden yanlış veri üretmesidir (Silent Failures / Sessiz Hatalar)**. 

Bir `pandas` veya `polars` veri çerçevesine (DataFrame) milyarlarca satır veri yüklediğinizi hayal edin. Eğer dönüşüm (transform) adımında bir `LEFT JOIN` işlemi sırasında anahtar (key) eşleşmelerini yanlış kurguladıysanız ve satırlar kopyalanarak çoğaldıysa (fan-out), sisteminiz hiçbir şekilde çökmez. Başarıyla çalışır, yeşil tik alır ve süreci tamamlar. Fakat günün sonunda şirketin yönetim kuruluna giden rapordaki aylık ciro iki kat fazla görünür. Veya makine öğrenmesi modelinize giden eğitim verisinde "Yaş" kolonu sessizce "NULL" değerlerle dolarsa, model çöp üretir (Garbage In, Garbage Out). 

İşte bu yüzden veri işleme kodunu test etmek; sadece algoritmik mantığı (logic) değil, **verinin doğasını, yapısını, sınırlarını ve istatistiksel dağılımını test etmeyi** gerektirir. Sektördeki kıdemli veri mühendislerini diğerlerinden ayıran en temel fark, bu "sessiz hataları" üretime (production) çıkmadan yakalayacak savunma hatlarını kurabilmeleridir. Bu araştırma yazısında, güvenilir bir veri boru hattı kurmak için kullanılması gereken dört altın test stratejisini ve kendi projeme entegre ettiğim pratik test laboratuvarımın sonuçlarını derinlemesine inceleyeceğiz.

---

## 2. Şema Testi (Schema Testing): Sınır Kapısındaki Güvenlik

Bir veri hattına (pipeline) dış dünyadan, API'lerden, bulut depolama alanlarından veya ilişkisel veritabanlarından sürekli yeni veri akar. Dış dünyanın kaotik yapısı nedeniyle bu verilerin formatı her an, habersizce değişebilir. Kaynak sistemdeki bir backend geliştiricisi, veritabanındaki "Tarih" kolonunun adını "Kayit_Tarihi" olarak değiştirebilir veya "Musteri_ID" kolonuna yanlışlıkla tamsayı (Integer) yerine metin (String) veri göndermeye başlayabilir. 

Şema testi, verinin işlenme mantığından ziyade **yapısını** kontrol eden ilk savunma hattıdır. Kodumuzun veriyi işlemeye başlamadan önce katı bir "sınır kapısı" kontrolünden geçirmesi prensibine dayanır.

**Neleri Kontrol Ederiz?**
* **Kolon İsimleri ve Varlığı:** Beklediğimiz tüm kritik kolonlar eksiksiz olarak veri setinde bulunuyor mu?
* **Veri Tipleri (Data Types):** "Fiyat" kolonu kesinlikle Float veya Integer mı? İçine yanlışlıkla bir para birimi sembolü (₺, $) karışmış mı?
* **Eksik Veri (Nullability):** "Kullanıcı_ID" kolonu asla NULL (boş) olmamalıdır, bu kural ihlal edilmiş mi?
* **Değer Aralıkları ve Kategoriler:** "Yaş" kolonu 0 ile 120 arasında mı? "Sipariş_Durumu" kolonu sadece 'Kargolandı', 'Hazırlanıyor' veya 'İptal' değerlerinden mi oluşuyor?

**Python Ekosisteminde Uygulama:**
Python dünyasında şema testleri için genellikle `Great Expectations` veya `Pandera` gibi gelişmiş kütüphaneler kullanılır. Özellikle `Pandera`, veri çerçevelerimizi (DataFrame) tıpkı `Pydantic` ile API verilerini doğrular gibi katı kurallarla tanımlamamıza olanak sağlar. Boru hattına giren veri bu şema testinden geçemezse, kod erken aşamada bilerek çökertilir (Fail Fast stratejisi) ve kirli verinin, sistemin ileriki aşamalarını zehirlemesi kesin olarak engellenir.

---

## 3. İnvaryant (Invariant) Testleri: Asla Değişmemesi Gereken Gerçekler

Matematikte ve bilgisayar bilimlerinde İnvaryant (Değişmez), bir işlem veya dönüşüm uygulandıktan sonra bile **doğruluğunu koruması gereken evrensel ve mantıksal koşuldur**. Veri dönüşüm adımlarımızı (Transform) test ederken, gigabaytlarca büyüklükteki veri setlerinin her bir satırını gözle kontrol etmemiz imkansızdır. Bunun yerine, verinin bütününe dair makro kurallar belirleriz.

**Veri İşlemede Kritik İnvaryant Örnekleri:**
1. **Filtreleme İnvaryantı:** Eğer bir veriyi `yas >= 18` koşuluyla filtreliyorsak, işlemden çıkan sonuç veri setindeki satır sayısı, giren veri setindeki satır sayısından **kesinlikle küçük veya ona eşit** olmak zorundadır. Asla daha fazla satır üretemez.
2. **Toplamsal (Conservation of Mass) İnvaryant:** E-ticaret verilerinde kullanıcıların işlem hareketlerini günlük olarak gruplayıp topladığımızı (GroupBy) varsayalım. İşlem öncesindeki ham tablodaki "Toplam Ciro" ile, gruplanmış ve küçültülmüş tablodaki "Toplam Ciro" birbirine kuruşu kuruşuna eşit olmak zorundadır. Veri küçülse de değer kaybolmamalıdır.
3. **Benzersizlik (Uniqueness) İnvaryantı:** İki farklı tabloyu birleştirirken (LEFT JOIN veya INNER JOIN) kullandığımız anahtar kolon (Primary Key), birleştirme işlemi sonucunda hala tekil (unique) kalmalıdır. Eğer bu koldaki tekillik bozuluyor ve satır sayısı artıyorsa, hatalı bir "fan-out" (satır patlaması) durumu yaşanmış demektir ve bu hemen yakalanmalıdır.

İnvaryant testleri, veri kodlarının içine `assert` komutlarıyla statik olarak yerleştirilir. Bu testler, kodunuzdaki matematiksel ve mantıksal hataları, karmaşık dış birim testlerine ihtiyaç duymadan verinin kendi doğası üzerinden anında yakalamanızı sağlar.

---

## 4. Altın Dosya (Golden File / Snapshot) Testleri: Güvenli Refactoring

Gerçek iş dünyasında, bazen içinde yüzlerce satır SQL sorgusu veya karmaşık, iç içe geçmiş `pandas` dönüşümleri olan, spagettiye dönmüş eski (legacy) kod tabanları devralırsınız. Bu kodun iç mantığını veya neden o şekilde yazıldığını kimse tam olarak bilmez, ancak sistemin mevcut durumda **doğru çalıştığı ve doğru iş raporları ürettiği** herkes tarafından kabul edilir.

Sizin mühendis olarak göreviniz bu eski kodu daha temiz, daha bakımı kolay ve daha hızlı çalışacak şekilde (örneğin eski bir Pandas kodunu modern ve yüksek performanslı Polars koduna geçirerek) yeniden yazmaktır (Refactoring). Ancak kodu tamamen değiştirirken hiçbir iş mantığını bozmadığınızdan nasıl emin olacaksınız? İşte burada **Altın Dosya (Golden File / Snapshot)** testleri hayat kurtarır.

**Altın Dosya Testi Nasıl Çalışır?**
1. Sistemdeki eski (legacy) kod parçasına sabit ve değişmez (deterministik) bir girdi dosyası verilir.
2. Kodun ürettiği çıktı (örneğin 150 kolonlu karmaşık bir Parquet veya CSV dosyası) diske kaydedilir. Bu dosya bizim "Altın Dosyamızdır" (Doğruluğundan kesinlikle emin olduğumuz, referans başucu kaynağımız).
3. Sonrasında siz kodu modernize edersiniz, fonksiyonları parçalar, mimariyi tamamen değiştirirsiniz.
4. Yeni yazdığınız kod, aynı girdiyle tekrar çalıştırılır ve ürettiği yeni çıktı, Altın Dosya ile bayt-bayt (byte-by-byte) karşılaştırılır.

Eğer yeni kodunuz Altın Dosya ile birebir aynı çıktıyı üretiyorsa, refactoring işleminiz başarıyla ve güvenle tamamlanmış demektir. `pytest-snapshot` veya `syrupy` gibi Python eklentileri bu süreci tam otomatik hale getirir. Mühendisler, ne yaptığını bilmedikleri yüzlerce satır kod için yüzlerce ayrı assertion (doğrulama) yazmak yerine Altın Dosya testini tercih ederek hem zamandan tasarruf eder hem de güvenliği maksimuma çıkarır.

---

## 5. Özellik Tabanlı Test (Property-Based Testing) ve Kendi Laboratuvar Testim

Geleneksel birim testlerinde (Unit Tests), kodumuza sabit, kendi uydurduğumuz girdiler veririz. Örneğin, bir metin temizleme fonksiyonuna `" Dilan "` stringini veririz ve çıktının boşluklardan arındırılmış `"dilan"` olmasını bekleriz. Ancak bu yöntem sadece mühendisin hayal gücüyle ve aklına gelen senaryolarla sınırlıdır. Gerçek dünyada kullanıcı verileri çok acımasızdır; sisteme Japonca karakterler, UTF-8 emojiler, sonsuz uzunlukta metinler, Null değerler veya özel SQL sembolleri gelebilir.

**Property-Based Testing (Özellik Tabanlı Test)**, koda manuel örnek girdiler yazmak yerine, verinin **"özelliklerini" (properties)** tanımladığımız ve bilgisayarın bizim yerimize binlerce uç durumu (edge case) test ettiği gelişmiş bir yaklaşımdır.

### Kendi Projemdeki Test Deneyimim (Hypothesis Kütüphanesi)
Bu teoriyi doğrulamak ve kodun sınırlarını zorlamak için projemin `scripts/data_test_demo.py` dosyasında ufak bir laboratuvar deneyi hazırladım. Test için Python'un endüstri standardı olan `hypothesis` kütüphanesini kullandım.

Sistemde yaş verilerini temizleyen basit bir `yasi_temizle()` fonksiyonu yazdım. Kuralım basitti: Fonksiyon yaş değerini 0 ile 120 arasında bir tamsayı olarak dönmeli, hatalı her türlü durumda ise çökmek yerine `None` dönmeliydi. 

Geleneksel test yazmak yerine `hypothesis`'e şu talimatı verdim:
`@given(st.text())` -> "Bana rastgele string (metin) verileri üret ve fonksiyonuma yolla."

Belirlediğim İnvaryant (Kural) ise şuydu:
`assert sonuc is None or (0 <= sonuc <= 120)` -> "Sonuç ya None olmalı ya da 0-120 arasında bir sayı. **Kod KESİNLİKLE ÇÖKMEMELİ.**"

**Testin Sonucu:**
Terminalde `pytest` üzerinden çalıştırdığımda, `hypothesis` arka planda fonksiyona yüzlerce akıl almaz metin formatı gönderdi. Boş stringler, semboller, devasa karakter blokları... Ve test **%100 PASSED (Başarılı)** sonucunu verdi. Kodum hiçbir saçma girdi karşısında çökmedi veya Exception fırlatmadı. Eğer fonksiyonumda en ufak bir tip dönüşümü (type casting) açığı olsaydı, `hypothesis` kütüphanesi saniyesinde o spesifik girdiyi bulup "İşte bu metin kodunu çökertti!" diyerek hatayı yüzüme vuracaktı. Özellik tabanlı testler, özellikle veri ayrıştırma (parsing) ve temizleme operasyonlarında kodun dayanıklılığını (robustness) kanıtlamanın en kesin yoludur.

---

## 6. Sonuç ve Üretime Alma (Production) Vizyonu

Yani işin özü ham yazılım kodlarına test yazmak yazılım mühendisliğinin temeli olsa da, gigabaytlarca veriyi işleyen boru hatlarında veri kalitesini ve doğruluğunu sağlamak bambaşka ve çok daha geniş bir vizyon gerektirir. 

1. **Şema testleri** ile sisteme giren veriyi sınır kapısında denetler,
2. **Property-Based testler** ile fonksiyonlarımızın dış dünyadan gelen acımasız kirliliğe karşı dayanıklılığını sınar,
3. **İnvaryant testleri** ile kodun yaptığı işlemlerin matematiksel doğruluğunu garantiye alır,
4. **Golden File testleri** ile de sistemin genel bütünlüğünü bozmadan güvenle kod modernizasyonu yaparız.

Bir sistem tasarımı mülakatında veya gerçek bir "Production" (Üretim) ortamında "Yazdığım veri boru hattının sessizce hata yapmadığından nasıl emin olabilirim?" sorusuna verilecek en olgun ve profesyonel cevap, işte bu dört katmanlı savunma hattını CI/CD süreçlerine entegre edebilmektir. Çünkü mükemmel bir veri sistemi, sadece hızlı çalışan değil, ne zaman kirlendiğini anında haber veren sistemdir.