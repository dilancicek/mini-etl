import csv
import logging
from pathlib import Path
from typing import Any, Iterable

# Yapılandırılmış loglama ayarlayalım
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MiniETLEngine")

class ETLEngine:
    """ETL sürecini yöneten, hata (dead-letter) toplayan ve özet rapor çıkaran motor."""
    def __init__(
        self,
        source: Any,
        pipeline: Any,
        sink: Any,
        dead_letter_path: Path | str
    ):
        self.source = source
        self.pipeline = pipeline
        self.sink = sink
        self.dead_letter_path = Path(dead_letter_path)

    def run(self) -> dict[str, int]:
        logger.info("ETL süreci başlatılıyor...")
        
        read_count = 0
        success_rows = []
        error_rows = []

        # 1. Extract (Veriyi oku)
        try:
            raw_data = self.source.read()
        except Exception as e:
            logger.error(f"Veri kaynağı okunamadı: {e}")
            raise e

        # 2. Transform & Validation (Dönüştür ve satır bazlı hata yönetimi yap)
        # Pipeline tek bir transform veya zincir olabilir
        if hasattr(self.pipeline, "transform"):
            transformed_stream = self.pipeline.transform(raw_data)
        else:
            transformed_stream = raw_data

        for row in raw_data: # Not: Satır bazlı denetim için ham veriden işleme alıyoruz
            read_count += 1
            try:
                # Tekil satıra dönüşüm/doğrulama uygulayalım
                # Pipeline zinciri içinde satır bazlı hata yakalama:
                if hasattr(self.pipeline, "func"):
                    processed_row = self.pipeline.func(dict(row))
                else:
                    processed_row = row
                success_rows.append(processed_row)
            except Exception as err:
                logger.warning(f"Satır işlenemedi (Dead-letter'a atılıyor): {row} | Hata: {err}")
                error_row = dict(row)
                error_row["error_reason"] = str(err)
                error_rows.append(error_row)

        # 3. Load (Başarılı verileri Sink'e yaz)
        self.sink.write(success_rows)

        # 4. Hatalı verileri Dead-letter dosyasına yaz
        if error_rows:
            self._write_dead_letters(error_rows)

        summary = {
            "read_count": read_count,
            "success_count": len(success_rows),
            "error_count": len(error_rows)
        }

        logger.info(f"ETL Tamamlandı. Özet: {summary}")
        return summary

    def _write_dead_letters(self, error_rows: list[dict[str, Any]]) -> None:
        if not error_rows:
            return
        
        fieldnames = list(error_rows[0].keys())
        with open(self.dead_letter_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in error_rows:
                writer.writerow(row)