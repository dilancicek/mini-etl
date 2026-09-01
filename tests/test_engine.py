import pytest
from pathlib import Path
from mini_etl.sources import CSVSource
from mini_etl.transforms import MapTransform
from mini_etl.sinks import CSVSink
from mini_etl.engine import ETLEngine

def test_etl_engine_execution(tmp_path):
    # 1. Kaynak dosya hazırlayalım (biri doğru, biri yaş alanında hata potansiyeli olan satırlar)
    input_file = tmp_path / "input.csv"
    input_file.write_text("id,name,age\n1,Ali,25\n2,Ayşe,invalid_age\n", encoding="utf-8")

    output_file = tmp_path / "output.csv"
    dead_letter_file = tmp_path / "dead_letter.csv"

    source = CSVSource(file_path=input_file)
    sink = CSVSink(file_path=output_file, fieldnames=["id", "name", "age"])

    # Yaş alanını int'e çeviren, hata verirse satırı reddeden bir dönüşüm yazalım
    def safe_transform(row):
        try:
            row["age"] = int(row["age"])
            return row
        except ValueError:
            raise ValueError("Geçersiz yaş formatı")

    transform = MapTransform(safe_transform)

    # Motoru kuralım
    engine = ETLEngine(
        source=source,
        pipeline=transform,
        sink=sink,
        dead_letter_path=dead_letter_file
    )

    summary = engine.run()

    # Kontroller
    assert summary["read_count"] == 2
    assert summary["success_count"] == 1  # Sadece Ali başarılı olmalı
    assert summary["error_count"] == 1    # Ayşe dead-letter'a gitmeli
    assert output_file.exists()
    assert dead_letter_file.exists()