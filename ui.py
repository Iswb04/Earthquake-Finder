import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone, timedelta


class EarthquakeMonitor:

    def __init__(self, root):

        self.root = root

        self.root.title("Earthquake Monitor")
        self.root.geometry("1000x650")
        self.root.minsize(850, 550)

        # Data
        self.earthquakes = []
        self.known_ids = set()

        # Filters
        self.selected_country = "All"
        self.period_minutes = 1440

        # Countries
        self.countries = [
            "All",
            "Argentina",
            "Australia",
            "Brazil",
            "Canada",
            "Chile",
            "China",
            "Colombia",
            "Costa Rica",
            "Ecuador",
            "France",
            "Greece",
            "Iceland",
            "India",
            "Indonesia",
            "Italy",
            "Japan",
            "Mexico",
            "New Zealand",
            "Peru",
            "Philippines",
            "Portugal",
            "Russia",
            "Spain",
            "Taiwan",
            "Turkey",
            "United Kingdom",
            "United States"
        ]

        self.create_interface()

    # =========================================================
    # INTERFACE
    # =========================================================

    def create_interface(self):

        # -----------------------------------------------------
        # TITLE
        # -----------------------------------------------------

        title = tk.Label(
            self.root,
            text="🌎 EARTHQUAKE MONITOR",
            font=("Arial", 24, "bold")
        )

        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            self.root,
            text="Real-time earthquake monitoring",
            font=("Arial", 11)
        )

        subtitle.pack(pady=(0, 20))

        # -----------------------------------------------------
        # FILTER AREA
        # -----------------------------------------------------

        filters_frame = tk.Frame(self.root)

        filters_frame.pack(
            fill="x",
            padx=30
        )

        # COUNTRY LABEL

        country_label = tk.Label(
            filters_frame,
            text="Country:",
            font=("Arial", 11, "bold")
        )

        country_label.pack(
            side="left"
        )

        # COUNTRY COMBOBOX

        self.country_combo = ttk.Combobox(
            filters_frame,
            width=22
        )

        self.country_combo["values"] = self.countries

        self.country_combo.set("All")

        self.country_combo.pack(
            side="left",
            padx=(8, 25)
        )

        # Detect typing
        self.country_combo.bind(
            "<KeyRelease>",
            self.filter_countries
        )

        # Detect selection
        self.country_combo.bind(
            "<<ComboboxSelected>>",
            self.country_selected
        )

        # -----------------------------------------------------
        # PERIOD
        # -----------------------------------------------------

        period_label = tk.Label(
            filters_frame,
            text="Period:",
            font=("Arial", 11, "bold")
        )

        period_label.pack(
            side="left"
        )

        # 1 HOUR

        self.hour_button = tk.Button(
            filters_frame,
            text="1 HOUR",
            width=9,
            command=lambda: self.change_period(60)
        )

        self.hour_button.pack(
            side="left",
            padx=5
        )

        # 1 DAY

        self.day_button = tk.Button(
            filters_frame,
            text="1 DAY",
            width=9,
            command=lambda: self.change_period(1440)
        )

        self.day_button.pack(
            side="left",
            padx=5
        )

        # -----------------------------------------------------
        # UPDATE BUTTON
        # -----------------------------------------------------

        self.update_button = tk.Button(
            filters_frame,
            text="UPDATE",
            width=10,
            bg="green",
            fg="white",
            activebackground="darkgreen",
            activeforeground="white",
            font=("Arial", 9, "bold"),
            command=self.manual_update
        )

        self.update_button.pack(
            side="left",
            padx=(15, 0)
        )

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        status_frame = tk.Frame(self.root)

        status_frame.pack(
            fill="x",
            padx=30,
            pady=(20, 10)
        )

        # LIVE

        self.live_label = tk.Label(
            status_frame,
            text="● LIVE",
            fg="red",
            font=("Arial", 10, "bold")
        )

        self.live_label.pack(
            side="left"
        )

        # LAST UPDATE

        self.update_label = tk.Label(
            status_frame,
            text="Last update: --",
            font=("Arial", 10)
        )

        self.update_label.pack(
            side="right"
        )

        # -----------------------------------------------------
        # TABLE
        # -----------------------------------------------------

        table_frame = tk.Frame(self.root)

        table_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        columns = (
            "magnitude",
            "location",
            "depth",
            "time"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        # HEADERS

        self.table.heading(
            "magnitude",
            text="Magnitude"
        )

        self.table.heading(
            "location",
            text="Location"
        )

        self.table.heading(
            "depth",
            text="Depth"
        )

        self.table.heading(
            "time",
            text="Time"
        )

        # COLUMNS

        self.table.column(
            "magnitude",
            width=100,
            anchor="center"
        )

        self.table.column(
            "location",
            width=500
        )

        self.table.column(
            "depth",
            width=120,
            anchor="center"
        )

        self.table.column(
            "time",
            width=120,
            anchor="center"
        )

        # SCROLLBAR

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        self.table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # -----------------------------------------------------
        # TICKER
        # -----------------------------------------------------

        ticker_frame = tk.Frame(
            self.root,
            relief="sunken",
            borderwidth=1
        )

        ticker_frame.pack(
            fill="x",
            padx=30,
            pady=(5, 20)
        )

        self.ticker = tk.Label(
            ticker_frame,
            text="LIVE • Waiting for data...",
            font=("Arial", 11, "bold"),
            anchor="w"
        )

        self.ticker.pack(
            fill="x",
            padx=10,
            pady=8
        )

    # =========================================================
    # COUNTRY AUTOCOMPLETE
    # =========================================================

    def filter_countries(self, event=None):

        typed = self.country_combo.get().lower()

        # Ignore navigation keys
        if event and event.keysym in [
            "Up",
            "Down",
            "Left",
            "Right",
            "Return",
            "Escape"
        ]:
            return

        if typed == "":
            filtered = self.countries

        else:

            filtered = [
                country
                for country in self.countries
                if country.lower().startswith(typed)
            ]

        self.country_combo["values"] = filtered

        # Open dropdown automatically
        if filtered:

            self.country_combo.event_generate(
                "<Down>"
            )

    # =========================================================
    # COUNTRY SELECTED
    # =========================================================

    def country_selected(self, event=None):

        self.selected_country = self.country_combo.get()

        self.update_table()

    # =========================================================
    # CHANGE PERIOD
    # =========================================================

    def change_period(self, minutes):

        self.period_minutes = minutes

        # Highlight selected button

        if minutes == 60:

            self.hour_button.config(
                relief="sunken"
            )

            self.day_button.config(
                relief="raised"
            )

        else:

            self.hour_button.config(
                relief="raised"
            )

            self.day_button.config(
                relief="sunken"
            )

        self.update_table()

    # =========================================================
    # UPDATE TABLE
    # =========================================================

    def update_table(self):

        # Clear table

        for item in self.table.get_children():

            self.table.delete(item)

        now = datetime.now(timezone.utc)

        limit = now - timedelta(
            minutes=self.period_minutes
        )

        for earthquake in self.earthquakes:

            event_time = datetime.fromtimestamp(
                earthquake["timestamp"] / 1000,
                timezone.utc
            )

            # TIME FILTER

            if event_time < limit:

                continue

            # COUNTRY FILTER

            if self.selected_country != "All":

                location = earthquake["location"]

                if location is None:

                    continue

                if self.selected_country.lower() not in location.lower():

                    continue

            # FORMAT TIME

            local_time = event_time.astimezone()

            formatted_time = local_time.strftime(
                "%H:%M:%S"
            )

            # MAGNITUDE

            magnitude = earthquake["magnitude"]

            if magnitude is None:

                magnitude_text = "-"

            else:

                magnitude_text = f"M {magnitude:.1f}"

            # DEPTH

            depth = earthquake["depth"]

            if depth is None:

                depth_text = "-"

            else:

                depth_text = f"{depth:.1f} km"

            # INSERT

            self.table.insert(
                "",
                "end",
                values=(
                    magnitude_text,
                    earthquake["location"],
                    depth_text,
                    formatted_time
                )
            )

    # =========================================================
    # RECEIVE API DATA
    # =========================================================

    def update_data(self, earthquakes):

        if not earthquakes:

            self.live_label.config(
                text="● OFFLINE",
                fg="gray"
            )

            self.ticker.config(
                text="Unable to retrieve earthquake data."
            )

            return

        # Detect new earthquakes

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

        # Replace current data

        self.earthquakes = earthquakes

        # Update table

        self.update_table()

        # Update status

        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )

        self.update_label.config(
            text=f"Last update: {current_time}"
        )

        self.live_label.config(
            text="● LIVE",
            fg="red"
        )

        # -----------------------------------------------------
        # TICKER
        # -----------------------------------------------------

        if new_events:

            first = new_events[0]

            magnitude = first["magnitude"]

            if magnitude is not None:

                message = (
                    f"🔴 NEW EARTHQUAKE • "
                    f"{first['location']} • "
                    f"M {magnitude:.1f}"
                )

            else:

                message = (
                    f"🔴 NEW EARTHQUAKE • "
                    f"{first['location']}"
                )

            if len(new_events) > 1:

                message = (
                    f"🔴 {len(new_events)} NEW EVENTS DETECTED • "
                    f"{first['location']}"
                )

            self.ticker.config(
                text=message
            )

        else:

            self.ticker.config(
                text="🟢 LIVE • No new earthquakes detected"
            )