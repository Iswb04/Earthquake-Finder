import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone, timedelta
import json
import os
import threading

from usgs import fetch_earthquakes


class EarthquakeMonitor:

    def __init__(
        self,
        root,
        on_update_finished=None
    ):

        self.root = root

        self.on_update_finished = (
            on_update_finished
        )

        self.root.title(
            "EARTHQUAKE MONITOR"
        )

        self.root.geometry(
            "1000x650"
        )

        self.root.minsize(
            900,
            600
        )

        # =====================================================
        # DATA
        # =====================================================

        self.earthquakes = []

        self.known_ids = set()

        self.first_load = True

        self.ticker_after_id = None

        # =====================================================
        # LOAD COUNTRIES
        # =====================================================

        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        countries_path = os.path.join(
            base_dir,
            "countries.json"
        )

        try:

            with open(
                countries_path,
                "r",
                encoding="utf-8"
            ) as file:

                countries = json.load(file)

        except (
            FileNotFoundError,
            json.JSONDecodeError
        ):

            countries = []

        countries.insert(
            0,
            "ALL"
        )

        # =====================================================
        # HEADER
        # =====================================================

        header = tk.Frame(
            root,
            bg="#111111",
            height=90
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(
            False
        )

        title = tk.Label(
            header,
            text="EARTHQUAKE MONITOR",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="#111111"
        )

        title.pack(
            anchor="w",
            padx=25,
            pady=(18, 0)
        )

        subtitle = tk.Label(
            header,
            text="Real-time earthquake monitoring",
            font=("Arial", 10),
            fg="#aaaaaa",
            bg="#111111"
        )

        subtitle.pack(
            anchor="w",
            padx=27
        )

        # =====================================================
        # FILTER BAR
        # =====================================================

        filter_frame = tk.Frame(
            root,
            bg="#f2f2f2",
            height=70
        )

        filter_frame.pack(
            fill="x"
        )

        filter_frame.pack_propagate(
            False
        )

        # =====================================================
        # COUNTRY
        # =====================================================

        tk.Label(
            filter_frame,
            text="Country",
            font=("Arial", 10, "bold"),
            bg="#f2f2f2",
            fg="#222222"
        ).pack(
            side="left",
            padx=(25, 8)
        )

        self.country_var = tk.StringVar(
            value="ALL"
        )

        self.country_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.country_var,
            values=countries,
            state="readonly",
            width=22
        )

        self.country_combo.pack(
            side="left",
            padx=(0, 25)
        )

        self.country_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self.update_table()
        )

        # =====================================================
        # PERIOD
        # =====================================================

        tk.Label(
            filter_frame,
            text="Period",
            font=("Arial", 10, "bold"),
            bg="#f2f2f2",
            fg="#222222"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.period_var = tk.StringVar(
            value="1 DAY"
        )

        self.period_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.period_var,
            values=[
                "1 HOUR",
                "1 DAY",
                "7 DAYS",
                "30 DAYS"
            ],
            state="readonly",
            width=12
        )

        self.period_combo.pack(
            side="left",
            padx=(0, 20)
        )

        self.period_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self.update_table()
        )

        # =====================================================
        # MAGNITUDE
        # =====================================================

        tk.Label(
            filter_frame,
            text="Magnitude",
            font=("Arial", 10, "bold"),
            bg="#f2f2f2",
            fg="#222222"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.magnitude_var = tk.StringVar(
            value="ALL"
        )

        self.magnitude_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.magnitude_var,
            values=[
                "ALL",
                "LOW",
                "MEDIUM",
                "HIGH",
                "MAJOR"
            ],
            state="readonly",
            width=12
        )

        self.magnitude_combo.pack(
            side="left",
            padx=(0, 15)
        )

        self.magnitude_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self.update_table()
        )

        # =====================================================
        # LIVE + LAST UPDATE
        # =====================================================

        status_frame = tk.Frame(
            filter_frame,
            bg="#f2f2f2"
        )

        status_frame.pack(
            side="right",
            padx=25
        )

        self.live_label = tk.Label(
            status_frame,
            text="● LIVE",
            font=("Arial", 10, "bold"),
            fg="red",
            bg="#f2f2f2"
        )

        self.live_label.pack(
            side="left",
            padx=(0, 15)
        )

        self.last_update_label = tk.Label(
            status_frame,
            text="Last update: --:--:--",
            font=("Arial", 10),
            fg="#555555",
            bg="#f2f2f2"
        )

        self.last_update_label.pack(
            side="left"
        )

        # =====================================================
        # TABLE
        # =====================================================

        table_frame = tk.Frame(
            root,
            bg="white"
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(15, 10)
        )

        columns = (
            "magnitude",
            "location",
            "depth",
            "time"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.tree.heading(
            "magnitude",
            text="Magnitude"
        )

        self.tree.heading(
            "location",
            text="Location"
        )

        self.tree.heading(
            "depth",
            text="Depth (km)"
        )

        self.tree.heading(
            "time",
            text="Time"
        )

        self.tree.column(
            "magnitude",
            width=90,
            anchor="center"
        )

        self.tree.column(
            "location",
            width=150
        )

        self.tree.column(
            "depth",
            width=50,
            anchor="center"
        )

        self.tree.column(
            "time",
            width=80,
            anchor="center"
        )

        # =====================================================
        # MAGNITUDE COLORS
        # =====================================================

        self.tree.tag_configure(
            "magnitude_yellow",
            foreground="#d4a500"
        )

        self.tree.tag_configure(
            "magnitude_orange",
            foreground="#e67e22"
        )

        self.tree.tag_configure(
            "magnitude_red",
            foreground="#e00000"
        )

        self.tree.tag_configure(
            "normal",
            foreground="#222222"
        )

        # =====================================================
        # SCROLLBAR
        # =====================================================

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # =====================================================
        # BOTTOM BAR
        # =====================================================

        bottom_frame = tk.Frame(
            root,
            bg="#eeeeee",
            height=42
        )

        bottom_frame.pack(
            fill="x",
            side="bottom"
        )

        bottom_frame.pack_propagate(
            False
        )

        # =====================================================
        # UPDATE BUTTON
        # =====================================================

        self.update_button = tk.Button(
            bottom_frame,
            text="UPDATE",
            command=self.manual_update,
            bg="#28a745",
            fg="white",
            activebackground="#218838",
            activeforeground="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=3
        )

        self.update_button.pack(
            side="left",
            padx=(12, 10),
            pady=7
        )

        # =====================================================
        # TICKER
        # =====================================================

        self.ticker = tk.Label(
            bottom_frame,
            text="Waiting for earthquake data...",
            font=("Arial", 10),
            fg="#555555",
            bg="#eeeeee",
            anchor="w",
            padx=0
        )

        self.ticker.pack(
            side="left",
            fill="both",
            expand=True
        )

    # =========================================================
    # MANUAL UPDATE
    # =========================================================

    def manual_update(self):

        self.period_var.set(
            "1 DAY"
        )

        self.live_label.config(
            text="● UPDATING",
            fg="red"
        )

        self.ticker.config(
            text="Fetching latest earthquake data...",
            fg="#555555"
        )

        self.update_button.config(
            state="disabled"
        )

        def worker():

            earthquakes = fetch_earthquakes()

            self.root.after(
                0,
                lambda: self.finish_manual_update(
                    earthquakes
                )
            )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    # =========================================================
    # FINISH MANUAL UPDATE
    # =========================================================

    def finish_manual_update(
        self,
        earthquakes
    ):

        self.update_data(
            earthquakes
        )

        self.update_button.config(
            state="normal"
        )

        if self.on_update_finished:

            self.on_update_finished()

    # =========================================================
    # UPDATE DATA
    # =========================================================

    def update_data(
        self,
        earthquakes
    ):

        if not earthquakes:

            self.ticker.config(
                text="Unable to retrieve earthquake data.",
                fg="#555555"
            )

            self.live_label.config(
                text="● OFFLINE",
                fg="red"
            )

            self.update_button.config(
                state="normal"
            )

            return

        # =====================================================
        # CANCEL OLD TICKER TIMER
        # =====================================================

        if self.ticker_after_id is not None:

            try:

                self.root.after_cancel(
                    self.ticker_after_id
                )

            except tk.TclError:

                pass

            self.ticker_after_id = None

        # =====================================================
        # LAST UPDATE
        # =====================================================

        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )

        self.last_update_label.config(
            text=f"Last update: {current_time}"
        )

        # =====================================================
        # FIRST LOAD
        # =====================================================

        if self.first_load:

            self.earthquakes = earthquakes

            for earthquake in earthquakes:

                self.known_ids.add(
                    earthquake["id"]
                )

            self.first_load = False

            self.update_table()

            self.show_latest_earthquake()

        # =====================================================
        # NORMAL UPDATE
        # =====================================================

        else:

            new_events = []

            for earthquake in earthquakes:

                earthquake_id = earthquake["id"]

                if earthquake_id not in self.known_ids:

                    new_events.append(
                        earthquake
                    )

                    self.known_ids.add(
                        earthquake_id
                    )

            self.earthquakes = earthquakes

            self.update_table()

            self.ticker.config(
                text="Updated successfully.",
                fg="#555555"
            )

            self.ticker_after_id = self.root.after(
                3000,
                self.show_latest_earthquake
            )

        # =====================================================
        # LIVE STATUS
        # =====================================================

        self.live_label.config(
            text="● LIVE",
            fg="red"
        )

        self.update_button.config(
            state="normal"
        )

    # =========================================================
    # SHOW LATEST EARTHQUAKE
    # =========================================================

    def show_latest_earthquake(self):

        self.ticker_after_id = None

        if not self.earthquakes:
            return

        latest = max(
            self.earthquakes,
            key=lambda earthquake:
            earthquake["timestamp"] or 0
        )

        magnitude = latest["magnitude"]

        if magnitude is None:

            magnitude = "N/A"

        else:

            magnitude = f"{magnitude:.1f}"

        event_time = datetime.fromtimestamp(
            latest["timestamp"] / 1000
        )

        formatted_time = event_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.ticker.config(
            text=(
                f"Latest earthquake: "
                f"M{magnitude} - "
                f"{latest['location']} - "
                f"{formatted_time}"
            ),
            fg="#555555"
        )

    # =========================================================
    # MAGNITUDE FILTER
    # =========================================================

    def magnitude_matches_filter(
        self,
        magnitude,
        selected
    ):

        if selected == "ALL":
            return True

        if magnitude is None:
            return False

        if selected == "LOW":

            return magnitude < 4.0

        if selected == "MEDIUM":

            return 4.0 <= magnitude < 6.0

        if selected == "HIGH":

            return 6.0 <= magnitude < 7.0

        if selected == "MAJOR":

            return magnitude >= 7.0

        return True

    # =========================================================
    # MAGNITUDE COLOR
    # =========================================================

    def get_magnitude_tag(
        self,
        magnitude
    ):

        if magnitude is None:
            return "normal"

        if magnitude >= 7.0:

            return "magnitude_red"

        if magnitude >= 6.0:

            return "magnitude_orange"

        if magnitude >= 4.0:

            return "magnitude_yellow"

        return "normal"

    # =========================================================
    # UPDATE TABLE
    # =========================================================

    def update_table(self):

        for item in self.tree.get_children():

            self.tree.delete(
                item
            )

        now = datetime.now(
            timezone.utc
        )

        period = self.period_var.get()

        country = self.country_var.get()

        magnitude_filter = (
            self.magnitude_var.get()
        )

        # =====================================================
        # PERIOD
        # =====================================================

        if period == "1 HOUR":

            time_limit = (
                now - timedelta(
                    hours=1
                )
            )

        elif period == "1 DAY":

            time_limit = (
                now - timedelta(
                    days=1
                )
            )

        elif period == "7 DAYS":

            time_limit = (
                now - timedelta(
                    days=7
                )
            )

        elif period == "30 DAYS":

            time_limit = (
                now - timedelta(
                    days=30
                )
            )

        else:

            time_limit = (
                now - timedelta(
                    days=1
                )
            )

        # =====================================================
        # FILTER DATA
        # =====================================================

        filtered = []

        for earthquake in self.earthquakes:

            timestamp = earthquake["timestamp"]

            if timestamp is None:
                continue

            event_time = datetime.fromtimestamp(
                timestamp / 1000,
                tz=timezone.utc
            )

            # PERIOD

            if event_time < time_limit:
                continue

            # COUNTRY

            if country != "ALL":

                location = earthquake["location"]

                if not location:
                    continue

                if country.lower() not in location.lower():

                    continue

            # MAGNITUDE

            if not self.magnitude_matches_filter(
                earthquake["magnitude"],
                magnitude_filter
            ):

                continue

            filtered.append(
                earthquake
            )

        # =====================================================
        # SORT NEWEST FIRST
        # =====================================================

        filtered.sort(
            key=lambda earthquake:
            earthquake["timestamp"] or 0,
            reverse=True
        )

        # =====================================================
        # INSERT ROWS
        # =====================================================

        for earthquake in filtered:

            timestamp = earthquake["timestamp"]

            event_time = datetime.fromtimestamp(
                timestamp / 1000
            )

            # DEPTH

            depth = earthquake["depth"]

            if depth is not None:

                depth_text = f"{depth:.1f}"

            else:

                depth_text = "N/A"

            # MAGNITUDE

            magnitude = earthquake["magnitude"]

            if magnitude is not None:

                magnitude_text = f"{magnitude:.1f}"

            else:

                magnitude_text = "N/A"

            # COLOR

            magnitude_tag = self.get_magnitude_tag(
                magnitude
            )

            self.tree.insert(
                "",
                "end",
                values=(
                    magnitude_text,
                    earthquake["location"],
                    depth_text,
                    event_time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ),
                tags=(
                    magnitude_tag,
                )
            )