import pytest
from pathlib import Path
from mini_etl.sinks import CSVSink

def test_csv_sink_writes_data(tmp_path):
    output_file = tmp_path / "output.csv"
    sink = CSVSink(file_path=output_file, fieldnames=["id", "name"])

    data = [{"id": "1", "name": "Ali"}, {"id": "2", "name": "Ayşe"}]
    sink.write(data)

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "Ali" in content
    assert "Ayşe" in content