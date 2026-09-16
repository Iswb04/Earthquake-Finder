import tkinter as tk
import threading

from usgs import buscar_terremotos
from ui import EarthquakeMonitor


def atualizar_api(app):

    def executar():

        terremotos = buscar_terremotos()

        # Tkinter não deve ser atualizado diretamente
        # pela thread.
        app.root.after(
            0,
            lambda: app.atualizar_dados(terremotos)
        )

    threading.Thread(
        target=executar,
        daemon=True
    ).start()

    # Próxima atualização em 60 segundos
    app.root.after(
        60000,
        lambda: atualizar_api(app)
    )


def main():

    root = tk.Tk()

    app = EarthquakeMonitor(root)

    # Primeira busca imediatamente
    atualizar_api(app)

    root.mainloop()


if __name__ == "__main__":
    main()