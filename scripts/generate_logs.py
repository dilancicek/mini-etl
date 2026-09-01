import random
from pathlib import Path

def generate_log_file(file_path: Path, num_lines: int = 500_000) -> None:
    """Performans testi için büyük bir sentetik log dosyası üretir."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    services = ["auth-service", "payment-service", "order-service", "user-service"]
    
    print(f"Log dosyası üretiliyor ({num_lines} satır)... Lütfen bekleyin.")
    
    with open(file_path, "w", encoding="utf-8") as f:
        for i in range(num_lines):
            level = random.choice(levels)
            service = random.choice(services)
            f.write(f"2026-09-01 12:00:0{i % 60} [{level}] {service}: İşlem ID {i} gerçekleştirildi.\n")
            
    print(f"Log dosyası başarıyla oluşturuldu: {file_path}")

if __name__ == "__main__":
    generate_log_file(Path("data/large_logs.txt"), num_lines=500_000)