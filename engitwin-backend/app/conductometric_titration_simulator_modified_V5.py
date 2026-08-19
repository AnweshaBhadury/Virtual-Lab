"""
============================================================================
 VIRTUAL CHEMISTRY LAB SIMULATOR
 Experiment 2 : Conductometric Titration of HCl with NaOH Solution
 (Determination of the Strength of an Unknown HCl Solution)

 Built for  : Python 3.14  (Tkinter + Matplotlib + NumPy)
 Behaviour  : Mimics a real conductometric titration bench --
              conductivity meter, magnetic stirrer, burette stand,
              beaker + electrode, step-locked procedure, wrong-operation
              detection, click/beep feedback, live graph plotting and
              a proper "practical-book" style observation table.
============================================================================
"""

import math
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


# ============================================================================
#  1.  PHYSICS / CHEMISTRY MODEL
# ============================================================================
class TitrationPhysics:
    """
    Simulates the conductance of the HCl / NaOH system based on
    ionic (equivalent) conductivities, exactly as described in the
    lab-manual theory:

        H+   lambda = 350
        OH-  lambda = 200
        Na+  lambda =  50
        Cl-  lambda =  76

    conductance  L  is proportional to  sum( c_ion * lambda_ion )
    where c_ion is the instantaneous concentration (meq/mL) of each ion
    in the mixed solution as NaOH is added drop-wise from the burette.
    """

    LAM_H, LAM_CL, LAM_NA, LAM_OH = 350.0, 76.0, 50.0, 200.0
    DROP_ML = 0.05          # 1 drop = 0.05 mL   (given in manual)
    BURETTE_CAPACITY_ML = 50.0

    def __init__(self):
        self.V1 = 25.0                                  # mL of HCl taken
        self.N2 = 0.5                                    # NaOH strength = N/2 (standardised)
        # "Unknown" strength of HCl the student must discover -- randomised
        # a little every run so the simulator behaves like a real bench.
        self.N1_true = round(random.uniform(0.040, 0.070), 4)
        self.k = 0.235                                    # meter calibration constant

    @property
    def V2_equivalence_ml(self):
        return (self.V1 * self.N1_true) / self.N2

    def conductance_at(self, V2_ml: float) -> float:
        """Return the (noisy) meter reading in mho x10^-3 units for a
        given volume (mL) of NaOH added so far."""
        V1, N1, N2 = self.V1, self.N1_true, self.N2
        total_v = V1 + V2_ml
        meq_H_initial = V1 * N1
        meq_OH_added = V2_ml * N2
        meq_H_left = max(0.0, meq_H_initial - meq_OH_added)
        meq_OH_excess = max(0.0, meq_OH_added - meq_H_initial)

        c_H = meq_H_left / total_v
        c_Cl = meq_H_initial / total_v          # Cl- is a spectator, constant moles
        c_Na = meq_OH_added / total_v
        c_OH = meq_OH_excess / total_v

        L = self.k * (c_H * self.LAM_H + c_Cl * self.LAM_CL +
                       c_Na * self.LAM_NA + c_OH * self.LAM_OH)
        noise = random.uniform(-0.03, 0.03)
        return round(max(0.05, L + noise), 2)


# ============================================================================
#  2.  EXPERIMENT STEP DEFINITIONS  (locked, sequential procedure)
# ============================================================================
STEPS = [
    ("Power ON the conductivity meter", "power"),
    ("Calibrate / zero the conductivity meter", "calibrate"),
    ("Pipette 25.0 mL of the unknown HCl solution into the beaker", "take_hcl"),
    ("Immerse the conductivity cell (electrode) into the HCl solution", "immerse"),
    ("Switch ON the magnetic stirrer", "stirrer"),
    ("Record the INITIAL conductance reading (before adding NaOH)", "record_initial"),
    ("Fill the burette with standard N/2 NaOH solution and open the stopcock", "fill_burette"),
    ("Add NaOH drop-wise and record the conductance after every addition", "titrate"),
    ("Plot the graph and locate the equivalence point", "graph"),
    ("Calculate the strength of the unknown HCl", "calculate"),
]


# ============================================================================
#  3.  MAIN APPLICATION
# ============================================================================
class LabSimulator(tk.Tk):

    BG = "#0e1620"
    PANEL = "#16212e"
    ACCENT = "#39c0ff"
    OK = "#33d17a"
    WARN = "#f5c211"
    ERR = "#ff5c5c"
    TEXT = "#e6edf3"

    def __init__(self):
        super().__init__()
        self.title("Virtual Lab | Conductometric Titration of HCl vs NaOH")
        self.geometry("1360x860")
        self.configure(bg=self.BG)
        self.minsize(1180, 760)

        self.phys = TitrationPhysics()

        # ---- state flags -----------------------------------------------
        self.meter_on = False
        self.calibrated = False
        self.hcl_taken = False
        self.electrode_in = False
        self.stirrer_on = False
        self.initial_recorded = False
        self.burette_filled = False
        self.valve_open = False
        self.current_step = 0
        self.needs_recording_before_next_add = False

        self.total_drops = 0
        self.readings = []          # list of dict: drops, vol, conductance, stirred(bool)
        self.obs_no = 0

        self.stirrer_angle = 0
        self.drop_anim_job = None

        self._build_style()
        self._build_layout()
        self._refresh_all()
        self._animate_stirrer()

    # ------------------------------------------------------------------
    #  STYLE
    # ------------------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TNotebook", background=self.BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.PANEL, foreground=self.TEXT,
                         padding=(16, 8), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.ACCENT)],
                   foreground=[("selected", "#00131c")])
        style.configure("Treeview", background="#0f1a24", fieldbackground="#0f1a24",
                         foreground=self.TEXT, rowheight=26, font=("Consolas", 10))
        style.configure("Treeview.Heading", background="#1c2b3a", foreground=self.ACCENT,
                         font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=6)

    # ------------------------------------------------------------------
    #  SOUND FEEDBACK
    # ------------------------------------------------------------------
    def play(self, kind="click"):
        freqs = {"click": (950, 40), "toggle": (700, 60),
                 "success": (1500, 130), "error": (260, 220), "warn": (520, 150)}
        f, d = freqs.get(kind, (900, 40))
        if HAS_WINSOUND:
            try:
                winsound.Beep(f, d)
                return
            except Exception:
                pass
        try:
            self.bell()
        except Exception:
            print("\a", end="")

    # ------------------------------------------------------------------
    #  LAYOUT
    # ------------------------------------------------------------------
    def _build_layout(self):
        header = tk.Frame(self, bg=self.PANEL, height=56)
        header.pack(side="top", fill="x")
        tk.Label(header, text="⚗  CONDUCTOMETRIC TITRATION  —  HCl  vs  NaOH",
                  bg=self.PANEL, fg=self.ACCENT, font=("Segoe UI", 16, "bold")).pack(side="left", padx=16, pady=10)
        self.step_lbl = tk.Label(header, text="", bg=self.PANEL, fg=self.TEXT,
                                  font=("Segoe UI", 10, "bold"))
        self.step_lbl.pack(side="right", padx=16)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_lab = tk.Frame(self.nb, bg=self.BG)
        self.tab_table = tk.Frame(self.nb, bg=self.BG)
        self.tab_graph = tk.Frame(self.nb, bg=self.BG)
        self.tab_help = tk.Frame(self.nb, bg=self.BG)

        self.nb.add(self.tab_lab, text="  🧪  Virtual Bench  ")
        self.nb.add(self.tab_table, text="  📋  Observation Table  ")
        self.nb.add(self.tab_graph, text="  📈  Graph & Result  ")
        self.nb.add(self.tab_help, text="  📖  Procedure  ")

        self._build_lab_tab()
        self._build_table_tab()
        self._build_graph_tab()
        self._build_help_tab()

    # ------------------------------------------------------------------
    #  TAB 1 : VIRTUAL BENCH (apparatus + controls + instruction/log)
    # ------------------------------------------------------------------
    def _build_lab_tab(self):
        left = tk.Frame(self.tab_lab, bg=self.BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.canvas = tk.Canvas(left, bg="#0a121b", width=760, height=560, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # instruction bar directly under the bench
        self.instr = tk.Label(left, text="", bg="#122536", fg=self.ACCENT, anchor="w",
                               font=("Segoe UI", 11, "bold"), padx=12, pady=8)
        self.instr.pack(fill="x", pady=(6, 0))

        right = tk.Frame(self.tab_lab, bg=self.PANEL, width=380)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(right, text="CONTROL PANEL", bg=self.PANEL, fg=self.ACCENT,
                  font=("Segoe UI", 12, "bold")).pack(pady=(12, 4))

        def sect(title):
            f = tk.Frame(right, bg=self.PANEL)
            f.pack(fill="x", padx=14, pady=(10, 2))
            tk.Label(f, text=title, bg=self.PANEL, fg="#8fa6bd",
                      font=("Segoe UI", 9, "bold")).pack(anchor="w")
            return f

        sect("① Meter")
        self.btn_power = self._btn(right, "⏻  Power ON Meter", self.act_power)
        self.btn_cal = self._btn(right, "⚙  Calibrate / Zero", self.act_calibrate)

        sect("② Sample Preparation")
        self.btn_hcl = self._btn(right, "🧫  Pipette 25 mL HCl", self.act_take_hcl)
        self.btn_electrode = self._btn(right, "🔌  Immerse Electrode", self.act_immerse)
        self.btn_stirrer = self._btn(right, "🌀  Toggle Stirrer", self.act_stirrer)
        self.btn_initial = self._btn(right, "📏  Record Initial Reading", self.act_record_initial)

        sect("③ Burette / Titrant")
        self.btn_fill = self._btn(right, "🧴  Fill Burette (N/2 NaOH)", self.act_fill_burette)
        self.btn_valve = self._btn(right, "🚰  Open / Close Stopcock", self.act_valve)

        sect("④ Titration")
        row = tk.Frame(right, bg=self.PANEL)
        row.pack(fill="x", padx=14, pady=2)
        self._btn(row, "+1 drop", lambda: self.act_add_drops(1), side="left", w=8)
        self._btn(row, "+5 drops", lambda: self.act_add_drops(5), side="left", w=8)
        self._btn(row, "+10 drops", lambda: self.act_add_drops(10), side="left", w=8)
        self.btn_record = self._btn(right, "✅  Record Conductance", self.act_record_reading)

        sect("⑤ Finish")
        self._btn(right, "🔄  Reset Experiment", self.act_reset)

        tk.Label(right, text="LIVE READOUT", bg=self.PANEL, fg="#8fa6bd",
                  font=("Segoe UI", 9, "bold")).pack(pady=(16, 2))
        self.readout = tk.Label(right, text="-- mho", bg="#03110a", fg="#42ff8a",
                                  font=("Consolas", 26, "bold"), width=12)
        self.readout.pack(pady=(0, 10))

        tk.Label(right, text="EVENT / ERROR LOG", bg=self.PANEL, fg="#8fa6bd",
                  font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14)
        logf = tk.Frame(right, bg=self.PANEL)
        logf.pack(fill="both", expand=True, padx=14, pady=(2, 12))
        self.log = tk.Text(logf, height=10, bg="#0a1420", fg=self.TEXT, wrap="word",
                             font=("Consolas", 9), relief="flat")
        self.log.pack(fill="both", expand=True)
        self.log.tag_config("err", foreground=self.ERR)
        self.log.tag_config("warn", foreground=self.WARN)
        self.log.tag_config("ok", foreground=self.OK)
        self.log.tag_config("info", foreground="#8fa6bd")

    def _btn(self, parent, text, cmd, side="top", w=None):
        b = tk.Button(parent, text=text, command=cmd, bg="#1c2b3a", fg=self.TEXT,
                       activebackground=self.ACCENT, activeforeground="#00131c",
                       relief="flat", font=("Segoe UI", 9, "bold"), bd=0,
                       padx=8, pady=7, cursor="hand2", width=w)
        b.pack(side=side, fill=("x" if side == "top" else None), padx=(0 if side == "left" else 14),
               pady=3 if side == "top" else 0, expand=(side == "left"))
        return b

    # ------------------------------------------------------------------
    #  TAB 2 : OBSERVATION TABLE  (matches practical-book layout)
    # ------------------------------------------------------------------
    def _build_table_tab(self):
        top = tk.Frame(self.tab_table, bg=self.BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="MEASUREMENT TABLE", bg=self.BG, fg=self.ACCENT,
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(top, text="1 drop = 0.05 mL          Vol. of HCl taken = 25.0 mL          "
                            "Strength of NaOH (S2) = N/2",
                  bg=self.BG, fg=self.TEXT, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 0))

        cols = ("obs", "vhcl", "drops", "vol", "cond", "note")
        headers = {"obs": "No. of\nObservation", "vhcl": "Vol. of HCl\nTaken (mL)",
                    "drops": "No. of\nDrops (n)", "vol": "Vol. of NaOH\n(mL)",
                    "cond": "Conductance\n(mho)", "note": "Note"}
        self.tree = ttk.Treeview(self.tab_table, columns=cols, show="headings", height=20)
        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=140 if c != "note" else 220, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ------------------------------------------------------------------
    #  TAB 3 : GRAPH & RESULT
    # ------------------------------------------------------------------
    def _build_graph_tab(self):
        top = tk.Frame(self.tab_graph, bg=self.BG)
        top.pack(fill="x", padx=10, pady=8)
        self._btn(top, "📈  Plot Graph & Find Equivalence Point", self.act_plot_graph, side="left")
        self._btn(top, "🧮  Calculate Strength of HCl", self.act_calculate, side="left")

        body = tk.Frame(self.tab_graph, bg=self.BG)
        body.pack(fill="both", expand=True, padx=10, pady=4)

        self.fig = Figure(figsize=(7.4, 5.6), dpi=100, facecolor="#0e1620")
        self.ax = self.fig.add_subplot(111)
        self._style_axes()
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=body)
        self.canvas_fig.get_tk_widget().pack(side="left", fill="both", expand=True)

        res = tk.Frame(body, bg=self.PANEL, width=380)
        res.pack(side="right", fill="y")
        res.pack_propagate(False)
        tk.Label(res, text="CALCULATION SHEET", bg=self.PANEL, fg=self.ACCENT,
                  font=("Segoe UI", 12, "bold")).pack(pady=12)
        self.result_text = tk.Text(res, bg="#0a1420", fg=self.TEXT, font=("Consolas", 10),
                                     relief="flat", wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.result_text.insert("end", "Complete the titration on the Virtual Bench tab, "
                                        "then click 'Plot Graph' and 'Calculate Strength'.")
        self.result_text.config(state="disabled")

    def _style_axes(self):
        self.ax.clear()
        self.ax.set_facecolor("#0a121b")
        self.ax.set_title("Conductance  vs.  Volume of NaOH added", color=self.TEXT, fontsize=11)
        self.ax.set_xlabel("Volume of NaOH (mL)", color=self.TEXT)
        self.ax.set_ylabel("Conductance (mho)", color=self.TEXT)
        self.ax.tick_params(colors=self.TEXT)
        for spine in self.ax.spines.values():
            spine.set_color("#3a4c5e")
        self.ax.grid(color="#20323f", linestyle="--", linewidth=0.6)

    # ------------------------------------------------------------------
    #  TAB 4 : PROCEDURE / HELP
    # ------------------------------------------------------------------
    def _build_help_tab(self):
        txt = tk.Text(self.tab_help, bg="#0a1420", fg=self.TEXT, font=("Segoe UI", 11),
                        wrap="word", relief="flat", padx=18, pady=16)
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        content = """PROCEDURE  —  Conductometric Titration of HCl with NaOH

Aim:  To determine the strength (normality) of an unknown HCl solution by
conductometric titration against standard N/2 NaOH solution.

Apparatus:  Conductivity meter + cell, burette, pipette, beaker, magnetic
stirrer, volumetric flask, retort stand.

Chemicals:  Standard oxalic acid, N/2 NaOH (standardised against oxalic
acid using phenolphthalein), unknown HCl (~N/20), phenolphthalein.

Theory (summary):
 HCl is a strong monobasic acid that ionises completely. The mobility of
 H+ (lambda = 350) is far higher than Na+ (lambda = 50), so the initial
 conductance of the acid is high. As NaOH is added:

     H+ + Cl- + Na+ + OH-  ->  Na+ + Cl- + H2O

 the fast H+ ions are progressively replaced by the slower Na+ ions, so
 conductance falls sharply until the equivalence point (only NaCl in
 solution). Beyond this point, excess Na+ and OH- ions raise the
 conductance again. Plotting conductance (y) against volume of NaOH (x)
 gives two straight lines; their intersection is the equivalence point.

Step-by-step procedure simulated on the 'Virtual Bench' tab:
  1. Power ON the conductivity meter and allow it to warm up.
  2. Calibrate / zero the meter using the CAL control.
  3. Pipette 25.0 mL of the unknown HCl solution into a clean beaker.
  4. Immerse the conductivity cell fully in the solution (electrodes
     must be covered, not touching the beaker walls/base).
  5. Switch ON the magnetic stirrer for uniform mixing.
  6. Record the INITIAL conductance (before any NaOH is added).
  7. Fill the burette with standard N/2 NaOH and open the stopcock.
  8. Add NaOH drop-wise (1 drop = 0.05 mL). After EVERY addition, stir
     and record the new conductance value. Continue past the point where
     the reading starts rising again (collect points on both branches).
  9. Plot conductance vs. volume of NaOH added on the Graph tab. Two
     straight lines are fitted; their intersection gives V2 (mL of NaOH
     required for complete neutralisation).
 10. Apply the law of equivalence:      V1 x S1 = V2 x S2
     where V1 = 25 mL, S2 = N/2 (0.5 N), and V2 is read from the graph,
     to calculate S1, the strength of the unknown HCl.

Precautions:
  • Wash the conductivity cell thoroughly with deionised water before use.
  • Note and keep the temperature constant during the run.
  • All glassware (pipette, burette, flask) must be calibrated.
  • NaOH must be added drop-wise, with stirring, and conductance read
    only after the solution is uniformly mixed (dilution error otherwise).

Molar (equivalent) conductivities used @ 25 C:
   H+ = 350      OH- = 200      Na+ = 50      Cl- = 76
"""
        txt.insert("end", content)
        txt.config(state="disabled")

    # ==================================================================
    #  APPARATUS DRAWING  (pseudo-3D canvas art)
    # ==================================================================
    def _grad_rect(self, x0, y0, x1, y1, c1, c2, steps=24, horiz=False):
        r1, g1, b1 = self.winfo_rgb(c1)
        r2, g2, b2 = self.winfo_rgb(c2)
        for i in range(steps):
            t = i / (steps - 1)
            r = int(r1 + (r2 - r1) * t) >> 8
            g = int(g1 + (g2 - g1) * t) >> 8
            b = int(b1 + (b2 - b1) * t) >> 8
            color = f"#{r:02x}{g:02x}{b:02x}"
            if horiz:
                xa = x0 + (x1 - x0) * i / steps
                xb = x0 + (x1 - x0) * (i + 1) / steps
                self.canvas.create_rectangle(xa, y0, xb, y1, fill=color, outline="", tags="app")
            else:
                ya = y0 + (y1 - y0) * i / steps
                yb = y0 + (y1 - y0) * (i + 1) / steps
                self.canvas.create_rectangle(x0, ya, x1, yb, fill=color, outline="", tags="app")

    def draw_bench(self):
        c = self.canvas
        c.delete("app")
        W = int(c.winfo_width() or 760)
        H = int(c.winfo_height() or 560)

        # bench surface shadow
        c.create_rectangle(0, H - 60, W, H, fill="#0a1620", outline="", tags="app")
        c.create_rectangle(0, H - 62, W, H - 58, fill="#1c3244", outline="", tags="app")

        # ---------------- RETORT STAND + BURETTE ------------------------
        stand_x = 150
        c.create_rectangle(stand_x - 6, 60, stand_x + 6, H - 60, fill="#3a4a58", outline="#1c2732", tags="app")
        c.create_rectangle(stand_x - 60, H - 66, stand_x + 60, H - 56, fill="#3a4a58", outline="#1c2732", tags="app")
        clamp_y = 150
        c.create_rectangle(stand_x - 6, clamp_y, stand_x + 70, clamp_y + 14, fill="#59707f", outline="#1c2732", tags="app")

        bx0, by0, bx1, by1 = stand_x + 40, 70, stand_x + 84, 260
        self._grad_rect(bx0, by0, bx1, by1, "#dff3ff", "#8fc7de")
        c.create_rectangle(bx0, by0, bx1, by1, outline="#5c8296", width=2, tags="app")
        for i in range(1, 10):
            yy = by0 + (by1 - by0) * i / 10
            c.create_line(bx0, yy, bx0 + 6, yy, fill="#4c6c7d", tags="app")

        # liquid level in burette (falls as NaOH used)
        frac_left = 1.0 - min(1.0, (self.total_drops * self.phys.DROP_ML) / self.phys.BURETTE_CAPACITY_ML)
        liq_top = by0 + 8 + (by1 - by0 - 16) * (1 - frac_left)
        if self.burette_filled:
            self._grad_rect(bx0 + 3, liq_top, bx1 - 3, by1 - 6, "#bfe8ff", "#4fa9d6")

        # stopcock
        cock_y = by1 + 4
        cock_color = self.OK if self.valve_open else "#8899a6"
        c.create_oval(bx0 + 10, cock_y, bx1 - 10, cock_y + 14, fill=cock_color, outline="#334", tags="app")
        c.create_line((bx0 + bx1) / 2, by1, (bx0 + bx1) / 2, by1 + 34, fill="#7fa8bd", width=3, tags="app")

        c.create_text(bx0 - 12, (by0 + by1) / 2, text="BURETTE\n(N/2 NaOH)", fill=self.TEXT,
                       font=("Segoe UI", 8, "bold"), angle=90, tags="app")

        # ---------------- MAGNETIC STIRRER + BEAKER ----------------------
        # Centre the sample vessel on the burette tip so NaOH drops fall
        # directly into the beaker; the stirrer remains immediately below it.
        plate_x, plate_y, plate_w, plate_h = 117, 455, 190, 26
        self._grad_rect(plate_x, plate_y, plate_x + plate_w, plate_y + plate_h, "#3d4650", "#171b1f")
        c.create_oval(plate_x + plate_w / 2 - 70, plate_y - 6, plate_x + plate_w / 2 + 70, plate_y + 6,
                      fill="#232a30", outline="#0d1114", tags="app")
        knob_color = self.OK if self.stirrer_on else "#66707a"
        c.create_oval(plate_x + plate_w - 34, plate_y + 4, plate_x + plate_w - 10, plate_y + 20,
                      fill=knob_color, outline="#111", tags="app")
        c.create_text(plate_x + plate_w / 2, plate_y + plate_h + 12, text="MAGNETIC STIRRER",
                       fill="#8fa6bd", font=("Segoe UI", 8, "bold"), tags="app")

        # beaker
        cx = plate_x + plate_w / 2
        beak_top, beak_bot = 304, plate_y - 4
        bw_top, bw_bot = 95, 80
        pts = [cx - bw_top, beak_top, cx + bw_top, beak_top,
               cx + bw_bot, beak_bot, cx - bw_bot, beak_bot]
        c.create_polygon(*pts, fill="#101b24", outline="#5c7284", width=2, tags="app")

        if self.hcl_taken:
            liquid_h = 0.55 * (beak_bot - beak_top)
            ly0 = beak_bot - liquid_h
            frac_w = 1 - (bw_top - bw_bot) * (liquid_h / (beak_bot - beak_top)) / bw_top
            lx0, lx1 = cx - bw_top * frac_w, cx + bw_top * frac_w
            colour_top = "#e9f7c9" if not self._eq_passed() else "#d8ecff"
            self._grad_rect(lx0, ly0, lx1, beak_bot - 4, colour_top, "#b9d98a" if not self._eq_passed() else "#8fc7de")
            # stir bar
            if self.stirrer_on:
                ang = math.radians(self.stirrer_angle)
                sx, sy, L = cx, beak_bot - 10, 16
                c.create_line(sx - L * math.cos(ang), sy - L * math.sin(ang) * 0.3,
                               sx + L * math.cos(ang), sy + L * math.sin(ang) * 0.3,
                               fill="#ff5c5c", width=4, capstyle="round", tags="app")

        c.create_polygon(cx - bw_top, beak_top, cx - bw_top + 12, beak_top - 10,
                          cx + bw_top - 12, beak_top - 10, cx + bw_top, beak_top,
                          fill="", outline="#5c7284", tags="app")
        c.create_text(cx, beak_bot + 16, text="BEAKER (HCl sample)", fill="#8fa6bd",
                       font=("Segoe UI", 8, "bold"), tags="app")

        # electrode / conductivity cell
        if self.electrode_in:
            ex = cx + 34
            c.create_rectangle(ex - 4, beak_top - 60, ex + 4, beak_bot - 20, fill="#c8c8c8", outline="#555", tags="app")
            c.create_rectangle(ex - 10, beak_top - 70, ex + 10, beak_top - 55, fill="#3a3a3a", outline="#111", tags="app")
            c.create_line(ex, beak_top - 70, ex + 140, beak_top - 130, fill="#222", width=2, tags="app")

        # ---------------- CONDUCTIVITY METER -----------------------------
        mx0, my0, mx1, my1 = 560, 130, 760, 260
        self._grad_rect(mx0, my0, mx1, my1, "#2b3a47", "#101a22")
        c.create_rectangle(mx0, my0, mx1, my1, outline="#0a0f14", width=3, tags="app")
        c.create_text((mx0 + mx1) / 2, my0 + 14, text="CONDUCTIVITY METER", fill=self.ACCENT,
                       font=("Segoe UI", 9, "bold"), tags="app")

        disp_col = "#03110a" if self.meter_on else "#050505"
        c.create_rectangle(mx0 + 16, my0 + 30, mx1 - 16, my0 + 78, fill=disp_col, outline="#000", tags="app")
        val_txt = f"{self.readings[-1]['cond']:.2f}" if self.readings else ("0.00" if self.meter_on else "----")
        digit_col = "#42ff8a" if self.meter_on else "#333"
        c.create_text((mx0 + mx1) / 2, my0 + 54, text=f"{val_txt}  mho", fill=digit_col,
                       font=("Consolas", 16, "bold"), tags="app")

        # power / cal indicator LEDs
        c.create_oval(mx0 + 16, my1 - 34, mx0 + 28, my1 - 22,
                       fill=(self.OK if self.meter_on else "#552"), outline="#000", tags="app")
        c.create_text(mx0 + 60, my1 - 28, text="POWER", fill="#8fa6bd", font=("Segoe UI", 7), tags="app")
        c.create_oval(mx0 + 100, my1 - 34, mx0 + 112, my1 - 22,
                       fill=(self.ACCENT if self.calibrated else "#552"), outline="#000", tags="app")
        c.create_text(mx0 + 150, my1 - 28, text="CAL", fill="#8fa6bd", font=("Segoe UI", 7), tags="app")

        c.create_line(mx0, my0 + 190, ex + 140 if self.electrode_in else mx0 - 60, beak_top - 130,
                       fill="#222", width=2, tags="app") if self.electrode_in else None

    def _eq_passed(self):
        return self.total_drops * self.phys.DROP_ML > self.phys.V2_equivalence_ml

    def _animate_stirrer(self):
        if self.stirrer_on:
            self.stirrer_angle = (self.stirrer_angle + 25) % 360
        self.draw_bench()
        self.after(140, self._animate_stirrer)

    # ==================================================================
    #  STATE / STEP HELPERS
    # ==================================================================
    def log_msg(self, text, kind="info"):
        icon = {"info": "•", "ok": "✔", "warn": "⚠", "err": "✖"}[kind]
        self.log.insert("end", f"{icon} {text}\n", kind)
        self.log.see("end")

    def error(self, text):
        self.play("error")
        self.log_msg(text, "err")
        messagebox.showerror("Incorrect Operation", text)

    def warn(self, text):
        self.play("warn")
        self.log_msg(text, "warn")

    def ok(self, text):
        self.play("success")
        self.log_msg(text, "ok")

    def _refresh_all(self):
        self.step_lbl.config(text=f"STEP {min(self.current_step + 1, len(STEPS))} / {len(STEPS)}")
        if self.current_step < len(STEPS):
            self.instr.config(text="NEXT STEP  ➜   " + STEPS[self.current_step][0])
        else:
            self.instr.config(text="✅ Procedure complete — review the Graph & Result tab.")
        self.draw_bench()

    def advance_if(self, key):
        """Move the guided-step pointer forward if this action matches
        the step currently expected (purely a teaching aid; most actions
        remain individually validated regardless of step order)."""
        if self.current_step < len(STEPS) and STEPS[self.current_step][1] == key:
            self.current_step += 1

    # ==================================================================
    #  ACTIONS  (each with incorrect-operation detection)
    # ==================================================================
    def act_power(self):
        self.play("toggle")
        self.meter_on = not self.meter_on
        if self.meter_on:
            self.ok("Conductivity meter powered ON.")
            self.advance_if("power")
        else:
            self.calibrated = False
            self.warn("Meter powered OFF — you will need to recalibrate before use.")
        self._refresh_all()

    def act_calibrate(self):
        if not self.meter_on:
            self.error("Cannot calibrate: the conductivity meter is OFF. Power it on first.")
            return
        self.play("click")
        self.calibrated = True
        self.ok("Meter calibrated / zeroed successfully.")
        self.advance_if("calibrate")
        self._refresh_all()

    def act_take_hcl(self):
        if self.hcl_taken:
            self.warn("HCl has already been pipetted into the beaker.")
            return
        self.play("click")
        self.hcl_taken = True
        self.ok("25.0 mL of unknown HCl pipetted into the beaker.")
        self.advance_if("take_hcl")
        self._refresh_all()

    def act_immerse(self):
        if not self.hcl_taken:
            self.error("Cannot immerse electrode: the beaker is empty. Take the HCl sample first.")
            return
        self.play("click")
        self.electrode_in = not self.electrode_in
        if self.electrode_in:
            self.ok("Conductivity cell immersed in the HCl solution.")
            self.advance_if("immerse")
        else:
            self.warn("Electrode removed from the solution.")
        self._refresh_all()

    def act_stirrer(self):
        if not self.hcl_taken:
            self.error("Cannot start stirrer: no solution in the beaker yet.")
            return
        self.play("toggle")
        self.stirrer_on = not self.stirrer_on
        self.log_msg("Magnetic stirrer " + ("switched ON." if self.stirrer_on else "switched OFF."),
                      "ok" if self.stirrer_on else "info")
        self.advance_if("stirrer")
        self._refresh_all()

    def act_record_initial(self):
        if not (self.meter_on and self.calibrated):
            self.error("Cannot record: meter must be powered ON and calibrated first.")
            return
        if not (self.hcl_taken and self.electrode_in):
            self.error("Cannot record: HCl sample must be prepared and electrode immersed.")
            return
        if not self.stirrer_on:
            self.warn("Stirrer is OFF — recording without stirring gives an unreliable reading.")
        if self.initial_recorded:
            self.warn("Initial reading was already recorded.")
            return
        cond = self.phys.conductance_at(0.0)
        self.obs_no += 1
        row = {"drops": 0, "vol": 0.0, "cond": cond, "stirred": self.stirrer_on}
        self.readings.append(row)
        self._push_row(row)
        self.initial_recorded = True
        self.ok(f"Initial conductance recorded: {cond} mho (0 drops of NaOH added).")
        self.advance_if("record_initial")
        self._refresh_all()

    def act_fill_burette(self):
        if not self.initial_recorded:
            self.error("Record the initial conductance of HCl before filling the burette.")
            return
        self.play("click")
        self.burette_filled = True
        self.ok("Burette filled to the mark with standard N/2 NaOH solution.")
        self.advance_if("fill_burette")
        self._refresh_all()

    def act_valve(self):
        if not self.burette_filled:
            self.error("Cannot open stopcock: the burette has not been filled with NaOH.")
            return
        self.play("toggle")
        self.valve_open = not self.valve_open
        self.log_msg("Stopcock " + ("opened." if self.valve_open else "closed."), "ok")
        self._refresh_all()

    def act_add_drops(self, n):
        # ---- incorrect-operation checks -------------------------------
        if not (self.meter_on and self.calibrated):
            self.error("Cannot titrate: conductivity meter must be ON and calibrated.")
            return
        if not (self.hcl_taken and self.electrode_in and self.initial_recorded):
            self.error("Cannot titrate: complete sample setup and record the initial reading first.")
            return
        if not self.burette_filled:
            self.error("Cannot titrate: fill the burette with NaOH first.")
            return
        if not self.valve_open:
            self.error("Cannot titrate: the burette stopcock is closed. Open it first.")
            return
        if self.needs_recording_before_next_add:
            self.error("Record the conductance for the previous addition before adding more NaOH "
                       "(this matches the practical's one-reading-per-addition rule).")
            return
        if (self.total_drops + n) * self.phys.DROP_ML > self.phys.BURETTE_CAPACITY_ML:
            self.error(f"Burette capacity ({self.phys.BURETTE_CAPACITY_ML:.0f} mL) exceeded — refill required.")
            return

        self.play("click")
        self.total_drops += n
        self.needs_recording_before_next_add = True
        self._drop_animation(n)
        self.log_msg(f"Added {n} drop(s) of NaOH  →  total {self.total_drops} drops "
                      f"({self.total_drops * self.phys.DROP_ML:.2f} mL).", "info")
        self._refresh_all()

    def _drop_animation(self, n):
        # small falling-drop visual cue on the burette tip
        c = self.canvas
        x = 212
        for i in range(min(n, 3)):
            drop = c.create_oval(x - 3, 296 + i * 6, x + 3, 302 + i * 6, fill="#8fc7de", outline="", tags="app")
        self.after(180, lambda: c.delete("app") if False else None)  # visual only; cleared on next draw_bench()

    def act_record_reading(self):
        if not self.needs_recording_before_next_add and self.readings:
            self.warn("No new NaOH has been added since the last recorded reading.")
            return
        if not (self.meter_on and self.calibrated and self.electrode_in):
            self.error("Cannot record: meter must be ON, calibrated, with electrode immersed.")
            return
        if not self.stirrer_on:
            self.warn("Recording without stirring — value may show extra scatter (dilution not uniform).")
        vol = self.total_drops * self.phys.DROP_ML
        cond = self.phys.conductance_at(vol)
        if not self.stirrer_on:
            cond = round(cond + random.uniform(-0.15, 0.15), 2)
        self.obs_no += 1
        row = {"drops": self.total_drops, "vol": vol, "cond": cond, "stirred": self.stirrer_on}
        self.readings.append(row)
        self._push_row(row)
        self.needs_recording_before_next_add = False
        self.ok(f"Recorded: {self.total_drops} drops ({vol:.2f} mL NaOH)  →  conductance = {cond} mho.")
        self.advance_if("titrate")
        self._refresh_all()

    def _push_row(self, row):
        note = "" if row["stirred"] else "* not stirred"
        self.tree.insert("", "end", values=(self.obs_no, f"{self.phys.V1:.1f}", row["drops"],
                                              f"{row['vol']:.2f}", f"{row['cond']:.2f}", note))

    def act_reset(self):
        if not messagebox.askyesno("Reset", "Reset the entire experiment and start over?"):
            return
        self.phys = TitrationPhysics()
        self.meter_on = self.calibrated = self.hcl_taken = self.electrode_in = False
        self.stirrer_on = self.initial_recorded = self.burette_filled = self.valve_open = False
        self.current_step = 0
        self.total_drops = 0
        self.needs_recording_before_next_add = False
        self.readings.clear()
        self.obs_no = 0
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.log.delete("1.0", "end")
        self._style_axes()
        self.canvas_fig.draw()
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", "Experiment reset. Follow the Virtual Bench steps again.")
        self.result_text.config(state="disabled")
        self.log_msg("Experiment reset. All apparatus returned to the OFF/empty state.", "info")
        self._refresh_all()

    # ==================================================================
    #  GRAPH + RESULT
    # ==================================================================
    def act_plot_graph(self):
        if len(self.readings) < 6:
            self.error("Not enough data points to plot a reliable graph. "
                       "Continue titrating (collect readings well before AND after the "
                       "equivalence point) before plotting.")
            return

        vols = np.array([r["vol"] for r in self.readings])
        conds = np.array([r["cond"] for r in self.readings])
        min_idx = int(np.argmin(conds))

        if min_idx < 2 or min_idx > len(vols) - 3:
            self.error("The minimum (equivalence) point is not clearly bracketed yet. "
                       "Add a few more NaOH increments before and/or after the minimum, "
                       "then plot again.")
            return

        pre_v, pre_c = vols[:min_idx + 1], conds[:min_idx + 1]
        post_v, post_c = vols[min_idx:], conds[min_idx:]

        m1, b1 = np.polyfit(pre_v, pre_c, 1)
        m2, b2 = np.polyfit(post_v, post_c, 1)

        if abs(m1 - m2) < 1e-6:
            self.error("The two branches appear parallel — collect a wider spread of points "
                       "on each side of the equivalence point and try again.")
            return

        v_eq = (b2 - b1) / (m1 - m2)
        l_eq = m1 * v_eq + b1
        self._last_v_eq = v_eq

        self._style_axes()
        self.ax.scatter(vols, conds, color="#39c0ff", zorder=5, label="Observed readings")
        xs1 = np.linspace(min(pre_v), max(v_eq, max(pre_v)), 50)
        xs2 = np.linspace(min(v_eq, min(post_v)), max(post_v), 50)
        self.ax.plot(xs1, m1 * xs1 + b1, color="#ff9f43", linewidth=2, label="Branch 1 (H+ → Na+)")
        self.ax.plot(xs2, m2 * xs2 + b2, color="#33d17a", linewidth=2, label="Branch 2 (excess NaOH)")
        self.ax.axvline(v_eq, color="#ff5c5c", linestyle=":", linewidth=1.5)
        self.ax.scatter([v_eq], [l_eq], color="#ff5c5c", s=90, zorder=6, marker="X",
                          label=f"Equivalence pt.  V2 = {v_eq:.2f} mL")
        self.ax.legend(facecolor="#16212e", edgecolor="#3a4c5e", labelcolor=self.TEXT, fontsize=8)
        self.canvas_fig.draw()

        self.ok(f"Graph plotted. Equivalence point located at V2 ≈ {v_eq:.2f} mL of NaOH.")
        self.advance_if("graph")
        self.nb.select(self.tab_graph)

    def act_calculate(self):
        if not hasattr(self, "_last_v_eq"):
            self.error("Plot the graph first to determine V2 (volume of NaOH at the equivalence point).")
            return
        V1 = self.phys.V1
        S2 = self.phys.N2
        V2 = self._last_v_eq
        S1 = (V2 * S2) / V1
        actual = self.phys.N1_true
        err_pct = abs(S1 - actual) / actual * 100

        report = (
            "LAW OF EQUIVALENCE\n"
            "   V1 x S1  =  V2 x S2\n\n"
            f"   V1 (vol. of HCl)          = {V1:.2f} mL\n"
            f"   S2 (strength of NaOH)     = {S2:.3f} N   (N/2)\n"
            f"   V2 (from graph)           = {V2:.2f} mL\n"
            "   ---------------------------------------\n"
            f"   S1 = (V2 x S2) / V1       = {S1:.4f} N\n\n"
            f"   ≈ N / {1/S1:.1f}\n\n"
            "----------------------------------------------\n"
            " Bench-reference check (for feedback only):\n"
            f"   Simulator's set strength   = {actual:.4f} N\n"
            f"   Your calculated strength   = {S1:.4f} N\n"
            f"   Deviation                  = {err_pct:.2f} %\n"
            f"   {'✔ Good agreement (<5%).' if err_pct < 5 else '⚠ Re-check drop spacing / stirring for accuracy.'}\n"
        )
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", report)
        self.result_text.config(state="disabled")
        self.ok(f"Strength of HCl calculated: {S1:.4f} N  (deviation {err_pct:.2f}% from set value).")
        self.advance_if("calculate")


# ============================================================================
#  ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    random.seed()
    app = LabSimulator()
    app.mainloop()
