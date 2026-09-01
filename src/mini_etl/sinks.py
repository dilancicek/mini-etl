import csv
from pathlib import Path
from typing import Any, Iterable

class CSVSink:
    """İşlenen verileri CSV dosyasına yazan hedef sınıfı."""
    def __init__(self, file_path: Path | str, fieldnames: list[str]):
        self.file_path = Path(file_path)
        self.fieldnames = fieldnames

    def write(self, data: Iterable[dict[str, Any]]) -> None:
        with open(self.file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)