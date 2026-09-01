import pytest
from mini_etl.sources import CSVSource

def test_csv_source_reads_data(tmp_path):
    # Geçici bir CSV dosyası yaratalım
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("id,name,age\n1,Ali,25\n2,Ayşe,30\n", encoding="utf-8")

    # Kaynağı oluşturalım
    source = CSVSource(file_path=csv_file)
    
    # Veriyi akış (generator) üzerinden okuyalım
    rows = list(source.read())

    assert len(rows) == 2
    assert rows[0] == {"id": "1", "name": "Ali", "age": "25"}
    assert rows[1] == {"id": "2", "name": "Ayşe", "age": "30"}