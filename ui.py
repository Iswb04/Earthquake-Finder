import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone, timedelta
import json
import os

class EarthquakeMonitor:
    def __init__(self, root, on_manual_update=None):
        self.root = root
        self.on_manual_update = on_manual_update

        # WINDOW
        self.root.title("EARTHQUAKE MONITOR")
        self.root.geometry("1100x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#080808")

        # COLORS
        self.bg = "#080808"
        self.panel = "#111111"
        self.panel_light = "#171717"
        self.border = "#252525"
        self.white = "#f5f5f5"
        self.gray = "#8c8c8c"
        self.gray_light = "#bdbdbd"
        self.green = "#20c96b"
        self.red = "#ff3b3b"
        self.yellow = "#e5c04a"
        self.orange = "#f08a3c"
        self.red_mag = "#ff4545"

        # DATA
        self.earthquakes = []
        self.ticker_after_id = None

        # LOAD COUNTRIES
        base_dir = os.path.dirname(os.path.abspath(__file__))
        countries_path = os.path.join(base_dir, "countries.json")

        try:
            with open(countries_path, "r", encoding="utf-8") as file:
                countries = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            countries = []

        countries.insert(0, "ALL")

        # STYLE
        self.setup_styles()

        # MAIN
        self.main = tk.Frame(root, bg=self.bg)
        self.main.pack(fill="both", expand=True, padx=24, pady=22)

        self.create_header()
        self.create_filter_panel(countries)
        self.create_table()
        self.create_footer()

    # STYLES
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # COMBOBOX
        style.configure(
            "Modern.TCombobox",
            background=self.panel_light,
            foreground=self.white,
            fieldbackground=self.panel_light,
            bordercolor=self.border,
            lightcolor=self.border,
            darkcolor=self.border,
            arrowcolor=self.gray_light,
            relief="flat",
            borderwidth=1,
            padding=7
        )
        style.map(
            "Modern.TCombobox",
            background=[("readonly", self.panel_light), ("active", self.panel_light), ("pressed", self.panel_light), ("focus", self.panel_light)],
            foreground=[("readonly", self.white), ("focus", self.white)],
            fieldbackground=[("readonly", self.panel_light), ("active", self.panel_light), ("pressed", self.panel_light), ("focus", self.panel_light)],
            bordercolor=[("readonly", self.border), ("active", self.border), ("pressed", self.border), ("focus", self.border)],
            lightcolor=[("readonly", self.border), ("active", self.border), ("pressed", self.border), ("focus", self.border)],
            darkcolor=[("readonly", self.border), ("active", self.border), ("pressed", self.border), ("focus", self.border)],
            arrowcolor=[("readonly", self.gray_light), ("active", self.gray_light), ("pressed", self.gray_light), ("focus", self.gray_light)]
        )

        # TREEVIEW
        style.configure(
            "Modern.Treeview",
            background=self.panel,
            foreground=self.gray_light,
            fieldbackground=self.panel,
            borderwidth=0,
            relief="flat",
            rowheight=36,
            font=("Arial", 9)
        )
        style.configure(
            "Modern.Treeview.Heading",
            background=self.panel_light,
            foreground=self.gray_light,
            borderwidth=0,
            relief="flat",
            font=("Arial", 9, "bold"),
            padding=(8, 10)
        )
        style.map(
            "Modern.Treeview",
            background=[("selected", "#202020"), ("focus", self.panel)],
            foreground=[("selected", self.white), ("focus", self.gray_light)]
        )

        # SCROLLBAR
        style.configure(
            "Modern.Vertical.TScrollbar",
            background="#202020",
            troughcolor="#0d0d0d",
            bordercolor="#0d0d0d",
            arrowcolor="#888888",
            relief="flat"
        )

    # HEADER
    def create_header(self):
        header = tk.Frame(self.main, bg=self.bg)
        header.pack(fill="x", pady=(0, 22))

        # TITLE
        title_frame = tk.Frame(header, bg=self.bg)
        title_frame.pack(side="left")

        title = tk.Frame(title_frame, bg=self.bg)
        title.pack(anchor="w")

        tk.Label(title, text="EARTHQUAKE", font=("Arial", 25, "bold"), fg=self.white, bg=self.bg).pack(side="left")
        tk.Label(title, text=" MONITOR", font=("Arial", 25, "bold"), fg=self.gray, bg=self.bg).pack(side="left")
        tk.Label(title_frame, text="Real-time earthquake monitoring", font=("Arial", 9), fg=self.gray, bg=self.bg).pack(anchor="w", pady=(4, 0))

        # STATUS
        status = tk.Frame(header, bg=self.bg)
        status.pack(side="right", anchor="n")

        self.live_label = tk.Label(status, text="● LIVE", font=("Arial", 10, "bold"), fg=self.red, bg=self.bg)
        self.live_label.pack(anchor="e")

        self.last_update_label = tk.Label(status, text="Last update: --:--:--", font=("Arial", 8), fg=self.gray, bg=self.bg)
        self.last_update_label.pack(anchor="e", pady=(5, 0))

    # FILTER PANEL
    def create_filter_panel(self, countries):
        panel = tk.Frame(self.main, bg=self.panel, highlightbackground=self.border, highlightcolor=self.border, highlightthickness=1, bd=0)
        panel.pack(fill="x", pady=(0, 15))

        inner = tk.Frame(panel, bg=self.panel)
        inner.pack(fill="x", padx=16, pady=14)

        # COUNTRY
        country_box = tk.Frame(inner, bg=self.panel)
        country_box.pack(side="left", padx=(0, 18))
        tk.Label(country_box, text="COUNTRY", font=("Arial", 8, "bold"), fg=self.gray, bg=self.panel).pack(anchor="w", pady=(0, 5))

        self.country_var = tk.StringVar(value="ALL")
        self.country_combo = ttk.Combobox(country_box, textvariable=self.country_var, values=countries, state="readonly", width=20, style="Modern.TCombobox")
        self.country_combo.pack()
        self.country_combo.bind("<<ComboboxSelected>>", self.on_filter_changed)

        # PERIOD
        period_box = tk.Frame(inner, bg=self.panel)
        period_box.pack(side="left", padx=(0, 18))
        tk.Label(period_box, text="PERIOD", font=("Arial", 8, "bold"), fg=self.gray, bg=self.panel).pack(anchor="w", pady=(0, 5))

        self.period_var = tk.StringVar(value="1 DAY")
        self.period_combo = ttk.Combobox(period_box, textvariable=self.period_var, values=["1 HOUR", "1 DAY", "7 DAYS", "30 DAYS"], state="readonly", width=12, style="Modern.TCombobox")
        self.period_combo.pack()
        self.period_combo.bind("<<ComboboxSelected>>", self.on_filter_changed)

        # MAGNITUDE
        magnitude_box = tk.Frame(inner, bg=self.panel)
        magnitude_box.pack(side="left")
        tk.Label(magnitude_box, text="MAGNITUDE", font=("Arial", 8, "bold"), fg=self.gray, bg=self.panel).pack(anchor="w", pady=(0, 5))

        self.magnitude_var = tk.StringVar(value="ALL")
        self.magnitude_combo = ttk.Combobox(magnitude_box, textvariable=self.magnitude_var, values=["ALL", "LOW", "MEDIUM", "HIGH", "MAJOR"], state="readonly", width=12, style="Modern.TCombobox")
        self.magnitude_combo.pack()
        self.magnitude_combo.bind("<<ComboboxSelected>>", self.on_filter_changed)

        # UPDATE BUTTON
        self.update_button = tk.Button(
            inner, text="UPDATE", command=self.manual_update, bg=self.green, fg="#050505",
            activebackground="#28e878", activeforeground="#050505", font=("Arial", 9, "bold"),
            relief="flat", bd=0, cursor="hand2", padx=20, pady=9
        )
        self.update_button.pack(side="right", padx=(20, 0))

    # FILTER CHANGE
    def on_filter_changed(self, event=None):
        self.update_table()
        # Remove keyboard focus from the Combobox so the selected text does not look highlighted.
        self.root.focus_set()

    # TABLE
    def create_table(self):
        table_container = tk.Frame(self.main, bg=self.panel, highlightbackground=self.border, highlightcolor=self.border, highlightthickness=1, bd=0)
        table_container.pack(fill="both", expand=True)

        # TABLE HEADER
        table_header = tk.Frame(table_container, bg=self.panel_light, height=42)
        table_header.pack(fill="x")
        table_header.pack_propagate(False)

        tk.Label(table_header, text="EARTHQUAKE EVENTS", font=("Arial", 9, "bold"), fg=self.white, bg=self.panel_light).pack(side="left", padx=14)

        # TABLE FRAME
        table_frame = tk.Frame(table_container, bg=self.panel)
        table_frame.pack(fill="both", expand=True, padx=8, pady=8)

        columns = ("magnitude", "location", "depth", "time")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Modern.Treeview", height=8)

        self.tree.heading("magnitude", text="MAGNITUDE")
        self.tree.heading("location", text="LOCATION")
        self.tree.heading("depth", text="DEPTH (KM)")
        self.tree.heading("time", text="TIME")

        self.tree.column("magnitude", width=90, minwidth=70, anchor="center")
        self.tree.column("location", width=220, minwidth=150)
        self.tree.column("depth", width=75, minwidth=60, anchor="center")
        self.tree.column("time", width=140, minwidth=110, anchor="center")

        # MAGNITUDE COLORS
        self.tree.tag_configure("magnitude_yellow", foreground=self.yellow)
        self.tree.tag_configure("magnitude_orange", foreground=self.orange)
        self.tree.tag_configure("magnitude_red", foreground=self.red_mag)
        self.tree.tag_configure("normal", foreground=self.gray_light)

        # SCROLLBAR
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview, style="Modern.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # FOOTER
    def create_footer(self):
        footer = tk.Frame(self.main, bg=self.bg)
        footer.pack(fill="x", pady=(12, 0))

        self.ticker = tk.Label(footer, text="Waiting for earthquake data...", font=("Arial", 9), fg=self.gray, bg=self.bg, anchor="w")
        self.ticker.pack(side="left", fill="x", expand=True)

        tk.Label(footer, text="SOURCE  USGS", font=("Arial", 8, "bold"), fg="#555555", bg=self.bg).pack(side="right")

    # MANUAL UPDATE
    def manual_update(self):
        # Disable button and update UI state
        self.live_label.config(text="● UPDATING", fg=self.red)
        self.ticker.config(text="Fetching latest earthquake data...", fg=self.gray)
        self.update_button.config(state="disabled")
        
        # Call the callback (from main.py) to do the actual data fetching
        if self.on_manual_update:
            self.on_manual_update()

    # UPDATE DATA
    def update_data(self, earthquakes):
        if not earthquakes:
            self.ticker.config(text="Unable to retrieve earthquake data.", fg=self.gray)
            self.live_label.config(text="● OFFLINE", fg=self.red)
            self.update_button.config(state="normal")
            return

        # CANCEL OLD TICKER
        if self.ticker_after_id is not None:
            self.root.after_cancel(self.ticker_after_id)
            self.ticker_after_id = None

        # LAST UPDATE
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.config(text=f"Last update: {current_time}")

        # STORE DATA
        self.earthquakes = earthquakes

        # UPDATE TABLE USING CURRENT FILTERS
        self.update_table()

        # TICKER & LIVE
        self.ticker.config(text="Updated successfully.", fg=self.gray)
        self.ticker_after_id = self.root.after(3000, self.show_latest_earthquake)
        self.live_label.config(text="● LIVE", fg=self.red)
        self.update_button.config(state="normal")

    # LATEST EARTHQUAKE
    def show_latest_earthquake(self):
        self.ticker_after_id = None
        if not self.earthquakes:
            return

        latest = max(self.earthquakes, key=lambda earthquake: earthquake["timestamp"] or 0)
        magnitude = latest["magnitude"]
        magnitude = "N/A" if magnitude is None else f"{magnitude:.1f}"

        event_time = datetime.fromtimestamp(latest["timestamp"] / 1000)
        formatted_time = event_time.strftime("%Y-%m-%d %H:%M:%S")

        self.ticker.config(
            text=f"Latest earthquake: M{magnitude} - {latest['location']} - {formatted_time}",
            fg=self.gray
        )

    # MAGNITUDE FILTER
    def magnitude_matches_filter(self, magnitude, selected):
        if selected == "ALL": return True
        if magnitude is None: return False
        if selected == "LOW": return magnitude < 4.0
        if selected == "MEDIUM": return 4.0 <= magnitude < 6.0
        if selected == "HIGH": return 6.0 <= magnitude < 7.0
        if selected == "MAJOR": return magnitude >= 7.0
        return True

    # MAGNITUDE TAG
    def get_magnitude_tag(self, magnitude):
        if magnitude is None: return "normal"
        if magnitude >= 7.0: return "magnitude_red"
        if magnitude >= 6.0: return "magnitude_orange"
        if magnitude >= 4.0: return "magnitude_yellow"
        return "normal"

    # UPDATE TABLE
    def update_table(self):
        # CLEAR TABLE
        for item in self.tree.get_children():
            self.tree.delete(item)

        # CURRENT FILTERS
        now = datetime.now(timezone.utc)
        period = self.period_var.get()
        country = self.country_var.get()
        magnitude_filter = self.magnitude_var.get()

        # PERIOD
        if period == "1 HOUR":
            time_limit = now - timedelta(hours=1)
        elif period == "1 DAY":
            time_limit = now - timedelta(days=1)
        elif period == "7 DAYS":
            time_limit = now - timedelta(days=7)
        elif period == "30 DAYS":
            time_limit = now - timedelta(days=30)
        else:
            time_limit = now - timedelta(days=1)

        # FILTER EVENTS
        filtered = []
        for earthquake in self.earthquakes:
            timestamp = earthquake["timestamp"]
            if timestamp is None:
                continue

            # TIME
            event_time = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
            if event_time < time_limit:
                continue

            # COUNTRY
            if country != "ALL":
                location = earthquake["location"]
                if not location or country.lower() not in location.lower():
                    continue

            # MAGNITUDE
            if not self.magnitude_matches_filter(earthquake["magnitude"], magnitude_filter):
                continue

            filtered.append(earthquake)

        # NEWEST FIRST
        filtered.sort(key=lambda earthquake: earthquake["timestamp"] or 0, reverse=True)

        # INSERT ALL FILTERED EVENTS
        for earthquake in filtered:
            timestamp = earthquake["timestamp"]
            event_time = datetime.fromtimestamp(timestamp / 1000)

            # DEPTH & MAGNITUDE
            depth = earthquake["depth"]
            depth_text = f"{depth:.1f}" if depth is not None else "N/A"

            magnitude = earthquake["magnitude"]
            magnitude_text = f"{magnitude:.1f}" if magnitude is not None else "N/A"

            # COLOR TAG
            magnitude_tag = self.get_magnitude_tag(magnitude)

            # INSERT ROW
            self.tree.insert("", "end", values=(
                magnitude_text,
                earthquake["location"],
                depth_text,
                event_time.strftime("%Y-%m-%d %H:%M:%S")
            ), tags=(magnitude_tag,))