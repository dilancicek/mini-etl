import csv
from pathlib import Path
from typing import Any, Dict, Generator, Protocol, runtime_checkable

@runtime_checkable
class DataSource(Protocol):
    """Tüm veri kaynaklarının uyması gereken ortak protokol (sözleşme)."""
    def read(self) -> Generator[Dict[str, Any], None, None]:
        ...

class CSVSource:
    """CSV dosyalarından bellek dostu (streaming) veri okuyan kaynak sınıfı."""
    def __init__(self, file_path: Path | str):
        self.file_path = Path(file_path)

    def read(self) -> Generator[Dict[str, Any], None, None]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {self.file_path}")
        
        with open(self.file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Her satırı bir sözlük (dict) olarak akıtıyoruz (streaming)
                yield dict(row)