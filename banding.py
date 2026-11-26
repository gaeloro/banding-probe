"""L020: bandingkan sekuensial vs thread vs asyncio (I/O-bound)
dan sekuensial vs multiprocessing (CPU-bound). Hasil harus identik."""
import asyncio
import math
import threading
import time
from concurrent.futures import ProcessPoolExecutor

# ---------- (a) I/O-bound: simulasi unduh dengan sleep ----------
N_IO, JEDA = 10, 0.2


def io_sekuensial() -> int:
    selesai = 0
    for _ in range(N_IO):
        time.sleep(JEDA)
        selesai += 1
    return selesai


def io_thread() -> int:
    hasil: list[int] = []

    def kerja() -> None:
        time.sleep(JEDA)
        hasil.append(1)

    threads = [threading.Thread(target=kerja) for _ in range(N_IO)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return len(hasil)


async def _satu_async() -> int:
    await asyncio.sleep(JEDA)
    return 1


def io_async() -> int:
    async def semua() -> int:
        return sum(await asyncio.gather(*(_satu_async() for _ in range(N_IO))))

    return asyncio.run(semua())


# ---------- (b) CPU-bound: hitung prima hingga 100.000 ----------
BATAS = 100_000


def _prima(n: int) -> bool:
    # Sengaja memeriksa SEMUA calon pembagi 2..akar(n) tanpa berhenti awal
    # (tetap benar secara matematis) agar beban CPU cukup besar untuk diukur.
    if n < 2:
        return False
    pembagi = 0
    for p in range(2, math.isqrt(n) + 1):
        if n % p == 0:
            pembagi += 1
    return pembagi == 0


def hitung_rentang(lo_hi: tuple[int, int]) -> int:
    lo, hi = lo_hi
    return sum(1 for n in range(lo, hi) if _prima(n))


def prima_sekuensial() -> int:
    return hitung_rentang((2, BATAS))


def prima_paralel() -> int:
    k = 4
    langkah = (BATAS - 2) // k
    potongan = [(2 + i * langkah, BATAS if i == k - 1 else 2 + (i + 1) * langkah) for i in range(k)]
    with ProcessPoolExecutor(max_workers=k) as ex:
        return sum(ex.map(hitung_rentang, potongan))


def ukur(fn, ulang: int = 2):
    terbaik, hasil = float("inf"), None
    for _ in range(ulang):
        t0 = time.perf_counter()
        hasil = fn()
        terbaik = min(terbaik, time.perf_counter() - t0)
    return hasil, terbaik


def main() -> None:
    print("== I/O-bound: 10 tugas x sleep 0,2s ==")
    r_seq, t_seq = ukur(io_sekuensial, 1)
    r_thr, t_thr = ukur(io_thread, 1)
    r_asy, t_asy = ukur(io_async, 1)
    print(f"sekuensial {t_seq:6.2f}s | thread {t_thr:6.2f}s ({t_seq/t_thr:.1f}x) | asyncio {t_asy:6.2f}s ({t_seq/t_asy:.1f}x)")
    assert r_seq == r_thr == r_asy == N_IO
    assert t_seq / t_thr >= 3, "thread harus >= 3x lebih cepat"
    assert t_seq / t_asy >= 3, "asyncio harus >= 3x lebih cepat"

    print("== CPU-bound: prima hingga 100.000 ==")
    p_seq, tp_seq = ukur(prima_sekuensial)
    p_par, tp_par = ukur(prima_paralel)
    print(f"sekuensial {tp_seq:6.2f}s | multiprocessing {tp_par:6.2f}s ({tp_seq/tp_par:.1f}x) | prima = {p_seq}")
    assert p_seq == p_par == 9592
    assert tp_seq / tp_par >= 1.5, "multiprocessing harus >= 1,5x lebih cepat"
    print("LULUS: hasil identik; I/O >= 3x, CPU >= 1,5x lebih cepat.")


if __name__ == "__main__":
    main()
