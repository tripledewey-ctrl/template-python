"""Einfache Tkinter-Oberflaeche: Ordner waehlen, suchen, Treffer als Liste anzeigen."""

from __future__ import annotations

import os
import subprocess  # nosec B404 - nur zum Oeffnen einer vom Benutzer gewaehlten Datei
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from bildfinder import __version__
from bildfinder.scanner import ImageFile, find_images, format_size

MAX_RESULTS = 5000


def open_file(path: Path) -> None:
    """Oeffnet eine Datei mit dem Standardprogramm des Betriebssystems."""
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]  # noqa: S606  # nosec B606
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)  # noqa: S603, S607  # nosec
    else:
        subprocess.run(["xdg-open", str(path)], check=False)  # noqa: S603, S607  # nosec


class BildfinderApp:
    def __init__(self, root: tk.Tk, folder: Path) -> None:
        self.root = root
        self.images: list[ImageFile] = []
        self._result: list[ImageFile] | Exception | None = None
        root.title(f"Bildfinder {__version__}")
        root.geometry("760x480")
        root.minsize(480, 300)

        top = ttk.Frame(root, padding=8)
        top.pack(fill=tk.X)
        self.folder_var = tk.StringVar(value=str(folder))
        ttk.Entry(top, textvariable=self.folder_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(top, text="Ordner...", command=self.choose_folder).pack(side=tk.LEFT, padx=4)
        self.search_btn = ttk.Button(top, text="Suchen", command=self.start_search)
        self.search_btn.pack(side=tk.LEFT)

        body = ttk.Frame(root, padding=(8, 0, 8, 0))
        body.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(body, activestyle="dotbox")
        scrollbar = ttk.Scrollbar(body, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.bind("<Double-Button-1>", self.open_selected)
        self.listbox.bind("<Return>", self.open_selected)

        self.status_var = tk.StringVar(value="Ordner waehlen und 'Suchen' klicken.")
        ttk.Label(root, textvariable=self.status_var, padding=8).pack(fill=tk.X)

    def choose_folder(self) -> None:
        chosen = filedialog.askdirectory(initialdir=self.folder_var.get())
        if chosen:
            self.folder_var.set(chosen)

    def start_search(self) -> None:
        folder = Path(self.folder_var.get())
        self.search_btn.state(["disabled"])
        self.status_var.set(f"Suche in {folder} ...")
        self.listbox.delete(0, tk.END)
        self._result = None
        threading.Thread(target=self._search, args=(folder,), daemon=True).start()
        self.root.after(100, self._poll)

    def _search(self, folder: Path) -> None:
        try:
            self._result = find_images(folder, limit=MAX_RESULTS)
        except Exception as exc:
            self._result = exc

    def _poll(self) -> None:
        result = self._result
        if result is None:
            self.root.after(100, self._poll)
            return
        self.search_btn.state(["!disabled"])
        if isinstance(result, Exception):
            self.status_var.set("Fehler bei der Suche.")
            messagebox.showerror("Bildfinder", str(result))
            return
        self.images = result
        for image in result:
            self.listbox.insert(
                tk.END, f"{image.name}  ({format_size(image.size)})  -  {image.path}"
            )
        suffix = f" (auf {MAX_RESULTS} begrenzt)" if len(result) >= MAX_RESULTS else ""
        self.status_var.set(f"{len(result)} Bild(er) gefunden{suffix}. Doppelklick oeffnet.")

    def open_selected(self, _event: object = None) -> None:
        selection: tuple[int, ...] = self.listbox.curselection()  # type: ignore[no-untyped-call]
        if selection:
            open_file(self.images[selection[0]].path)


def run_gui(folder: Path) -> int:
    root = tk.Tk()
    BildfinderApp(root, folder)
    root.mainloop()
    return 0
