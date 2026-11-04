import queue
import threading

POLL_MILLISECONDS = 100


def run_in_background(widget, work, on_done, on_error, on_progress=None):
    results = queue.Queue(maxsize=1)
    progress = queue.SimpleQueue()

    def report(*values):
        progress.put(values)

    def worker():
        try:
            value = work(report) if on_progress else work()
            results.put((True, value))
        except Exception as error:
            results.put((False, error))

    def poll():
        if not widget.winfo_exists():
            return
        while on_progress and not progress.empty():
            on_progress(*progress.get())
        try:
            succeeded, value = results.get_nowait()
        except queue.Empty:
            widget.after(POLL_MILLISECONDS, poll)
            return
        (on_done if succeeded else on_error)(value)

    threading.Thread(target=worker, daemon=True).start()
    widget.after(POLL_MILLISECONDS, poll)
