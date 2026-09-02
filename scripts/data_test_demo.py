from hypothesis import given, strategies as st

# 1. Test Edeceğimiz Ufak Veri Temizleme Fonksiyonu
def yasi_temizle(yas_girdisi):
    # Eğer yaş 0-120 arasındaysa sayıyı döner, yoksa hatalı veriler için None döner.
    try:
        yas = int(yas_girdisi)
        return yas if 0 <= yas <= 120 else None
    except (ValueError, TypeError):
        return None

# 2. Property-Based Test (Hypothesis ile Sınırları Zorlamak)
# Kural (İnvaryant): Sisteme ne kadar saçma bir metin girerse girsin, kod KESİNLİKLE ÇÖKMEMELİ!
@given(st.text())
def test_yasi_temizle_asla_cokmez(rastgele_metin):
    sonuc = yasi_temizle(rastgele_metin)
    
    # İnvaryant Kontrolü: Sonuç ya None olmalı ya da 0-120 arasında bir tamsayı.
    assert sonuc is None or (0 <= sonuc <= 120)

if __name__ == "__main__":
    import pytest
    import sys
    print("--- ÖZELLİK TABANLI TEST (PROPERTY-BASED TESTING) BAŞLIYOR ---")
    
    # Bu dosyadaki testleri doğrudan çalıştırıyoruz
    sys.exit(pytest.main([__file__, "-v"]))