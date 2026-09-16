import tkinter as tk
import threading
import queue

from usgs import fetch_earthquakes
from ui import EarthquakeMonitor


REFRESH_INTERVAL = 60000


def main():

    root = tk.Tk()

    refresh_job = None
    result_queue = queue.Queue()

    def schedule_refresh():

        nonlocal refresh_job

        if refresh_job is not None:

            try:
                root.after_cancel(refresh_job)
            except tk.TclError:
                pass

        refresh_job = root.after(
            REFRESH_INTERVAL,
            fetch_data
        )

    def fetch_data():

        def worker():

            try:

                earthquakes = fetch_earthquakes()

                result_queue.put(
                    ("success", earthquakes)
                )

            except Exception as error:

                result_queue.put(
                    ("error", error)
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def check_queue():

        try:

            while True:

                status, data = result_queue.get_nowait()

                if status == "success":

                    finish_update(data)

                else:

                    print(
                        f"Error fetching earthquake data: {data}"
                    )

                    app.ticker.config(
                        text="Unable to retrieve earthquake data."
                    )

                    app.live_label.config(
                        text="● OFFLINE",
                        fg="red"
                    )

                    app.update_button.config(
                        state="normal"
                    )

        except queue.Empty:

            pass

        root.after(
            100,
            check_queue
        )

    def finish_update(earthquakes):

        app.update_data(
            earthquakes
        )

        schedule_refresh()

    def reset_refresh_timer():

        schedule_refresh()

    app = EarthquakeMonitor(
        root,
        on_update_finished=reset_refresh_timer
    )

    # Start checking the queue from the Tkinter main thread
    root.after(
        100,
        check_queue
    )

    # Initial API request
    root.after(
        200,
        fetch_data
    )

    root.mainloop()


if __name__ == "__main__":
    main()