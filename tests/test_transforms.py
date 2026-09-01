import pytest
from mini_etl.transforms import BaseTransform, MapTransform, PipelineChain
from mini_etl.sinks import CSVSink

def test_map_transform():
    # Gelen sözlükteki yaşları integer'a çeviren bir dönüşüm fonksiyonu yazalım
    def parse_age(row):
        row["age"] = int(row["age"])
        return row

    transform = MapTransform(parse_age)
    
    input_data = [{"name": "Ali", "age": "25"}]
    result = list(transform.transform(input_data))

    assert result == [{"name": "Ali", "age": 25}]

def test_base_transform_not_implemented():
    """BaseTransform doğrudan çağrıldığında NotImplementedError vermeli."""
    base = BaseTransform()
    with pytest.raises(NotImplementedError):
        list(base.transform([]))

def test_pipeline_chain_execution(tmp_path):
    """>> operatörü ile kurulan pipeline zincirinin çalışmasını test edelim."""
    output_file = tmp_path / "chain_out.csv"

    def uppercase_name(row):
        row["name"] = row["name"].upper()
        return row

    transform = MapTransform(uppercase_name)
    sink = CSVSink(file_path=output_file, fieldnames=["name"])

    # Transform ile Sink'i >> operatörüyle zincirleyelim
    pipeline = transform >> sink
    
    data = [{"name": "zeynep"}]
    pipeline.execute(data)

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "ZEYNEP" in content

def test_pipeline_chain_invalid_step():
    """Pipeline içine geçersiz bir adım verilirse TypeError fırlatmalı."""
    chain = PipelineChain(["gecersiz_adim_tipi"])
    with pytest.raises(TypeError):
        chain.execute([{"test": "data"}])