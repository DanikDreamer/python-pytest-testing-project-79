import threading
import time


def progress_bar_decorator(func):
    progress_bar_refresh_time = 1.0
    progress_bar_item = '█'

    def wrapper(*args, **kwargs):
        count = 0

        def update_progress_bar(stop_semaphore):
            nonlocal count
            while not stop_semaphore.acquire(blocking=False):
                time.sleep(progress_bar_refresh_time)
                count += 1
                print(f'Downloading: '
                      f'|{progress_bar_item * count}', end='\r', flush=True)
            print()

        stop_semaphore = threading.Semaphore(0)
        progress_thread = threading.Thread(
            target=update_progress_bar, args=(stop_semaphore,))
        progress_thread.start()

        try:
            result = func(*args, **kwargs)
            print(f'Downloading: |{progress_bar_item * count}| 100.0%')

            return result
        except Exception as e:
            raise e
        finally:
            stop_semaphore.release()
            progress_thread.join()

    return wrapper
