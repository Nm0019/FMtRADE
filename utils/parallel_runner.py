# utils/parallel_runner.py

from multiprocessing import Pool, cpu_count


def run_in_parallel(task_function, symbols, timeframes, desc="Job", processes=None):
    """
    اجرای موازی روی ترکیب (symbol, timeframe) با استفاده از multiprocessing.

    Args:
        task_function (function): تابعی که باید اجرا شود.
        symbols (list): لیست نمادها.
        timeframes (list): لیست تایم‌فریم‌ها.
        desc (str): متن توصیفی برای پرینت وضعیت.
        processes (int or None): تعداد پردازش‌های هم‌زمان. None یعنی استفاده از تمام هسته‌ها.

    Returns:
        list: لیست نتایج خروجی از تابع اجرا شده.
    """
    tasks = [(symbol, tf) for symbol in symbols for tf in timeframes]
    print(f"🚀 Running {len(tasks)} {desc} tasks using {processes or cpu_count()} cores...")

    with Pool(processes=processes or cpu_count()) as pool:
        results = pool.starmap(task_function, tasks)

    print(f"🏁 All {desc} tasks finished.")
    return results
