# 🔍 Ödev 2.5 Araştırma: Python GIL (Global Interpreter Lock) Gerçeği, Kendi Benchmark'ım ve Çözüm Yolları

Python'la veri mühendisliği veya arka uç (backend) geliştirme yaparken eninde sonunda çarpacağımız somut bir duvar var: GIL, yani Global Interpreter Lock. Teorik olarak her yerde "Python aynı anda sadece tek bir thread çalıştırır" cümlesini okuyoruz ama bunun geliştirici tarafındaki pratik karşılığı tam olarak ne? Bu yazıda GIL'in neden var olduğunu, veri işleme süreçlerini nasıl etkilediğini ve yazdığım test betiğiyle performans üzerindeki gerçek etkisini tüm şeffaflığıyla inceledim.

## GIL Nedir ve Gerçekte Hangi Sorunu Çözer?

Kullandığımız standart ve en yaygın Python yorumlayıcısı olan CPython, arka planda bellek yönetimi için "Reference Counting" (Referans Sayımı) adı verilen bir yöntem kullanıyor. Yani hafızadaki bir değişkene (örneğin devasa bir DataFrame'e veya bir listeye) kodun kaç farklı yerinden işaret edildiğini sürekli sayıyor. Bu sayı sıfıra indiğinde ise Garbage Collector (Çöp Toplayıcı) devreye girip o değişkeni bellekten siliyor. 

Eğer GIL olmasaydı ve biz C++ veya Java'daki gibi özgürce çoklu thread (multithreading) kullansaydık, iki farklı thread aynı anda bu referans sayacını değiştirmeye çalışabilirdi. Bu da "Race Condition" dediğimiz meşhur yarış durumuna, hafıza sızıntılarına veya programın aniden işletim sistemi seviyesinde çökmesine yol açardı. Python'un yaratıcıları, her bir bellek nesnesine ayrı ayrı kilit (fine-grained lock) koyup dili aşırı karmaşıklaştırmak ve yavaşlatmak yerine, tüm yorumlayıcıyı (interpreter) tek bir devasa kilit altına almayı seçmişler. 

Özetle GIL; aynı anda sadece tek bir yerel iş parçacığının (thread) Python kodunu çalıştırmasına izin veren bir güvenlik önlemidir. Bilgisayarımız isterse 32 çekirdekli olsun, standart bir Python kodu tek bir çekirdek üzerinde sürekli bağlam değişimi (context switch) yaparak çalışmaya mahkumdur.

## Benchmark Testim: Teori Pratiğe Karşı

GIL'in sadece kitaplarda yazan bir teori olmadığını görmek ve sınırlarını anlamak için `gil_benchmark.py` adında bir performans testi hazırladım. Testi iki farklı dünya için kurguladım: Biri işlemciyi sonuna kadar yoran (CPU-bound) matematiksel bir görev, diğeri ise ağdan yanıt beklemeye odaklı (I/O-bound) bir görev.

Bilgisayarımda elde ettiğim test sonuçları şu şekilde tabloya yansıdı:

| İşlem Türü | Tek Thread Süresi | Çift Thread Süresi | Beklenti vs. Gerçekleşen |
|---|---|---|---|
| **CPU-Bound** | 11.09 sn | 10.33 sn | %50 hızlanma beklerken süre neredeyse hiç değişmedi. |
| **I/O-Bound** | 4.00 sn | 2.00 sn | Süre kusursuz bir şekilde yarıya düştü. Paralellik sağlandı! |

### Neden Böyle Oldu? (Sonuçların Teknik Analizi)

**1. CPU-Bound Durumu (GIL'in Duvar Olduğu Anlar):**
İlk testimde bilgisayara ağır bir matematiksel geriye sayım döngüsü verdim. Çift thread kullandığımda donanımsal olarak sürenin yaklaşık 5.5 saniyeye inmesini beklerdim ama 10.33 saniyede kaldı. Neden? Çünkü GIL, iki thread'in aynı anda matematiksel işlem yapmasına izin vermedi. Thread'ler "kilit bende, hayır şimdi bende" diyerek CPU üzerinde birbirleriyle savaştılar. 
Eğer for döngüleriyle milyonlarca satırlık veri işliyor, görüntü manipülasyonu yapıyor veya yapay zeka matris çarpımları yapıyorsanız `threading` kullanmak hiçbir işe yaramaz. Hatta kilidi alıp verme maliyeti (overhead) yüzünden kodunuz tek thread'li halinden daha yavaş bile çalışabilir. Mini-ETL projemizin performans yarışmasında tam da bu yüzden threading yerine, GIL'i tamamen atlayan `multiprocessing`'i ve Rust tabanlı `Polars` kütüphanesini tercih ettim.

**2. I/O-Bound Durumu (GIL'in Özgür Bıraktığı Anlar):**
İkinci testimde, `time.sleep()` kullanarak ağ üzerinden bir API'ye istek atmışız gibi bir bekleme simülasyonu yaptım. Sonuç beklediğimiz gibi harikaydı: Süre 4 saniyeden tam 2 saniyeye indi. 
Çünkü Python aslında çok akıllı ve optimize bir dil; bir thread ağdan bir JSON cevabı beklerken veya diske bir CSV dosyası yazarken işlemciyi meşgul etmediği için GIL kilidini anında serbest bırakır. Yazdığım asenkron API istemcisi ödevinde 1000 adet kaydı `httpx` ve `asyncio` kullanarak bu sayede bloklanmadan, Rate Limit engellerini aşarak saniyeler içinde tamamlayabildik.

## Eşzamanlılık (Concurrency) ve Paralellik (Parallelism) Farkı

Bu noktada mülakatların vazgeçilmez sorusuna da cevap vermek gerekiyor. Python'da thread'ler ile yaptığımız şey aslında **Paralellik (Parallelism)** değil, **Eşzamanlılıktır (Concurrency)**. 
Paralellik, iki işin gerçekten aynı milisaniyede, iki farklı çekirdekte yapılmasıdır (Bunu Python'da sadece `multiprocessing` ile yapabiliriz). Eşzamanlılık ise, bir iş beklerken diğerine geçilmesi ve dışarıdan bakıldığında ikisinin aynı anda yapılıyormuş gibi bir illüzyon yaratmasıdır (I/O işlemlerindeki thread'ler veya async yapılar). GIL, paralelliği engeller ama eşzamanlılığa asla karışmaz.

## Gelecek Neler Getiriyor? (PEP 703 ve GIL'in Sonu)

Python topluluğu da yıllardır veri bilimcilerin ve mühendislerin bu konudaki serzenişlerinin farkında. Bu yüzden Python 3.13 ile birlikte **PEP 703 (Making the Global Interpreter Lock Optional in CPython)** projesi hayata geçiyor. Artık Python'u derlerken `--disable-gil` bayrağını (flag) kullanarak GIL'siz, serbest bir Python yorumlayıcısı elde edebileceğiz. Bu henüz deneysel bir özellik olsa da, önümüzdeki birkaç yıl içinde veri mühendisliği dünyasında kartların yeniden dağıtılmasına ve Python'un çok çekirdekli işlemcilerde devasa bir hız sıçraması yaşamasına yol açacak.

## Sonuç

Bugünün şartlarında Python'da GIL bir bug veya hata değil, bir mimari tercihtir. Bir yazılım mühendisi olarak asıl mesele, yazdığımız kodun CPU-bound mu yoksa I/O-bound mu olduğunu doğru teşhis edebilmekten geçiyor. Ağ istekleri ve disk işlemlerinde thread'leri veya `asyncio` gibi asenkron yapıları özgürce kullanabilirken; ağır matematiksel veri işleme yüklerinde multiprocessing'e veya C/Rust ile yazılmış, GIL'i arka planda serbest bırakan kütüphanelere (NumPy, Polars) yönelmek, sistem tasarımının en temel kuralıdır.