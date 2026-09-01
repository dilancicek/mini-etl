import time
import tracemalloc
from collections import Counter
from pathlib import Path
from multiprocessing import Pool, cpu_count
import polars as pl

LOG_FILE = Path("data/large_logs.txt")

# Ölçüm yardımcı fonksiyonu
def measure_performance(func, name):
    tracemalloc.start()
    start_time = time.perf_counter()
    
    result = func()
    
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    elapsed = end_time - start_time
    peak_mb = peak / (1024 * 1024)
    
    print(f"[{name}] Süre: {elapsed:.4f} saniye | Peak Bellek: {peak_mb:.2f} MB")
    return elapsed, peak_mb, result

# (a) Naif Satır Döngüsü (Tüm dosyayı RAM'e liste olarak al)
def method_naive_loop():
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines() # Belleği şişiren kısım burası
    
    counter = Counter()
    for line in lines:
        if "[INFO]" in line:
            counter["INFO"] += 1
        elif "[WARNING]" in line:
            counter["WARNING"] += 1
        elif "[ERROR]" in line:
            counter["ERROR"] += 1
        elif "[DEBUG]" in line:
            counter["DEBUG"] += 1
    return counter

# (b) Generator + Counter (Bellek dostu akış)
def line_generator(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            yield line

def method_generator_counter():
    counter = Counter()
    for line in line_generator(LOG_FILE):
        if "[INFO]" in line:
            counter["INFO"] += 1
        elif "[WARNING]" in line:
            counter["WARNING"] += 1
        elif "[ERROR]" in line:
            counter["ERROR"] += 1
        elif "[DEBUG]" in line:
            counter["DEBUG"] += 1
    return counter

# (c) Multiprocessing Chunk (Paralel işlem)
def process_chunk(chunk_lines):
    counter = Counter()
    for line in chunk_lines:
        if "[INFO]" in line:
            counter["INFO"] += 1
        elif "[WARNING]" in line:
            counter["WARNING"] += 1
        elif "[ERROR]" in line:
            counter["ERROR"] += 1
        elif "[DEBUG]" in line:
            counter["DEBUG"] += 1
    return counter

def method_multiprocessing():
    chunk_size = 50_000
    chunks = []
    current_chunk = []
    
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            current_chunk.append(line)
            if len(current_chunk) >= chunk_size:
                chunks.append(current_chunk)
                current_chunk = []
    if current_chunk:
        chunks.append(current_chunk)
        
    with Pool(cpu_count()) as pool:
        results = pool.map(process_chunk, chunks)
        
    total_counter = Counter()
    for res in results:
        total_counter.update(res)
    return total_counter

# (d) Polars (Vektörel tarama)
def method_polars():
    # Polars ile hızlı metin tarama
    df = pl.read_csv(LOG_FILE, separator="\t", has_header=False, new_columns=["raw"])
    # Basit string içerik sayımları
    text_col = df["raw"]
    info_count = text_col.str.contains(r"\[INFO\]").sum()
    warn_count = text_col.str.contains(r"\[WARNING\]").sum()
    error_count = text_col.str.contains(r"\[ERROR\]").sum()
    debug_count = text_col.str.contains(r"\[DEBUG\]").sum()
    return {"INFO": info_count, "WARNING": warn_count, "ERROR": error_count, "DEBUG": debug_count}

if __name__ == "__main__":
    print("--- PERFORMANS YARIŞMASI BAŞLIYOR ---")
    
    t_naive, m_naive, _ = measure_performance(method_naive_loop, "a) Naive Line Loop")
    t_gen, m_gen, _ = measure_performance(method_generator_counter, "b) Generator + Counter")
    t_mp, m_mp, _ = measure_performance(method_multiprocessing, "c) Multiprocessing Chunk")
    t_polars, m_polars, _ = measure_performance(method_polars, "d) Polars")
    
    print("\n" + "="*50)
    print(f"{'Yöntem':<25} | {'Süre (sn)':<10} | {'Peak Bellek (MB)':<15}")
    print("-"*50)
    print(f"{'a) Naive Loop':<25} | {t_naive:<10.4f} | {m_naive:<15.2f}")
    print(f"{'b) Generator+Counter':<25} | {t_gen:<10.4f} | {m_gen:<15.2f}")
    print(f"{'c) Multiprocessing':<25} | {t_mp:<10.4f} | {m_mp:<15.2f}")
    print(f"{'d) Polars':<25} | {t_polars:<10.4f} | {m_polars:<15.2f}")
    print("="*50)