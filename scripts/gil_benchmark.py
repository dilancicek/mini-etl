import time
import threading

# 1. CPU-Bound İşlem (İşlemciyi yoran matematiksel hesap - GIL burada başa bela olur)
def cpu_bound_task(n):
    while n > 0:
        n -= 1

# 2. I/O-Bound İşlem (Ağ isteği veya disk beklemesi - GIL burada serbest kalır)
def io_bound_task():
    time.sleep(2) # İnternetten veri çekiyormuşuz gibi simüle ediyoruz

def run_single_thread_cpu():
    start = time.perf_counter()
    cpu_bound_task(100_000_000)
    cpu_bound_task(100_000_000)
    print(f"CPU-Bound Tek Thread Süresi: {time.perf_counter() - start:.2f} saniye")

def run_multi_thread_cpu():
    start = time.perf_counter()
    t1 = threading.Thread(target=cpu_bound_task, args=(100_000_000,))
    t2 = threading.Thread(target=cpu_bound_task, args=(100_000_000,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f"CPU-Bound Çift Thread Süresi: {time.perf_counter() - start:.2f} saniye")

def run_single_thread_io():
    start = time.perf_counter()
    io_bound_task()
    io_bound_task()
    print(f"I/O-Bound Tek Thread Süresi: {time.perf_counter() - start:.2f} saniye")

def run_multi_thread_io():
    start = time.perf_counter()
    t1 = threading.Thread(target=io_bound_task)
    t2 = threading.Thread(target=io_bound_task)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f"I/O-Bound Çift Thread Süresi: {time.perf_counter() - start:.2f} saniye")

if __name__ == "__main__":
    print("--- GIL BENCHMARK TESTİ ---")
    run_single_thread_cpu()
    run_multi_thread_cpu()
    print("-" * 30)
    run_single_thread_io()
    run_multi_thread_io()