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
            root.after_cancel(refresh_job)
        
        
        refresh_job = root.after(REFRESH_INTERVAL, fetch_data) # Inicia uma nova contagem de 1 minuto

    def fetch_data():
        def worker():
            try:
                earthquakes = fetch_earthquakes()
                result_queue.put(("success", earthquakes))
            except Exception as error:
                result_queue.put(("error", error))

        threading.Thread(target=worker, daemon=True).start()

    def check_queue():
        try:
            while True:
                status, data = result_queue.get_nowait()
                
                if status == "success":
                    finish_update(data)
                else:
                    print(f"Error fetching earthquake data: {data}")
                    app.ticker.config(text="Unable to retrieve earthquake data.")
                    app.live_label.config(text="● OFFLINE", fg="red")
                    app.update_button.config(state="normal")
        
        except queue.Empty:
            pass
            
        root.after(100, check_queue)

    def finish_update(earthquakes):
        app.update_data(earthquakes)
        schedule_refresh()

    def manual_update_trigger():
        
        nonlocal refresh_job # Cancelar o timer quando clica 
        if refresh_job is not None:
            root.after_cancel(refresh_job)
            refresh_job = None
            
        
        fetch_data() # Faz a busca (quando terminar, finish_update vai chamar schedule_refresh recomeçando a contagem)

    
    app = EarthquakeMonitor( # Agora passa o manual_update_trigger para o botão
        root,
        on_manual_update=manual_update_trigger
    )

    root.after(100, check_queue) # Verifica a fila de eventos na thread principal

    root.after(200, fetch_data) # Primeira chamada pra API

    root.mainloop()

if __name__ == "__main__":
    main()