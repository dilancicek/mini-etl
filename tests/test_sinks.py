import csv
import sqlite3

from mini_etl.sinks import CSVSink, SQLiteSink


def test_csv_sink_write(tmp_path):
    # CSV Sink testi
    file_path = tmp_path / "test_output.csv"
    sink = CSVSink(file_path=file_path, fieldnames=["id", "name", "age"])
    
    data = [
        {"id": 1, "name": "Ahmet", "age": 30},
        {"id": 2, "name": "Mehmet", "age": 25}
    ]
    
    sink.write(data)
    
    # Yazılan veriyi okuyup doğrulayalım
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) == 2
    assert rows[0]["name"] == "Ahmet"
    assert rows[1]["age"] == "25"

def test_sqlite_sink_write_normal(tmp_path):
    # SQLite Sink normal veri yazma testi
    db_path = tmp_path / "test.db"
    sink = SQLiteSink(db_path=db_path, table_name="users")
    
    data = [
        {"id": 1, "name": "Ayşe"},
        {"id": 2, "name": "Fatma"}
    ]
    
    sink.write(data)
    
    # Veritabanına bağlanıp verinin yazıldığını doğrulayalım
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    
    assert len(rows) == 2
    # Kodun içindeki dict değerleri string'e (str) çevrildiği için '1' olarak kontrol ediyoruz
    assert rows[0][0] == "1" 
    assert rows[0][1] == "Ayşe"

def test_sqlite_sink_empty_data(tmp_path):
    # SQLite Sink boş veri (early return) testi
    db_path = tmp_path / "test_empty.db"
    sink = SQLiteSink(db_path=db_path, table_name="empty_users")
    
    sink.write([])  # Boş liste gönderiyoruz
    
    # Tablonun hiç oluşmadığını doğrulamamız lazım
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empty_users'")
    table_exists = cursor.fetchone()
    conn.close()
    
    assert table_exists is None