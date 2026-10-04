from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from image_engine import optimize_root


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Shopify Product Agent — V1")
        self.root.geometry("860x700")
        self.root.minsize(760, 620)

        self.folder = tk.StringVar()
        self.quality = tk.IntVar(value=88)
        self.max_width = tk.IntVar(value=2000)
        self.max_height = tk.IntVar(value=2000)
        self.status = tk.StringVar(value="Ready")

        self.build_ui()

    def build_ui(self):
        root = self.root
        root.configure(bg="#f4f4f4")

        header = tk.Frame(root, bg="#202124", padx=24, pady=18)
        header.grid(row=0, column=0, sticky="ew")
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(4, weight=1)

        tk.Label(header, text="SHOPIFY PRODUCT AGENT", fg="white", bg="#202124",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(header, text="VERSION 1 • Product Image Optimizer", fg="#d7d7d7", bg="#202124",
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        body = tk.Frame(root, bg="#f4f4f4", padx=28, pady=20)
        body.grid(row=1, column=0, sticky="ew")
        body.grid_columnconfigure(1, weight=1)

        tk.Label(body, text="1. Product Folder", bg="#f4f4f4",
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Entry(body, textvariable=self.folder, font=("Segoe UI", 10)).grid(
            row=1, column=0, columnspan=1, sticky="ew", pady=(8, 18), ipady=7)
        tk.Button(body, text="SELECT FOLDER", command=self.choose_folder,
                  bg="#ffffff", fg="#222222", relief="solid", bd=1,
                  font=("Segoe UI", 9, "bold"), padx=18).grid(row=1, column=1, sticky="e", padx=(10, 0), pady=(8, 18))

        settings = tk.LabelFrame(body, text="2. Optimization Settings", bg="#f4f4f4",
                                 font=("Segoe UI", 10, "bold"), padx=15, pady=12)
        settings.grid(row=2, column=0, columnspan=2, sticky="ew")
        for i in range(6):
            settings.grid_columnconfigure(i, weight=1)

        tk.Label(settings, text="WebP Quality", bg="#f4f4f4").grid(row=0, column=0, sticky="w")
        tk.Spinbox(settings, from_=50, to=100, textvariable=self.quality, width=7).grid(row=0, column=1, sticky="w")
        tk.Label(settings, text="Max Width", bg="#f4f4f4").grid(row=0, column=2, sticky="w")
        tk.Spinbox(settings, from_=100, to=10000, textvariable=self.max_width, width=8).grid(row=0, column=3, sticky="w")
        tk.Label(settings, text="Max Height", bg="#f4f4f4").grid(row=0, column=4, sticky="w")
        tk.Spinbox(settings, from_=100, to=10000, textvariable=self.max_height, width=8).grid(row=0, column=5, sticky="w")

        rules = tk.Frame(body, bg="#f4f4f4", pady=16)
        rules.grid(row=3, column=0, columnspan=2, sticky="ew")
        tk.Label(rules, text="3. V1 Rules", bg="#f4f4f4", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(rules, text="✓ Supported formats → WebP\n✓ GIF → unchanged\n✓ Originals untouched\n✓ Creates optimized folder\n✓ Preserves aspect ratio and transparency",
                 bg="#f4f4f4", justify="left", font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))

        action = tk.Frame(root, bg="#f4f4f4", padx=28, pady=8)
        action.grid(row=2, column=0, sticky="ew")
        self.button = tk.Button(action, text="OPTIMIZE IMAGES", command=self.start,
                                bg="#1f6feb", fg="white", activebackground="#1557b0",
                                activeforeground="white", relief="flat", bd=0,
                                font=("Segoe UI", 11, "bold"), padx=30, pady=12,
                                cursor="hand2")
        self.button.pack(fill="x")

        status_frame = tk.Frame(root, bg="#f4f4f4", padx=28, pady=4)
        status_frame.grid(row=3, column=0, sticky="ew")
        tk.Label(status_frame, textvariable=self.status, bg="#f4f4f4",
                 font=("Segoe UI", 9)).pack(anchor="w")
        self.progress = ttk.Progressbar(status_frame, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(5, 0))

        log_frame = tk.Frame(root, bg="#f4f4f4", padx=28, pady=8)
        log_frame.grid(row=4, column=0, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        self.log = tk.Text(log_frame, wrap="word", font=("Consolas", 9), height=12)
        self.log.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scrollbar.set)

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing product folders")
        if folder:
            self.folder.set(folder)
            self.status.set("Folder selected")

    def write_log(self, message):
        self.root.after(0, lambda: (self.log.insert("end", message + "\n"), self.log.see("end")))

    def start(self):
        if not self.folder.get():
            messagebox.showwarning("Select folder", "Please select the folder containing your product folders.")
            return
        root = Path(self.folder.get())
        if not root.is_dir():
            messagebox.showerror("Invalid folder", "The selected folder does not exist.")
            return

        try:
            quality = int(self.quality.get())
            width = int(self.max_width.get())
            height = int(self.max_height.get())
            if not 50 <= quality <= 100 or width <= 0 or height <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid settings", "Please enter valid optimization settings.")
            return

        self.button.config(state="disabled")
        self.progress["value"] = 0
        self.status.set("Optimizing images...")
        self.log.delete("1.0", "end")

        threading.Thread(target=self.worker, args=(root, quality, width, height), daemon=True).start()

    def worker(self, root, quality, width, height):
        try:
            report, rows = optimize_root(root, quality, width, height,
                                         progress=lambda value: self.root.after(0, lambda: self.progress.configure(value=value * 100)),
                                         log=self.write_log)
            ok = sum(1 for row in rows if row[6] == "OK")
            failed = sum(1 for row in rows if row[6] == "FAILED")
            self.root.after(0, lambda: self.finish(report, ok, failed))
        except Exception as exc:
            self.root.after(0, lambda: self.fail(exc))

    def finish(self, report, ok, failed):
        self.button.config(state="normal")
        self.progress["value"] = 100
        self.status.set(f"Complete — {ok} processed, {failed} failed")
        messagebox.showinfo("Optimization complete", f"Finished.\n\nReport:\n{report}")

    def fail(self, exc):
        self.button.config(state="normal")
        self.status.set("Failed")
        messagebox.showerror("Optimization failed", str(exc))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
