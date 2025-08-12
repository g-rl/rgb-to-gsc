import tkinter as tk
from tkinter import ttk
import math
import sys

def clamp_01(v):
    return max(0.0, min(1.0, v))

def format_gsc_value(value):
    s = f"{value:.3f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s

class conversion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("rgb ⇄ gsc color converter")
        self.resizable(False, False)
        self.style = ttk.Style(self)
        pad = 8
        container = ttk.Frame(self, padding=pad)
        container.grid(row=0, column=0, sticky="nsew")
        mode_frame = ttk.Frame(container)
        mode_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0,6))
        ttk.Label(mode_frame, text="input mode:").pack(side="left")
        self.mode = tk.StringVar(value="0-255")
        rb1 = ttk.Radiobutton(mode_frame, text="0-255", variable=self.mode, value="0-255", command=self.on_mode_change)
        rb2 = ttk.Radiobutton(mode_frame, text="0.0-1.0", variable=self.mode, value="0.0-1.0", command=self.on_mode_change)
        rb1.pack(side="left", padx=(6,4))
        rb2.pack(side="left")
        self.vars = {"r": tk.DoubleVar(value=178.0), "g": tk.DoubleVar(value=141.0), "b": tk.DoubleVar(value=216.0)}
        self.scales = {}
        for i, ch in enumerate(("r","g","b")):
            frame = ttk.Frame(container, relief="flat")
            frame.grid(row=1+i, column=0, sticky="ew", pady=4)
            ttk.Label(frame, text=ch, width=2).pack(side="left")
            scale = tk.Scale(frame, from_=0, to=255, orient="horizontal", variable=self.vars[ch],
                             length=320, showvalue=False, command=lambda val, c=ch: self.on_slide(c))
            scale.pack(side="left", padx=(6,8))
            value_label = ttk.Label(frame, textvariable=tk.StringVar(value=str(int(self.vars[ch].get()))), width=6)
            value_label.pack(side="left")
            self.scales[ch] = (scale, value_label)
        preview_frame = ttk.Frame(container)
        preview_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(6,0))
        self.preview = tk.Canvas(preview_frame, width=360, height=80, bd=1, relief="sunken")
        self.preview.pack(side="left")
        self.preview.bind("<Button-1>", self.copy_gsc_from_preview)
        info_frame = ttk.Frame(preview_frame, padding=(8,0,0,0))
        info_frame.pack(side="left", fill="y", expand=False)
        ttk.Label(info_frame, text="hex:").grid(row=0, column=0, sticky="w")
        self.hex_var = tk.StringVar(value="#b28dd8")
        ttk.Entry(info_frame, textvariable=self.hex_var, width=12).grid(row=0, column=1, sticky="w", padx=(6,0))
        ttk.Button(info_frame, text="copy", command=lambda: self.copy_to_clipboard(self.hex_var.get())).grid(row=0, column=2, padx=6)
        ttk.Label(info_frame, text="rgb (0-255):").grid(row=1, column=0, sticky="w", pady=(6,0))
        self.rgb_var = tk.StringVar(value="178, 141, 216")
        ttk.Entry(info_frame, textvariable=self.rgb_var, width=14).grid(row=1, column=1, sticky="w", padx=(6,0), pady=(6,0))
        ttk.Button(info_frame, text="copy", command=lambda: self.copy_to_clipboard(self.rgb_var.get())).grid(row=1, column=2, padx=6, pady=(6,0))
        ttk.Label(info_frame, text="gsc (0-1):").grid(row=2, column=0, sticky="w", pady=(6,0))
        self.gsc_var = tk.StringVar(value="(0.698, 0.553, 0.847)")
        ttk.Entry(info_frame, textvariable=self.gsc_var, width=18).grid(row=2, column=1, sticky="w", padx=(6,0), pady=(6,0))
        ttk.Button(info_frame, text="copy", command=lambda: self.copy_to_clipboard(self.gsc_var.get())).grid(row=2, column=2, padx=6, pady=(6,0))
        tip = "tip: switch to '0.0-1.0' to use gsc-style sliders directly."
        ttk.Label(container, text=tip, foreground="gray").grid(row=5, column=0, pady=(8,0), sticky="w")
        self.on_mode_change()
        self.update_preview()

    def on_mode_change(self):
        mode = self.mode.get()
        for ch, (scale, label) in self.scales.items():
            if mode == "0-255":
                scale.config(from_=0, to=255, resolution=1)
                v = self.vars[ch].get()
                if v <= 1.001:
                    self.vars[ch].set(round(v * 255))
            else:
                scale.config(from_=0.0, to=1.0, resolution=0.001)
                v = self.vars[ch].get()
                if v > 1.001:
                    self.vars[ch].set(round((v / 255.0), 3))
            label.config(text=self.format_value_display(ch))
        self.update_preview()

    def format_value_display(self, ch):
        mode = self.mode.get()
        v = self.vars[ch].get()
        if mode == "0-255":
            return f"{int(round(v))}"
        else:
            return f"{v:.3f}"

    def on_slide(self, ch):
        scale, label = self.scales[ch]
        label.config(text=self.format_value_display(ch))
        self.update_preview()

    def update_preview(self):
        mode = self.mode.get()
        if mode == "0-255":
            r = int(round(self.vars["r"].get()))
            g = int(round(self.vars["g"].get()))
            b = int(round(self.vars["b"].get()))
            gsc_r = clamp_01(r / 255.0)
            gsc_g = clamp_01(g / 255.0)
            gsc_b = clamp_01(b / 255.0)
        else:
            gsc_r = clamp_01(self.vars["r"].get())
            gsc_g = clamp_01(self.vars["g"].get())
            gsc_b = clamp_01(self.vars["b"].get())
            r = int(round(gsc_r * 255))
            g = int(round(gsc_g * 255))
            b = int(round(gsc_b * 255))
        hexcol = f"#{r:02x}{g:02x}{b:02x}"
        self.preview.delete("all")
        self.preview.create_rectangle(0, 0, 360, 80, fill=hexcol, outline="")
        text_color = "#000000" if (r*0.299 + g*0.587 + b*0.114) > 186 else "#ffffff"
        self.preview.create_text(180, 40, text=f"{hexcol}  —  rgb {r},{g},{b}", fill=text_color, font=("segoe ui", 10, "bold"))
        gsc_string = f"({format_gsc_value(gsc_r)}, {format_gsc_value(gsc_g)}, {format_gsc_value(gsc_b)})"
        self.hex_var.set(hexcol)
        self.rgb_var.set(f"{r}, {g}, {b}")
        self.gsc_var.set(gsc_string)

    def copy_gsc_from_preview(self, event):
        self.copy_to_clipboard(self.gsc_var.get())

    def copy_to_clipboard(self, text):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            old = self.title()
            self.title(f"copied: {text}")
            self.after(900, lambda: self.title(old))
        except Exception as e:
            print("copy failed:", e, file=sys.stderr)

if __name__ == "__main__":
    app = conversion()
    app.mainloop()
