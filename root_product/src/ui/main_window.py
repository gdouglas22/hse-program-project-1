from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import math

from core.errors import InputError
from core.parse import parse_degree, parse_number, parse_precision
from core.roots import all_roots, format_polar, format_root, principal_root
from i18n.manager import I18nManager


class MainWindow:
    def __init__(self, root: tk.Tk, i18n: I18nManager) -> None:
        self.root = root
        self.i18n = i18n

        self.number_var = tk.StringVar()
        self.degree_var = tk.StringVar(value="2")
        self.precision_var = tk.StringVar(value="6")
        self.mode_var = tk.StringVar()
        self.language_var = tk.StringVar()
        self.mode_key = "complex"
        self._language_by_name: dict[str, str] = {}
        self._mode_by_label: dict[str, str] = {}

        self._setup_style()
        self._build_ui()
        self._apply_language()
        self._set_status(self.i18n.t("status_ready"))

        self._fade_in()

    def _setup_style(self) -> None:
        self.colors = {
            "bg_top": "#f4efe9",
            "bg_bottom": "#e7edf6",
            "card": "#f9fafb",
            "card_border": "#dfe5eb",
            "text": "#1f2937",
            "muted": "#5b6573",
            "accent": "#2f6f61",
            "accent_hover": "#3a8171",
            "input_bg": "#ffffff",
            "input_border": "#c9d2dd",
        }
        self.root.configure(bg=self.colors["bg_bottom"])
        font_family = self._pick_font(
            [
                "Segoe UI Variable",
                "Segoe UI",
                "SF Pro Text",
                "Helvetica Neue",
                "Ubuntu",
                "Noto Sans",
            ]
        )
        mono_family = self._pick_font(
            ["Cascadia Mono", "Consolas", "Menlo", "DejaVu Sans Mono", "Courier New"]
        )
        self.base_font = tkfont.Font(family=font_family, size=11)
        self.title_font = tkfont.Font(family=font_family, size=16, weight="bold")
        self.mono_font = tkfont.Font(family=mono_family, size=10)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Card.TFrame", background=self.colors["card"])
        style.configure(
            "Card.TLabel",
            background=self.colors["card"],
            foreground=self.colors["text"],
            font=self.base_font,
        )
        style.configure(
            "Muted.TLabel",
            background=self.colors["card"],
            foreground=self.colors["muted"],
            font=self.base_font,
        )
        style.configure(
            "TEntry",
            fieldbackground=self.colors["input_bg"],
            foreground=self.colors["text"],
            padding=6,
            borderwidth=1,
        )
        style.configure(
            "TCombobox",
            fieldbackground=self.colors["input_bg"],
            foreground=self.colors["text"],
            padding=6,
        )
        style.configure(
            "TSpinbox",
            fieldbackground=self.colors["input_bg"],
            foreground=self.colors["text"],
            padding=6,
        )
        style.configure(
            "TButton",
            foreground=self.colors["text"],
            padding=(14, 6),
            borderwidth=0,
        )
        style.map(
            "TButton",
            background=[
                ("active", "#eef2f7"),
                ("!active", self.colors["card"]),
            ],
        )
        style.configure(
            "Accent.TButton",
            foreground="#ffffff",
            padding=(14, 6),
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[
                ("active", self.colors["accent_hover"]),
                ("!active", self.colors["accent"]),
            ],
        )

    def _pick_font(self, candidates: list[str]) -> str:
        available = set(tkfont.families(self.root))
        for name in candidates:
            if name in available:
                return name
        return "TkDefaultFont"

    def _build_ui(self) -> None:
        self.root.title(self.i18n.t("app_title"))
        self.root.geometry("840x560")
        self.root.minsize(720, 500)
        self.root.bind("<Return>", lambda _event: self._on_compute())
        self.degree_var.trace_add("write", self._on_degree_change)

        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0, bd=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.root.bind("<Configure>", self._on_resize)

        self.card = tk.Frame(
            self.root,
            bg=self.colors["card"],
            highlightbackground=self.colors["card_border"],
            highlightthickness=1,
        )
        self.card.place(relx=0.5, rely=0.5, relwidth=0.92, relheight=0.9, anchor="center")
        self.card.columnconfigure(0, weight=1)
        self.card.rowconfigure(0, weight=1)

        main = ttk.Frame(self.card, style="Card.TFrame", padding=(20, 18))
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(1, weight=1)
        main.rowconfigure(8, weight=1)

        header = tk.Frame(main, bg=self.colors["accent"])
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)
        self.label_title = tk.Label(
            header,
            bg=self.colors["accent"],
            fg="#ffffff",
            font=self.title_font,
            padx=12,
            pady=10,
            anchor="w",
        )
        self.label_title.grid(row=0, column=0, sticky="ew")

        self.label_number = ttk.Label(main, style="Card.TLabel")
        self.entry_number = ttk.Entry(main, textvariable=self.number_var, width=32)

        self.label_degree = ttk.Label(main, style="Card.TLabel")
        self.spin_degree = ttk.Spinbox(
            main, from_=2, to=50, textvariable=self.degree_var, width=6
        )

        self.label_precision = ttk.Label(main, style="Card.TLabel")
        self.spin_precision = ttk.Spinbox(
            main, from_=0, to=50, textvariable=self.precision_var, width=6
        )

        self.label_mode = ttk.Label(main, style="Card.TLabel")
        self.combo_mode = ttk.Combobox(main, textvariable=self.mode_var, state="readonly")
        self.combo_mode.bind("<<ComboboxSelected>>", self._on_mode_selected)

        self.label_language = ttk.Label(main, style="Card.TLabel")
        self.combo_language = ttk.Combobox(
            main, textvariable=self.language_var, state="readonly"
        )
        self.combo_language.bind("<<ComboboxSelected>>", self._on_language_selected)
        self.combo_language.bind("<Button-1>", self._refresh_languages)

        self.button_compute = ttk.Button(
            main, command=self._on_compute, style="Accent.TButton"
        )
        self.button_clear = ttk.Button(main, command=self._on_clear)
        self.button_copy = ttk.Button(main, command=self._on_copy)

        result_row = ttk.Frame(main, style="Card.TFrame")
        result_row.columnconfigure(0, weight=1)
        self.label_result = ttk.Label(result_row, style="Card.TLabel")
        self.button_calculate = ttk.Button(
            result_row, command=self._on_compute, style="Accent.TButton"
        )

        self.text_output = tk.Text(
            main,
            height=16,
            wrap="word",
            bg="#fdfdfd",
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.colors["input_border"],
            highlightcolor=self.colors["accent"],
        )
        self.text_output.configure(
            state="disabled",
            font=self.mono_font,
            spacing1=2,
            spacing3=2,
        )

        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            main, textvariable=self.status_var, anchor="w", style="Muted.TLabel"
        )

        self.label_number.grid(row=1, column=0, sticky="w", padx=(0, 6), pady=4)
        self.entry_number.grid(row=1, column=1, sticky="ew", pady=4)

        self.label_degree.grid(row=2, column=0, sticky="w", padx=(0, 6), pady=4)
        self.spin_degree.grid(row=2, column=1, sticky="w", pady=4)

        self.label_precision.grid(row=3, column=0, sticky="w", padx=(0, 6), pady=4)
        self.spin_precision.grid(row=3, column=1, sticky="w", pady=4)

        self.label_mode.grid(row=4, column=0, sticky="w", padx=(0, 6), pady=4)
        self.combo_mode.grid(row=4, column=1, sticky="w", pady=4)

        self.label_language.grid(row=5, column=0, sticky="w", padx=(0, 6), pady=4)
        self.combo_language.grid(row=5, column=1, sticky="w", pady=4)

        button_row = ttk.Frame(main, style="Card.TFrame")
        button_row.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 6))
        self.button_compute.grid(in_=button_row, row=0, column=0, padx=(0, 8))
        self.button_clear.grid(in_=button_row, row=0, column=1, padx=(0, 8))
        self.button_copy.grid(in_=button_row, row=0, column=2, padx=(0, 8))

        result_row.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(8, 4))
        self.label_result.grid(row=0, column=0, sticky="w")
        self.button_calculate.grid(row=0, column=1, sticky="e", padx=(8, 0))

        self.text_output.grid(row=8, column=0, columnspan=2, sticky="nsew", pady=(0, 6))
        self.status_bar.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        self.root.update_idletasks()
        self._draw_background(self.root.winfo_width(), self.root.winfo_height())

    def _apply_language(self) -> None:
        self.root.title(self.i18n.t("app_title"))
        self.label_title.config(text=self.i18n.t("app_title"))
        self.label_number.config(text=self.i18n.t("label_number"))
        self.label_degree.config(text=self.i18n.t("label_degree"))
        self.label_precision.config(text=self.i18n.t("label_precision"))
        self.label_mode.config(text=self.i18n.t("label_mode"))
        self.label_language.config(text=self.i18n.t("label_language"))
        self.button_compute.config(text=self.i18n.t("button_compute"))
        self.button_clear.config(text=self.i18n.t("button_clear"))
        self.button_copy.config(text=self.i18n.t("button_copy"))
        self.button_calculate.config(text=self.i18n.t("button_calculate"))
        self.label_result.config(text=self.i18n.t("result_header"))

        self._refresh_modes()

        self._refresh_languages()

    def _mode_labels(self, degree: int) -> dict[str, str]:
        labels: dict[str, str] = {
            "arith": self.i18n.t("mode_arithmetic"),
            "complex": self.i18n.t("mode_complex"),
            "all": self.i18n.t("mode_all"),
        }
        for k in range(degree):
            labels[f"analytic:{k}"] = self.i18n.t("mode_analytic_root").format(
                index=k + 1
            )
        return labels

    def _refresh_languages(self, *_args) -> None:
        current_code = self.i18n.language
        self.i18n.reload()
        items = self.i18n.available_languages()
        self._language_by_name = {name: code for code, name in items}
        names = [name for _, name in items]
        self.combo_language["values"] = names
        self._fit_combobox(self.combo_language, names, min_width=10, max_width=28)
        current_name = None
        for code, name in items:
            if code == current_code:
                current_name = name
                break
        if current_name:
            self.language_var.set(current_name)

    def _on_language_selected(self, _event: tk.Event) -> None:
        name = self.language_var.get()
        code = self._language_by_name.get(name)
        if code:
            self.i18n.set_language(code)
            self._apply_language()
            self._set_status(self.i18n.t("status_ready"))

    def _on_mode_selected(self, _event: tk.Event) -> None:
        selected = self.mode_var.get()
        key = self._mode_by_label.get(selected)
        if key:
            self.mode_key = key

    def _on_compute(self) -> None:
        self._set_status(self.i18n.t("status_ready"))
        self._set_output("")
        try:
            parsed = parse_number(self.number_var.get())
            degree = parse_degree(self.degree_var.get())
            precision = parse_precision(self.precision_var.get())
        except InputError as exc:
            self._set_error(str(exc))
            return

        lines = [f"{self.i18n.t('result_header')}:"]
        if self.mode_key == "arith":
            if parsed.is_complex:
                self._set_error("arithmetic_not_real")
                return
            root = principal_root(parsed, degree)
            if isinstance(root, complex):
                self._set_error("arithmetic_not_real")
                return
            if isinstance(root, float) and math.isnan(root):
                self._set_error("arithmetic_not_real")
                return
            rect = format_root(root, precision)
            lines.append(f"k=0: {rect}")
        elif self.mode_key == "complex":
            root = principal_root(parsed, degree)
            rect = format_root(root, precision)
            if isinstance(root, complex):
                polar = format_polar(root, precision)
                lines.append(f"k=0: {rect} ({polar})")
            else:
                lines.append(f"k=0: {rect}")
        elif self.mode_key == "all":
            roots = all_roots(parsed, degree)
            for k, root in enumerate(roots):
                rect = format_root(root, precision)
                polar = format_polar(root, precision)
                lines.append(f"k={k}: {rect} ({polar})")
        elif self.mode_key.startswith("analytic:"):
            try:
                k = int(self.mode_key.split(":", 1)[1])
            except ValueError:
                k = 0
            roots = all_roots(parsed, degree)
            if 0 <= k < len(roots):
                root = roots[k]
                rect = format_root(root, precision)
                polar = format_polar(root, precision)
                lines.append(f"k={k}: {rect} ({polar})")
            else:
                root = principal_root(parsed, degree)
                rect = format_root(root, precision)
                lines.append(f"k=0: {rect}")
        else:
            root = principal_root(parsed, degree)
            rect = format_root(root, precision)
            lines.append(f"k=0: {rect}")
        self._set_output("\n".join(lines))

    def _on_clear(self) -> None:
        self.number_var.set("")
        self._set_output("")
        self._set_status(self.i18n.t("status_ready"))

    def _on_copy(self) -> None:
        text = self.text_output.get("1.0", "end").strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self._set_status(self.i18n.t("status_copied"))

    def _set_output(self, text: str) -> None:
        self.text_output.configure(state="normal")
        self.text_output.delete("1.0", "end")
        self.text_output.insert("1.0", text)
        self.text_output.configure(state="disabled")

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _set_error(self, error_code: str) -> None:
        key = f"error_{error_code}"
        message = self.i18n.t(key)
        if message == key:
            message = self.i18n.t("status_error")
        self._set_status(message)
        self._set_output(message)

    def _on_resize(self, event: tk.Event) -> None:
        if event.widget is self.root:
            self._draw_background(event.width, event.height)

    def _draw_background(self, width: int, height: int) -> None:
        self.bg_canvas.delete("all")
        self._draw_gradient(width, height)
        self._draw_shapes(width, height)

    def _draw_gradient(self, width: int, height: int) -> None:
        r1, g1, b1 = self._hex_to_rgb(self.colors["bg_top"])
        r2, g2, b2 = self._hex_to_rgb(self.colors["bg_bottom"])
        for i in range(0, height, 2):
            ratio = i / max(1, height - 1)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.bg_canvas.create_line(0, i, width, i, fill=color)

    def _draw_shapes(self, width: int, height: int) -> None:
        self.bg_canvas.create_oval(
            -120, -100, 260, 260, outline="#e5ddd3", width=2
        )
        self.bg_canvas.create_oval(
            width - 260,
            height - 220,
            width + 140,
            height + 140,
            outline="#d9e2ef",
            width=2,
        )

    def _hex_to_rgb(self, value: str) -> tuple[int, int, int]:
        value = value.lstrip("#")
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)

    def _fade_in(self) -> None:
        try:
            self.root.attributes("-alpha", 0.0)
        except tk.TclError:
            return

        def step(alpha: float) -> None:
            if alpha >= 1.0:
                self.root.attributes("-alpha", 1.0)
                return
            self.root.attributes("-alpha", alpha)
            self.root.after(16, step, alpha + 0.06)

        step(0.0)

    def _on_degree_change(self, *_args) -> None:
        self._refresh_modes()

    def _refresh_modes(self) -> None:
        try:
            degree = parse_degree(self.degree_var.get())
        except InputError:
            degree = 2
        mode_labels = self._mode_labels(degree)
        self._mode_by_label = {label: key for key, label in mode_labels.items()}
        mode_values = list(mode_labels.values())
        self.combo_mode["values"] = mode_values
        self._fit_combobox(self.combo_mode, mode_values, min_width=18, max_width=36)
        if self.mode_key not in mode_labels:
            self.mode_key = "complex"
        self.mode_var.set(mode_labels.get(self.mode_key, ""))

    def _fit_combobox(
        self,
        combobox: ttk.Combobox,
        values: list[str],
        min_width: int,
        max_width: int,
    ) -> None:
        if not values:
            combobox.config(width=min_width)
            return
        longest = max(len(value) for value in values)
        width = min(max(longest + 2, min_width), max_width)
        combobox.config(width=width)


def run_app() -> None:
    root = tk.Tk()
    i18n = I18nManager()
    MainWindow(root, i18n)
    root.mainloop()
