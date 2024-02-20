from pathlib import Path
from tkinter import ttk
import datetime
import queue
import tkinter as tk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

class MyEventHandler(FileSystemEventHandler):
    def __init__(self, q):
        self._q = q
        super().__init__()

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent):
            self._q.put((
                Path(event.src_path).name,
                "Modificado",
                datetime.datetime.now().strftime("%H:%M:%S")
            ))

def process_events(observer, q, modtree):
    if not observer.is_alive():
        return
    try:
        new_item = q.get_nowait()
    except queue.Empty:
        pass
    else:
        modtree.insert("", 0, text=new_item[0], values=new_item[1:])
    root.after(500, process_events, observer, q, modtree)

root = tk.Tk()
root.config(width=600, height=500)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.title("Registro de modificaciones en tiempo real")
modtree = ttk.Treeview(columns=("action", "time",))
modtree.heading("#0", text="Archivo")
modtree.heading("action", text="Acción")
modtree.heading("time", text="Hora")
modtree.grid(column=0, row=0, sticky="nsew")

# Ruta del archivo a monitorear
file_to_monitor = r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\analisis_matriz.csv"

observer = Observer()
q = queue.Queue()
observer.schedule(MyEventHandler(q), Path(file_to_monitor).parent, recursive=False)
observer.start()
root.after(1, process_events, observer, q, modtree)
root.mainloop()
observer.stop()
observer.join()
