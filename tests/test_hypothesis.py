from hypothesis import given, strategies as st
from mini_etl.transforms import MapTransform

@given(st.integers(), st.text(min_size=1))
def test_map_transform_with_hypothesis(number_val, text_val):
    """Hypothesis kütüphanesi ile rastgele üretilen binlerce veri üzerinde dönüşüm testi."""
    def double_number(row):
        row["num"] = row["num"] * 2
        return row

    transform = MapTransform(double_number)
    input_row = {"num": number_val, "text": text_val}
    
    result = list(transform.transform([input_row]))
    
    assert len(result) == 1
    assert result[0]["num"] == number_val * 2
    assert result[0]["text"] == text_val