import csv
import sqlite3
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

class SQLiteSink:
    """İşlenen verileri SQLite veritabanına yazan hedef sınıfı."""
    def __init__(self, db_path: Path | str, table_name: str):
        self.db_path = Path(db_path)
        self.table_name = table_name

    def write(self, data: Iterable[dict[str, Any]]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        rows = list(data)
        if not rows:
            conn.close()
            return

        # Tabloyu dinamik olarak oluşturmak için ilk satırın anahtarlarını alalım
        first_row = rows[0]
        columns = list(first_row.keys())
        columns_def = ", ".join([f'"{col}" TEXT' for col in columns])
        
        cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        cursor.execute(f"CREATE TABLE {self.table_name} ({columns_def})")

        placeholders = ", ".join(["?" for _ in columns])
        insert_sql = f"INSERT INTO {self.table_name} ({', '.join([f'\"{c}\"' for c in columns])}) VALUES ({placeholders})"

        values = [[str(row.get(col, "")) for col in columns] for row in rows]
        cursor.executemany(insert_sql, values)

        conn.commit()
        conn.close()