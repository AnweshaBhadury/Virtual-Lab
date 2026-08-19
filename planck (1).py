"""
PLANCK'S CONSTANT - VIRTUAL PHYSICS LAB
Photoelectric Effect Method
Python 3.14+

No external packages required.

Features:
- Professional laboratory-style interface
- Mercury lamp
- Optical filters
- Photoelectric cell
- Variable DC power supply
- Voltmeter
- Microammeter
- Step-by-step procedure
- Incorrect-operation detection
- Switch/click feedback
- Live photocurrent simulation
- Automatic I-V scan
- I-V graph
- Stopping potential vs frequency graph
- Photon energy vs frequency graph
- Practical-book observation table
- Automatic calculation of Planck's constant
- Work-function calculation
- Percentage error
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random


# ============================================================
# PHYSICAL CONSTANTS
# ============================================================

E_CHARGE = 1.602176634e-19       # Coulomb
H_TRUE = 6.62607015e-34          # J s
C_LIGHT = 299792458.0            # m/s

# Assumed photocathode work function
WORK_FUNCTION_EV = 2.20

# Simulated measurement uncertainty
MEASUREMENT_ERROR = 0.004


# ============================================================
# FILTER DATA
# ============================================================

FILTERS = [
    ("UV", 365, "#b78cff"),
    ("Violet", 405, "#8c78ff"),
    ("Blue", 436, "#579dff"),
    ("Green", 546, "#4ee38a"),
    ("Yellow", 578, "#ffd84d"),
]


# ============================================================
# UI COLORS
# ============================================================

BG = "#10171d"
PANEL = "#1b2730"
DARK = "#0b1116"
BENCH = "#18252d"

TEXT = "#eaf2f5"
MUTED = "#8fa2ad"

CYAN = "#39d0ff"
GREEN = "#4ee38a"
YELLOW = "#ffd166"
RED = "#ff6262"
WHITE = "#ffffff"


# ============================================================
# PHYSICS FUNCTIONS
# ============================================================

def calculate_frequency(wavelength_nm):
    """
    Calculate frequency:
        ν = c / λ
    """
    wavelength_m = wavelength_nm * 1e-9
    return C_LIGHT / wavelength_m


def calculate_stopping_potential(wavelength_nm):
    """
    Einstein photoelectric equation:

        eVs = hf - phi

    Work function is given in eV.
    """

    frequency = calculate_frequency(wavelength_nm)

    photon_energy_ev = (
        H_TRUE * frequency / E_CHARGE
    )

    stopping_voltage = (
        photon_energy_ev - WORK_FUNCTION_EV
    )

    return stopping_voltage


# ============================================================
# MAIN APPLICATION
# ============================================================

class PlanckLab(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title(
            "Planck's Constant - Virtual Physics Laboratory"
        )

        self.geometry("1450x900")
        self.minsize(1150, 720)

        self.configure(bg=BG)

        # ----------------------------------------------------
        # Experiment state
        # ----------------------------------------------------

        self.power_on = False
        self.lamp_on = False
        self.cell_connected = False

        self.selected_filter = 2

        self.voltage = 0.0
        self.current = 0.0

        self.procedure_step = 0

        self.running_scan = False
        self.scan_voltage = 3.0

        # Observation data
        self.measurements = []

        # I-V graph data
        self.iv_voltage = []
        self.iv_current = []

        # ----------------------------------------------------
        # Tk variables
        # ----------------------------------------------------

        self.status_var = tk.StringVar(
            value="SYSTEM READY - Begin the practical."
        )

        self.voltage_var = tk.StringVar(
            value="+0.000 V"
        )

        self.current_var = tk.StringVar(
            value="0.00 µA"
        )

        self.h_result_var = tk.StringVar(
            value="Not calculated"
        )

        self.phi_result_var = tk.StringVar(
            value="Not calculated"
        )

        self.error_result_var = tk.StringVar(
            value="Not calculated"
        )

        # Build interface
        self.build_header()
        self.build_main()
        self.build_status_bar()

        self.refresh_all()

        self.bind(
            "<Configure>",
            self.on_resize
        )


    # ========================================================
    # HEADER
    # ========================================================

    def build_header(self):

        header = tk.Frame(
            self,
            bg=DARK,
            height=75
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="PLANCK'S CONSTANT",
            bg=DARK,
            fg=CYAN,
            font=("Segoe UI", 24, "bold")
        ).pack(
            side="left",
            padx=25
        )

        tk.Label(
            header,
            text=(
                "PHOTOELECTRIC EFFECT  •  "
                "VIRTUAL PHYSICS LABORATORY"
            ),
            bg=DARK,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(
            side="left"
        )

        self.power_indicator = tk.Label(
            header,
            text="● POWER OFF",
            bg=DARK,
            fg=RED,
            font=("Segoe UI", 11, "bold")
        )

        self.power_indicator.pack(
            side="right",
            padx=30
        )


    # ========================================================
    # MAIN LAYOUT
    # ========================================================

    def build_main(self):

        main = tk.Frame(
            self,
            bg=BG
        )

        main.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=10
        )

        # ----------------------------------------------------
        # LEFT
        # ----------------------------------------------------

        left = tk.Frame(
            main,
            bg=BG
        )

        left.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # RIGHT
        # ----------------------------------------------------

        right = tk.Frame(
            main,
            bg=BG,
            width=420
        )

        right.pack(
            side="right",
            fill="y",
            padx=(10, 0)
        )

        right.pack_propagate(False)

        # ----------------------------------------------------
        # Apparatus
        # ----------------------------------------------------

        apparatus_frame = tk.LabelFrame(
            left,
            text="  ENGINEERING LAB APPARATUS  ",
            bg=PANEL,
            fg=CYAN,
            font=("Segoe UI", 11, "bold"),
            bd=1,
            relief="solid"
        )

        apparatus_frame.pack(
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            apparatus_frame,
            bg="#0c141a",
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        # Right panels
        self.build_control_panel(right)
        self.build_procedure_panel(right)
        self.build_instrument_panel(right)


    # ========================================================
    # BUTTON HELPER
    # ========================================================

    def create_button(
        self,
        parent,
        text,
        command,
        bg="#263640"
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=WHITE,
            activebackground="#405967",
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            pady=7
        )


    # ========================================================
    # CONTROL PANEL
    # ========================================================

    def build_control_panel(self, parent):

        frame = tk.LabelFrame(
            parent,
            text="  CONTROL PANEL  ",
            bg=PANEL,
            fg=CYAN,
            font=("Segoe UI", 10, "bold"),
            bd=1,
            relief="solid"
        )

        frame.pack(
            fill="x",
            pady=(0, 8)
        )

        # Main power
        self.power_button = self.create_button(
            frame,
            "⏻  MAIN POWER",
            self.toggle_power
        )

        self.power_button.pack(
            fill="x",
            padx=10,
            pady=8
        )

        # Lamp
        self.lamp_button = self.create_button(
            frame,
            "💡  LIGHT SOURCE OFF",
            self.toggle_lamp
        )

        self.lamp_button.pack(
            fill="x",
            padx=10,
            pady=4
        )

        # Cell
        self.cell_button = self.create_button(
            frame,
            "🔌  CONNECT PHOTO CELL",
            self.toggle_cell
        )

        self.cell_button.pack(
            fill="x",
            padx=10,
            pady=4
        )

        # Filter
        tk.Label(
            frame,
            text="Optical Filter / Wavelength",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=10,
            pady=(8, 2)
        )

        self.filter_combo = ttk.Combobox(
            frame,
            state="readonly",
            values=[
                f"{name} - {wavelength} nm"
                for name, wavelength, _ in FILTERS
            ]
        )

        self.filter_combo.current(
            self.selected_filter
        )

        self.filter_combo.pack(
            fill="x",
            padx=10,
            pady=4
        )

        self.filter_combo.bind(
            "<<ComboboxSelected>>",
            self.change_filter
        )

        # Voltage
        tk.Label(
            frame,
            text="Variable / Retarding Voltage",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=10,
            pady=(8, 0)
        )

        self.voltage_scale = tk.Scale(
            frame,
            from_=-4,
            to=4,
            resolution=0.01,
            orient="horizontal",
            bg=PANEL,
            fg=TEXT,
            troughcolor=DARK,
            highlightthickness=0,
            showvalue=False,
            command=self.voltage_changed
        )

        self.voltage_scale.pack(
            fill="x",
            padx=10
        )

        # Record
        self.record_button = self.create_button(
            frame,
            "●  RECORD STOPPING POTENTIAL",
            self.record_measurement,
            "#245d48"
        )

        self.record_button.pack(
            fill="x",
            padx=10,
            pady=(8, 4)
        )

        # I-V scan
        self.scan_button = self.create_button(
            frame,
            "▶  AUTOMATIC I-V SCAN",
            self.start_scan,
            "#24506a"
        )

        self.scan_button.pack(
            fill="x",
            padx=10,
            pady=4
        )

        # Results
        self.results_button = self.create_button(
            frame,
            "📊  OBSERVATION & GRAPHS",
            self.open_results,
            "#294554"
        )

        self.results_button.pack(
            fill="x",
            padx=10,
            pady=4
        )

        # Reset
        self.reset_button = self.create_button(
            frame,
            "↻  RESET EXPERIMENT",
            self.reset_experiment,
            "#55383a"
        )

        self.reset_button.pack(
            fill="x",
            padx=10,
            pady=(4, 10)
        )


    # ========================================================
    # PROCEDURE PANEL
    # ========================================================

    def build_procedure_panel(self, parent):

        frame = tk.LabelFrame(
            parent,
            text="  STEP-BY-STEP PROCEDURE  ",
            bg=PANEL,
            fg=CYAN,
            font=("Segoe UI", 10, "bold"),
            bd=1,
            relief="solid"
        )

        frame.pack(
            fill="both",
            expand=True,
            pady=8
        )

        self.procedure_text = tk.Text(
            frame,
            bg="#0f171d",
            fg=TEXT,
            font=("Segoe UI", 9),
            wrap="word",
            relief="flat",
            padx=10,
            pady=10
        )

        self.procedure_text.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        self.procedure_text.configure(
            state="disabled"
        )

        navigation = tk.Frame(
            frame,
            bg=PANEL
        )

        navigation.pack(
            fill="x",
            padx=8,
            pady=(0, 8)
        )

        tk.Button(
            navigation,
            text="← PREVIOUS",
            command=self.previous_step,
            bg="#263640",
            fg=WHITE,
            relief="flat"
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=2
        )

        tk.Button(
            navigation,
            text="NEXT →",
            command=self.next_step,
            bg="#24506a",
            fg=WHITE,
            relief="flat"
        ).pack(
            side="right",
            fill="x",
            expand=True,
            padx=2
        )


    # ========================================================
    # INSTRUMENT PANEL
    # ========================================================

    def build_instrument_panel(self, parent):

        frame = tk.LabelFrame(
            parent,
            text="  DIGITAL INSTRUMENTS  ",
            bg=PANEL,
            fg=CYAN,
            font=("Segoe UI", 10, "bold"),
            bd=1,
            relief="solid"
        )

        frame.pack(
            fill="x",
            pady=(0, 8)
        )

        self.create_meter(
            frame,
            "PRECISION VOLTMETER",
            self.voltage_var,
            GREEN
        )

        self.create_meter(
            frame,
            "PHOTO CURRENT MICROAMMETER",
            self.current_var,
            YELLOW
        )

        self.instrument_info = tk.Label(
            frame,
            text="",
            bg=PANEL,
            fg=MUTED,
            justify="left",
            font=("Segoe UI", 9)
        )

        self.instrument_info.pack(
            anchor="w",
            padx=10,
            pady=7
        )


    def create_meter(
        self,
        parent,
        title,
        variable,
        color
    ):

        box = tk.Frame(
            parent,
            bg="#080d11",
            bd=2,
            relief="sunken"
        )

        box.pack(
            fill="x",
            padx=8,
            pady=5
        )

        tk.Label(
            box,
            text=title,
            bg="#080d11",
            fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(
            anchor="w",
            padx=8,
            pady=(5, 0)
        )

        tk.Label(
            box,
            textvariable=variable,
            bg="#080d11",
            fg=color,
            font=("Consolas", 20, "bold")
        ).pack(
            pady=(0, 6)
        )


    # ========================================================
    # STATUS BAR
    # ========================================================

    def build_status_bar(self):

        bar = tk.Frame(
            self,
            bg=DARK,
            height=45
        )

        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Label(
            bar,
            text="STATUS:",
            bg=DARK,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(
            side="left",
            padx=(15, 5)
        )

        tk.Label(
            bar,
            textvariable=self.status_var,
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 9)
        ).pack(
            side="left"
        )


    # ========================================================
    # SOUND
    # ========================================================

    def click_sound(self):

        try:
            self.bell()
        except tk.TclError:
            pass


    # ========================================================
    # ERROR MESSAGE
    # ========================================================

    def show_error(
        self,
        title,
        message
    ):

        self.click_sound()

        self.status_var.set(
            "⚠ " + message.split("\n")[0]
        )

        messagebox.showwarning(
            title,
            message,
            parent=self
        )


    # ========================================================
    # POWER
    # ========================================================

    def toggle_power(self):

        self.click_sound()

        self.power_on = not self.power_on

        if self.power_on:

            self.power_indicator.config(
                text="● POWER ON",
                fg=GREEN
            )

            self.power_button.config(
                text="⏻  MAIN POWER - ON",
                bg="#245d48"
            )

            self.status_var.set(
                "Main laboratory power supply switched ON."
            )

        else:

            self.power_indicator.config(
                text="● POWER OFF",
                fg=RED
            )

            self.power_button.config(
                text="⏻  MAIN POWER",
                bg="#263640"
            )

            # Safety shutdown
            self.lamp_on = False
            self.cell_connected = False

            self.lamp_button.config(
                text="💡  LIGHT SOURCE OFF",
                bg="#263640"
            )

            self.cell_button.config(
                text="🔌  CONNECT PHOTO CELL",
                bg="#263640"
            )

            self.status_var.set(
                "Main power OFF - circuit safely isolated."
            )

        self.refresh_all()


    # ========================================================
    # LAMP
    # ========================================================

    def toggle_lamp(self):

        self.click_sound()

        if not self.power_on:

            self.show_error(
                "INCORRECT OPERATION",
                "MAIN POWER is OFF.\n\n"
                "First switch ON MAIN POWER."
            )

            return

        self.lamp_on = not self.lamp_on

        if self.lamp_on:

            self.lamp_button.config(
                text="💡  LIGHT SOURCE - ON",
                bg="#6a5823"
            )

            self.status_var.set(
                "Mercury lamp switched ON."
            )

        else:

            self.lamp_button.config(
                text="💡  LIGHT SOURCE OFF",
                bg="#263640"
            )

            self.status_var.set(
                "Light source switched OFF."
            )

        self.refresh_all()


    # ========================================================
    # PHOTO CELL
    # ========================================================

    def toggle_cell(self):

        self.click_sound()

        if not self.power_on:

            self.show_error(
                "CIRCUIT ERROR",
                "MAIN POWER is OFF.\n\n"
                "Switch ON MAIN POWER first."
            )

            return

        if not self.lamp_on:

            self.show_error(
                "MEASUREMENT ERROR",
                "LIGHT SOURCE is OFF.\n\n"
                "Switch ON the mercury lamp first."
            )

            return

        self.cell_connected = not self.cell_connected

        if self.cell_connected:

            self.cell_button.config(
                text="🔌  PHOTO CELL - CONNECTED",
                bg="#245d48"
            )

            self.status_var.set(
                "Photoelectric cell connected."
            )

        else:

            self.cell_button.config(
                text="🔌  CONNECT PHOTO CELL",
                bg="#263640"
            )

            self.status_var.set(
                "Photoelectric cell disconnected."
            )

        self.refresh_all()


    # ========================================================
    # FILTER
    # ========================================================

    def change_filter(self, event=None):

        self.click_sound()

        self.selected_filter = (
            self.filter_combo.current()
        )

        name, wavelength, _ = FILTERS[
            self.selected_filter
        ]

        self.status_var.set(
            f"{name} filter selected - "
            f"{wavelength} nm."
        )

        self.refresh_all()


    # ========================================================
    # VOLTAGE
    # ========================================================

    def voltage_changed(
        self,
        value
    ):

        self.voltage = float(value)

        self.update_current()

        self.update_instrument_info()

        self.draw_apparatus()


    # ========================================================
    # CURRENT CALCULATION
    # ========================================================

    def update_current(self):

        if not (
            self.power_on
            and self.lamp_on
            and self.cell_connected
        ):

            self.current = 0.0

        else:

            _, wavelength, _ = FILTERS[
                self.selected_filter
            ]

            stopping_voltage = (
                calculate_stopping_potential(
                    wavelength
                )
            )

            # At retarding potential -Vs
            # the photocurrent becomes zero.

            if self.voltage <= -stopping_voltage:

                self.current = 0.0

            else:

                available_voltage = (
                    self.voltage
                    + stopping_voltage
                )

                available_voltage = max(
                    available_voltage,
                    0.0
                )

                # Realistic saturation-style current
                self.current = (
                    8.5
                    * (
                        1
                        - math.exp(
                            -available_voltage
                            / 0.65
                        )
                    )
                )

                # Measurement noise
                self.current += random.uniform(
                    -0.025,
                    0.025
                )

                self.current = max(
                    self.current,
                    0.0
                )

        self.voltage_var.set(
            f"{self.voltage:+.3f} V"
        )

        self.current_var.set(
            f"{self.current:.2f} µA"
        )


    # ========================================================
    # RECORD STOPPING POTENTIAL
    # ========================================================

    def record_measurement(self):

        self.click_sound()

        # Safety checks
        if not self.power_on:

            self.show_error(
                "OPERATION NOT ALLOWED",
                "MAIN POWER must be ON."
            )

            return

        if not self.lamp_on:

            self.show_error(
                "OPERATION NOT ALLOWED",
                "LIGHT SOURCE must be ON."
            )

            return

        if not self.cell_connected:

            self.show_error(
                "OPERATION NOT ALLOWED",
                "PHOTOELECTRIC CELL must be connected."
            )

            return

        _, wavelength, _ = FILTERS[
            self.selected_filter
        ]

        # Current must be approximately zero
        if self.current > 0.08:

            self.show_error(
                "STOPPING POTENTIAL NOT REACHED",
                "Photocurrent is still flowing.\n\n"
                "Increase the negative/retarding voltage "
                "until the microammeter reads approximately 0 µA."
            )

            return

        # Prevent duplicate observation
        for row in self.measurements:

            if row["wavelength"] == wavelength:

                self.status_var.set(
                    f"{wavelength} nm reading already recorded."
                )

                return

        # Simulated measurement
        measured_voltage = (
            calculate_stopping_potential(
                wavelength
            )
            + random.uniform(
                -MEASUREMENT_ERROR,
                MEASUREMENT_ERROR
            )
        )

        self.measurements.append(
            {
                "wavelength": wavelength,
                "frequency": calculate_frequency(
                    wavelength
                ),
                "stopping_voltage": measured_voltage
            }
        )

        # Sort by frequency
        self.measurements.sort(
            key=lambda row: row["frequency"]
        )

        self.status_var.set(
            f"Reading recorded: "
            f"{wavelength} nm, "
            f"Vs = {measured_voltage:.3f} V"
        )


    # ========================================================
    # AUTOMATIC I-V SCAN
    # ========================================================

    def start_scan(self):

        self.click_sound()

        if not (
            self.power_on
            and self.lamp_on
            and self.cell_connected
        ):

            self.show_error(
                "SCAN CANNOT START",
                "Complete the laboratory sequence:\n\n"
                "1. MAIN POWER ON\n"
                "2. LIGHT SOURCE ON\n"
                "3. PHOTO CELL CONNECTED"
            )

            return

        if self.running_scan:
            return

        self.running_scan = True

        self.iv_voltage.clear()
        self.iv_current.clear()

        self.scan_voltage = 3.0

        self.scan_button.config(
            text="⏳  I-V SCAN RUNNING",
            bg="#6a5823"
        )

        self.status_var.set(
            "Automatic I-V scan running..."
        )

        self.run_scan_step()


    def run_scan_step(self):

        if not self.running_scan:
            return

        if self.scan_voltage < -3.0:

            self.running_scan = False

            self.scan_button.config(
                text="▶  AUTOMATIC I-V SCAN",
                bg="#24506a"
            )

            self.status_var.set(
                "I-V scan completed."
            )

            return

        self.voltage_scale.set(
            round(
                self.scan_voltage,
                2
            )
        )

        self.update_current()

        self.iv_voltage.append(
            self.voltage
        )

        self.iv_current.append(
            self.current
        )

        self.scan_voltage -= 0.08

        self.after(
            30,
            self.run_scan_step
        )


    # ========================================================
    # PROCEDURE
    # ========================================================

    def update_procedure(self):

        procedures = [

            (
                "STEP 1 - CHECK APPARATUS",

                "Verify the mercury lamp, optical filter, "
                "photoelectric cell, DC supply, voltmeter "
                "and microammeter.\n\n"
                "Keep MAIN POWER OFF before starting."
            ),

            (
                "STEP 2 - SWITCH ON MAIN POWER",

                "Press MAIN POWER.\n\n"
                "The laboratory electrical supply is now active."
            ),

            (
                "STEP 3 - SWITCH ON LIGHT SOURCE",

                "Switch ON the mercury lamp.\n\n"
                "The selected monochromatic light will illuminate "
                "the photoelectric cell."
            ),

            (
                "STEP 4 - CONNECT PHOTO CELL",

                "Connect the photoelectric cell to the measuring "
                "circuit.\n\n"
                "The microammeter will now respond to light."
            ),

            (
                "STEP 5 - SELECT WAVELENGTH",

                "Select one optical filter.\n\n"
                "Record wavelength λ.\n\n"
                "Calculate frequency using:\n"
                "ν = c / λ"
            ),

            (
                "STEP 6 - FIND STOPPING POTENTIAL",

                "Slowly move the voltage control toward the "
                "negative/retarding region.\n\n"
                "Continue until the photocurrent becomes "
                "approximately zero."
            ),

            (
                "STEP 7 - RECORD READING",

                "When current ≈ 0 µA, press RECORD STOPPING "
                "POTENTIAL.\n\n"
                "Repeat the procedure for different wavelengths."
            ),

            (
                "STEP 8 - GRAPHICAL ANALYSIS",

                "Plot stopping potential Vs against frequency ν.\n\n"
                "Equation:\n"
                "Vs = (h/e)ν - φ/e\n\n"
                "Therefore:\n"
                "h = e × slope"
            )
        ]

        title, body = procedures[
            self.procedure_step
        ]

        text = (
            f"PROCEDURE "
            f"{self.procedure_step + 1} / 8\n"
            + "═" * 38
            + "\n\n"
            + title
            + "\n\n"
            + body
        )

        self.procedure_text.configure(
            state="normal"
        )

        self.procedure_text.delete(
            "1.0",
            "end"
        )

        self.procedure_text.insert(
            "1.0",
            text
        )

        self.procedure_text.configure(
            state="disabled"
        )


    def next_step(self):

        if self.procedure_step < 7:

            self.procedure_step += 1

            self.click_sound()

            self.update_procedure()


    def previous_step(self):

        if self.procedure_step > 0:

            self.procedure_step -= 1

            self.click_sound()

            self.update_procedure()


    # ========================================================
    # LINEAR REGRESSION
    # ========================================================

    @staticmethod
    def linear_regression(
        x_values,
        y_values
    ):

        n = len(x_values)

        if n < 2:
            return 0.0, 0.0

        x_mean = (
            sum(x_values) / n
        )

        y_mean = (
            sum(y_values) / n
        )

        denominator = sum(
            (
                x - x_mean
            ) ** 2
            for x in x_values
        )

        if denominator == 0:
            return 0.0, y_mean

        numerator = sum(
            (
                x - x_mean
            )
            * (
                y - y_mean
            )
            for x, y in zip(
                x_values,
                y_values
            )
        )

        slope = (
            numerator
            / denominator
        )

        intercept = (
            y_mean
            - slope * x_mean
        )

        return slope, intercept


    # ========================================================
    # ANALYSIS
    # ========================================================

    def calculate_results(self):

        if len(self.measurements) < 2:
            return None

        x_values = [
            row["frequency"]
            for row in self.measurements
        ]

        y_values = [
            row["stopping_voltage"]
            for row in self.measurements
        ]

        slope, intercept = (
            self.linear_regression(
                x_values,
                y_values
            )
        )

        h_experimental = (
            E_CHARGE
            * slope
        )

        work_function = (
            -intercept
        )

        percentage_error = (
            abs(
                h_experimental
                - H_TRUE
            )
            / H_TRUE
            * 100
        )

        return (
            slope,
            intercept,
            h_experimental,
            work_function,
            percentage_error
        )


    # ========================================================
    # RESULTS WINDOW
    # ========================================================

    def open_results(self):

        self.click_sound()

        window = tk.Toplevel(
            self
        )

        window.title(
            "Planck's Constant - Practical Record"
        )

        window.geometry(
            "1250x800"
        )

        window.configure(
            bg=BG
        )

        tk.Label(
            window,
            text=(
                "OBSERVATION TABLE & "
                "GRAPHICAL ANALYSIS"
            ),
            bg=BG,
            fg=CYAN,
            font=("Segoe UI", 18, "bold")
        ).pack(
            pady=12
        )

        notebook = ttk.Notebook(
            window
        )

        notebook.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=8
        )

        observation_tab = tk.Frame(
            notebook,
            bg=PANEL
        )

        iv_tab = tk.Frame(
            notebook,
            bg=PANEL
        )

        planck_tab = tk.Frame(
            notebook,
            bg=PANEL
        )

        energy_tab = tk.Frame(
            notebook,
            bg=PANEL
        )

        result_tab = tk.Frame(
            notebook,
            bg=PANEL
        )

        notebook.add(
            observation_tab,
            text="Observation Table"
        )

        notebook.add(
            iv_tab,
            text="I-V Graph"
        )

        notebook.add(
            planck_tab,
            text="Vs vs Frequency"
        )

        notebook.add(
            energy_tab,
            text="Photon Energy Graph"
        )

        notebook.add(
            result_tab,
            text="Final Result"
        )

        self.build_observation_table(
            observation_tab
        )

        self.build_iv_graph(
            iv_tab
        )

        self.build_planck_graph(
            planck_tab
        )

        self.build_energy_graph(
            energy_tab
        )

        self.build_final_result(
            result_tab
        )


    # ========================================================
    # OBSERVATION TABLE
    # ========================================================

    def build_observation_table(
        self,
        parent
    ):

        tk.Label(
            parent,
            text=(
                "OBSERVATION TABLE - "
                "PRACTICAL BOOK"
            ),
            bg=PANEL,
            fg=WHITE,
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 3)
        )

        tk.Label(
            parent,
            text=(
                "Experiment: Determination of "
                "Planck's constant using "
                "photoelectric effect"
            ),
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=15
        )

        columns = (
            "serial",
            "wavelength",
            "frequency",
            "stopping",
            "energy"
        )

        table = ttk.Treeview(
            parent,
            columns=columns,
            show="headings"
        )

        headings = {

            "serial":
                "S.No.",

            "wavelength":
                "Wavelength λ (nm)",

            "frequency":
                "Frequency ν (Hz)",

            "stopping":
                "Stopping Potential Vs (V)",

            "energy":
                "Photon Energy hν/e (eV)"
        }

        widths = {

            "serial": 70,

            "wavelength": 170,

            "frequency": 220,

            "stopping": 230,

            "energy": 210
        }

        for column in columns:

            table.heading(
                column,
                text=headings[column]
            )

            table.column(
                column,
                width=widths[column],
                anchor="center"
            )

        table.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=12
        )

        for index, row in enumerate(
            self.measurements,
            start=1
        ):

            photon_energy = (
                H_TRUE
                * row["frequency"]
                / E_CHARGE
            )

            table.insert(
                "",
                "end",
                values=(
                    index,
                    row["wavelength"],
                    f"{row['frequency']:.4e}",
                    f"{row['stopping_voltage']:.4f}",
                    f"{photon_energy:.4f}"
                )
            )

        tk.Label(
            parent,
            text=(
                "Observation rule: stopping potential "
                "is recorded when photocurrent is approximately zero."
            ),
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=15,
            pady=7
        )


    # ========================================================
    # GRAPH ENGINE
    # ========================================================

    @staticmethod
    def graph_format(value):

        if (
            abs(value) >= 100000
            or (
                0 < abs(value) < 0.001
            )
        ):

            return f"{value:.2e}"

        return f"{value:.3f}"


    def draw_graph(
        self,
        canvas,
        x_values,
        y_values,
        title,
        x_label,
        y_label,
        point_color=YELLOW,
        line_color=CYAN,
        regression=False
    ):

        canvas.delete("all")

        width = max(
            canvas.winfo_width(),
            900
        )

        height = max(
            canvas.winfo_height(),
            520
        )

        canvas.create_rectangle(
            0,
            0,
            width,
            height,
            fill="#101820",
            outline=""
        )

        canvas.create_text(
            width / 2,
            30,
            text=title,
            fill=WHITE,
            font=("Segoe UI", 14, "bold")
        )

        if not x_values:

            canvas.create_text(
                width / 2,
                height / 2,
                text="No experimental data available.",
                fill=MUTED,
                font=("Segoe UI", 12)
            )

            return

        left = 90
        right = 45
        top = 65
        bottom = 80

        graph_width = (
            width
            - left
            - right
        )

        graph_height = (
            height
            - top
            - bottom
        )

        xmin = min(x_values)
        xmax = max(x_values)

        ymin = min(y_values)
        ymax = max(y_values)

        if xmin == xmax:
            xmin -= 1
            xmax += 1

        if ymin == ymax:
            ymin -= 1
            ymax += 1

        xpad = (
            xmax - xmin
        ) * 0.08

        ypad = (
            ymax - ymin
        ) * 0.12

        xmin -= xpad
        xmax += xpad

        ymin -= ypad
        ymax += ypad

        def sx(x):

            return (
                left
                + (
                    x - xmin
                )
                / (
                    xmax - xmin
                )
                * graph_width
            )

        def sy(y):

            return (
                top
                + graph_height
                - (
                    y - ymin
                )
                / (
                    ymax - ymin
                )
                * graph_height
            )

        # Grid
        for i in range(11):

            gx = (
                left
                + i
                * graph_width
                / 10
            )

            gy = (
                top
                + i
                * graph_height
                / 10
            )

            canvas.create_line(
                gx,
                top,
                gx,
                top + graph_height,
                fill="#263740"
            )

            canvas.create_line(
                left,
                gy,
                left + graph_width,
                gy,
                fill="#263740"
            )

        # Axes
        canvas.create_line(
            left,
            top + graph_height,
            left + graph_width,
            top + graph_height,
            fill="#9aaab2",
            width=2
        )

        canvas.create_line(
            left,
            top,
            left,
            top + graph_height,
            fill="#9aaab2",
            width=2
        )

        # Tick values
        for i in range(6):

            xv = (
                xmin
                + i
                * (
                    xmax - xmin
                )
                / 5
            )

            yv = (
                ymin
                + i
                * (
                    ymax - ymin
                )
                / 5
            )

            canvas.create_text(
                sx(xv),
                top + graph_height + 20,
                text=self.graph_format(xv),
                fill=MUTED,
                font=("Consolas", 8)
            )

            canvas.create_text(
                left - 30,
                sy(yv),
                text=self.graph_format(yv),
                fill=MUTED,
                font=("Consolas", 8)
            )

        # Labels
        canvas.create_text(
            left + graph_width / 2,
            height - 25,
            text=x_label,
            fill=WHITE,
            font=("Segoe UI", 10)
        )

        canvas.create_text(
            20,
            top + graph_height / 2,
            text=y_label,
            fill=WHITE,
            font=("Segoe UI", 10),
            angle=90
        )

        # Data line
        if len(x_values) >= 2:

            pairs = sorted(
                zip(
                    x_values,
                    y_values
                )
            )

            points = []

            for x, y in pairs:

                points.extend(
                    (
                        sx(x),
                        sy(y)
                    )
                )

            canvas.create_line(
                *points,
                fill=line_color,
                width=2,
                smooth=True
            )

        # Data points
        for x, y in zip(
            x_values,
            y_values
        ):

            px = sx(x)
            py = sy(y)

            canvas.create_oval(
                px - 5,
                py - 5,
                px + 5,
                py + 5,
                fill=point_color,
                outline=WHITE
            )

        # Regression
        if (
            regression
            and len(x_values) >= 2
        ):

            slope, intercept = (
                self.linear_regression(
                    x_values,
                    y_values
                )
            )

            x1 = xmin
            x2 = xmax

            y1 = (
                slope * x1
                + intercept
            )

            y2 = (
                slope * x2
                + intercept
            )

            canvas.create_line(
                sx(x1),
                sy(y1),
                sx(x2),
                sy(y2),
                fill=RED,
                width=2,
                dash=(8, 4)
            )

            h_experimental = (
                E_CHARGE
                * slope
            )

            canvas.create_text(
                width - 180,
                top + 35,
                text=(
                    f"Slope = {slope:.4e}\n"
                    f"h = {h_experimental:.5e} J·s"
                ),
                fill=GREEN,
                font=("Consolas", 9, "bold"),
                justify="left"
            )


    # ========================================================
    # I-V GRAPH
    # ========================================================

    def build_iv_graph(
        self,
        parent
    ):

        canvas = tk.Canvas(
            parent,
            bg="#101820",
            highlightthickness=0
        )

        canvas.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        canvas.update_idletasks()

        self.draw_graph(
            canvas,
            self.iv_voltage,
            self.iv_current,
            "PHOTOELECTRIC I-V CHARACTERISTIC",
            "Applied Voltage V (V)",
            "Photocurrent I (µA)",
            YELLOW,
            CYAN
        )


    # ========================================================
    # PLANCK GRAPH
    # ========================================================

    def build_planck_graph(
        self,
        parent
    ):

        canvas = tk.Canvas(
            parent,
            bg="#101820",
            highlightthickness=0
        )

        canvas.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        canvas.update_idletasks()

        x_values = [
            row["frequency"]
            for row in self.measurements
        ]

        y_values = [
            row["stopping_voltage"]
            for row in self.measurements
        ]

        self.draw_graph(
            canvas,
            x_values,
            y_values,
            "STOPPING POTENTIAL Vs vs FREQUENCY ν",
            "Frequency ν (Hz)",
            "Stopping Potential Vs (V)",
            YELLOW,
            GREEN,
            True
        )


    # ========================================================
    # PHOTON ENERGY GRAPH
    # ========================================================

    def build_energy_graph(
        self,
        parent
    ):

        canvas = tk.Canvas(
            parent,
            bg="#101820",
            highlightthickness=0
        )

        canvas.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        canvas.update_idletasks()

        x_values = [
            row["frequency"]
            for row in self.measurements
        ]

        y_values = [
            H_TRUE
            * row["frequency"]
            / E_CHARGE
            for row in self.measurements
        ]

        self.draw_graph(
            canvas,
            x_values,
            y_values,
            "PHOTON ENERGY hν/e vs FREQUENCY ν",
            "Frequency ν (Hz)",
            "Photon Energy hν/e (eV)",
            CYAN,
            GREEN,
            True
        )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    def build_final_result(
        self,
        parent
    ):

        container = tk.Frame(
            parent,
            bg=PANEL
        )

        container.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=30
        )

        tk.Label(
            container,
            text="EXPERIMENTAL RESULT",
            bg=PANEL,
            fg=CYAN,
            font=("Segoe UI", 21, "bold")
        ).pack(
            pady=10
        )

        results = self.calculate_results()

        if results is None:

            h_text = "Need ≥ 2 observations"
            phi_text = "Need ≥ 2 observations"
            error_text = "—"

            description = (
                "Record stopping potential for at least "
                "two different wavelengths.\n\n"
                "For a proper practical, use several wavelengths."
            )

        else:

            (
                slope,
                intercept,
                h_experimental,
                phi,
                percentage_error
            ) = results

            h_text = (
                f"{h_experimental:.5e} J·s"
            )

            phi_text = (
                f"{phi:.4f} eV"
            )

            error_text = (
                f"{percentage_error:.3f} %"
            )

            description = (
                f"Slope = {slope:.5e} V/Hz\n"
                f"Intercept = {intercept:.5f} V\n\n"
                "Using:\n"
                "h = e × slope\n\n"
                f"Experimental h = {h_experimental:.5e} J·s\n\n"
                f"Accepted h = {H_TRUE:.8e} J·s\n\n"
                f"Percentage error = {percentage_error:.3f}%\n\n"
                f"Work function = {phi:.4f} eV\n\n"
                "CONCLUSION:\n"
                "Planck's constant is determined from the "
                "slope of the Vs versus frequency graph."
            )

        self.h_result_var.set(
            h_text
        )

        self.phi_result_var.set(
            phi_text
        )

        self.error_result_var.set(
            error_text
        )

        self.result_box(
            container,
            "Experimental Planck Constant",
            self.h_result_var,
            GREEN
        )

        self.result_box(
            container,
            "Work Function",
            self.phi_result_var,
            YELLOW
        )

        self.result_box(
            container,
            "Percentage Error",
            self.error_result_var,
            CYAN
        )

        tk.Label(
            container,
            text=description,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10),
            justify="center"
        ).pack(
            pady=15
        )


    def result_box(
        self,
        parent,
        title,
        variable,
        color
    ):

        box = tk.Frame(
            parent,
            bg="#0b1217",
            bd=2,
            relief="ridge"
        )

        box.pack(
            fill="x",
            pady=6
        )

        tk.Label(
            box,
            text=title,
            bg="#0b1217",
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(
            pady=(8, 2)
        )

        tk.Label(
            box,
            textvariable=variable,
            bg="#0b1217",
            fg=color,
            font=("Consolas", 20, "bold")
        ).pack(
            pady=(0, 8)
        )


    # ========================================================
    # APPARATUS DRAWING
    # ========================================================

    def draw_apparatus(self):

        canvas = self.canvas

        canvas.delete("all")

        width = max(
            canvas.winfo_width(),
            850
        )

        height = max(
            canvas.winfo_height(),
            540
        )

        # ----------------------------------------------------
        # Laboratory bench
        # ----------------------------------------------------

        canvas.create_rectangle(
            0,
            height * 0.78,
            width,
            height,
            fill=BENCH,
            outline=""
        )

        # Rear panel
        canvas.create_rectangle(
            25,
            25,
            width - 25,
            height * 0.78,
            fill="#101a20",
            outline="#33444e",
            width=2
        )

        canvas.create_text(
            50,
            52,
            text=(
                "PHOTOELECTRIC EFFECT "
                "— EXPERIMENTAL BENCH"
            ),
            anchor="w",
            fill=CYAN,
            font=("Segoe UI", 12, "bold")
        )

        # ----------------------------------------------------
        # Mercury lamp
        # ----------------------------------------------------

        lamp_x = 135
        lamp_y = height * 0.44

        self.draw_lamp(
            canvas,
            lamp_x,
            lamp_y,
            height
        )

        # ----------------------------------------------------
        # Filter
        # ----------------------------------------------------

        filter_x = 285

        canvas.create_rectangle(
            filter_x - 25,
            lamp_y - 64,
            filter_x + 25,
            lamp_y + 64,
            fill="#303b42",
            outline="#8b999f",
            width=2
        )

        _, wavelength, filter_color = FILTERS[
            self.selected_filter
        ]

        canvas.create_rectangle(
            filter_x - 16,
            lamp_y - 48,
            filter_x + 16,
            lamp_y + 48,
            fill=filter_color,
            outline=WHITE
        )

        canvas.create_text(
            filter_x,
            lamp_y + 82,
            text=(
                "OPTICAL FILTER\n"
                f"{wavelength} nm"
            ),
            fill=TEXT,
            font=("Segoe UI", 8, "bold"),
            justify="center"
        )

        # ----------------------------------------------------
        # Light beam
        # ----------------------------------------------------

        if self.lamp_on:

            canvas.create_polygon(
                lamp_x + 55,
                lamp_y - 12,
                filter_x - 18,
                lamp_y - 18,
                filter_x - 18,
                lamp_y + 18,
                lamp_x + 55,
                lamp_y + 12,
                fill="#435c68",
                outline=""
            )

        # ----------------------------------------------------
        # Photoelectric cell
        # ----------------------------------------------------

        cell_x = width * 0.55
        cell_y = lamp_y

        self.draw_photo_cell(
            canvas,
            cell_x,
            cell_y,
            height
        )

        if self.lamp_on:

            canvas.create_polygon(
                filter_x + 20,
                lamp_y - 18,
                cell_x - 75,
                lamp_y - 23,
                cell_x - 75,
                lamp_y + 23,
                filter_x + 20,
                lamp_y + 18,
                fill="#354e5a",
                outline=""
            )

        # ----------------------------------------------------
        # DC supply
        # ----------------------------------------------------

        supply_x = width * 0.82
        supply_y = height * 0.31

        self.draw_power_supply(
            canvas,
            supply_x,
            supply_y
        )

        # ----------------------------------------------------
        # Voltmeter
        # ----------------------------------------------------

        meter_x = width * 0.82
        meter_y = height * 0.61

        self.draw_meter(
            canvas,
            meter_x - 82,
            meter_y,
            "V",
            self.voltage_var.get(),
            CYAN
        )

        # ----------------------------------------------------
        # Microammeter
        # ----------------------------------------------------

        self.draw_meter(
            canvas,
            meter_x + 82,
            meter_y,
            "µA",
            self.current_var.get(),
            YELLOW
        )

        # ----------------------------------------------------
        # Wires
        # ----------------------------------------------------

        self.draw_wire(
            canvas,
            cell_x + 75,
            cell_y - 20,
            meter_x - 140,
            meter_y - 42,
            self.cell_connected
        )

        self.draw_wire(
            canvas,
            cell_x + 75,
            cell_y + 20,
            meter_x - 20,
            meter_y + 42,
            self.cell_connected
        )


    # ========================================================
    # LAMP DRAWING
    # ========================================================

    def draw_lamp(
        self,
        canvas,
        x,
        y,
        height
    ):

        # Stand
        canvas.create_rectangle(
            x - 5,
            y + 85,
            x + 5,
            height * 0.76,
            fill="#697981",
            outline=""
        )

        canvas.create_rectangle(
            x - 58,
            height * 0.76,
            x + 58,
            height * 0.80,
            fill="#4b565d",
            outline="#8d9aa1"
        )

        # Housing
        canvas.create_polygon(
            x - 50,
            y - 42,
            x + 42,
            y - 42,
            x + 58,
            y + 16,
            x - 62,
            y + 16,
            fill="#414d54",
            outline="#909da4",
            width=2
        )

        if self.lamp_on:

            bulb_color = FILTERS[
                self.selected_filter
            ][2]

            # Glow
            for radius in (
                62,
                48,
                36
            ):

                canvas.create_oval(
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                    outline="#56646c"
                )

        else:

            bulb_color = "#59656c"

        canvas.create_oval(
            x - 25,
            y - 25,
            x + 25,
            y + 25,
            fill=bulb_color,
            outline=WHITE,
            width=2
        )

        canvas.create_text(
            x,
            y + 43,
            text="MERCURY LAMP",
            fill=TEXT,
            font=("Segoe UI", 9, "bold")
        )


    # ========================================================
    # PHOTOELECTRIC CELL DRAWING
    # ========================================================

    def draw_photo_cell(
        self,
        canvas,
        x,
        y,
        height
    ):

        # Stand
        canvas.create_rectangle(
            x - 4,
            y + 72,
            x + 4,
            height * 0.76,
            fill="#697981",
            outline=""
        )

        canvas.create_rectangle(
            x - 62,
            height * 0.76,
            x + 62,
            height * 0.80,
            fill="#4b565d",
            outline="#8d9aa1"
        )

        # Cell body
        canvas.create_rectangle(
            x - 78,
            y - 57,
            x + 78,
            y + 57,
            fill="#26353e",
            outline="#9aa7ae",
            width=2
        )

        # Window
        canvas.create_oval(
            x - 50,
            y - 42,
            x + 50,
            y + 42,
            fill="#142127",
            outline="#7d8c94",
            width=2
        )

        # Cathode
        canvas.create_arc(
            x - 34,
            y - 30,
            x + 34,
            y + 30,
            start=70,
            extent=220,
            style="arc",
            outline=YELLOW,
            width=4
        )

        # Anode
        canvas.create_line(
            x + 20,
            y - 30,
            x + 20,
            y + 30,
            fill=CYAN,
            width=4
        )

        canvas.create_text(
            x - 12,
            y - 52,
            text="K",
            fill=YELLOW,
            font=("Segoe UI", 8, "bold")
        )

        canvas.create_text(
            x + 30,
            y - 52,
            text="A",
            fill=CYAN,
            font=("Segoe UI", 8, "bold")
        )

        canvas.create_text(
            x,
            y + 78,
            text="PHOTOELECTRIC CELL",
            fill=TEXT,
            font=("Segoe UI", 9, "bold")
        )


    # ========================================================
    # POWER SUPPLY DRAWING
    # ========================================================

    def draw_power_supply(
        self,
        canvas,
        x,
        y
    ):

        canvas.create_rectangle(
            x - 92,
            y - 67,
            x + 92,
            y + 68,
            fill="#29363e",
            outline="#87959d",
            width=2
        )

        # Display
        canvas.create_rectangle(
            x - 67,
            y - 44,
            x + 67,
            y + 5,
            fill="#080d11",
            outline="#5d6c75"
        )

        canvas.create_text(
            x,
            y - 19,
            text=f"{self.voltage:+.2f} V",
            fill=GREEN,
            font=("Consolas", 18, "bold")
        )

        canvas.create_text(
            x,
            y + 28,
            text="VARIABLE DC SUPPLY",
            fill=TEXT,
            font=("Segoe UI", 8, "bold")
        )

        # Control knob
        canvas.create_oval(
            x - 23,
            y + 41,
            x + 23,
            y + 87,
            fill="#59676e",
            outline="#b0bbc0"
        )

        canvas.create_line(
            x,
            y + 64,
            x + 13,
            y + 50,
            fill=WHITE,
            width=2
        )


    # ========================================================
    # METER DRAWING
    # ========================================================

    def draw_meter(
        self,
        canvas,
        x,
        y,
        label,
        value,
        color
    ):

        canvas.create_oval(
            x - 58,
            y - 58,
            x + 58,
            y + 58,
            fill="#1d282e",
            outline="#83929a",
            width=2
        )

        # Tick marks
        for i in range(11):

            angle = math.radians(
                210 + i * 12
            )

            inner = 41
            outer = 50

            x1 = (
                x
                + inner * math.cos(angle)
            )

            y1 = (
                y
                + inner * math.sin(angle)
            )

            x2 = (
                x
                + outer * math.cos(angle)
            )

            y2 = (
                y
                + outer * math.sin(angle)
            )

            canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="#8d9ca4"
            )

        canvas.create_text(
            x,
            y - 15,
            text=label,
            fill=color,
            font=("Segoe UI", 10, "bold")
        )

        canvas.create_text(
            x,
            y + 10,
            text=value,
            fill=WHITE,
            font=("Consolas", 8, "bold")
        )


    # ========================================================
    # WIRES
    # ========================================================

    def draw_wire(
        self,
        canvas,
        x1,
        y1,
        x2,
        y2,
        connected
    ):

        if connected:

            color = "#42d9ff"

        else:

            color = "#37454d"

        middle = (
            x1 + x2
        ) / 2

        canvas.create_line(
            x1,
            y1,
            middle,
            y1,
            middle,
            y2,
            x2,
            y2,
            fill=color,
            width=3,
            smooth=True
        )


    # ========================================================
    # INSTRUMENT INFORMATION
    # ========================================================

    def update_instrument_info(self):

        _, wavelength, _ = FILTERS[
            self.selected_filter
        ]

        frequency = calculate_frequency(
            wavelength
        )

        stopping_voltage = (
            calculate_stopping_potential(
                wavelength
            )
        )

        self.instrument_info.config(
            text=(
                f"Selected λ        : {wavelength} nm\n"
                f"Frequency ν        : {frequency:.4e} Hz\n"
                f"Expected Vs        : {stopping_voltage:.3f} V"
            )
        )


    # ========================================================
    # REFRESH
    # ========================================================

    def refresh_all(self):

        self.update_current()

        self.update_instrument_info()

        self.update_procedure()

        self.draw_apparatus()


    # ========================================================
    # RESET
    # ========================================================

    def reset_experiment(self):

        self.click_sound()

        answer = messagebox.askyesno(
            "RESET EXPERIMENT",
            (
                "Are you sure you want to erase "
                "all observations and reset the laboratory?"
            ),
            parent=self
        )

        if not answer:
            return

        self.power_on = False
        self.lamp_on = False
        self.cell_connected = False

        self.voltage = 0.0
        self.current = 0.0

        self.procedure_step = 0

        self.running_scan = False

        self.scan_voltage = 3.0

        self.measurements.clear()

        self.iv_voltage.clear()
        self.iv_current.clear()

        self.voltage_scale.set(0)

        self.filter_combo.current(2)

        self.power_indicator.config(
            text="● POWER OFF",
            fg=RED
        )

        self.power_button.config(
            text="⏻  MAIN POWER",
            bg="#263640"
        )

        self.lamp_button.config(
            text="💡  LIGHT SOURCE OFF",
            bg="#263640"
        )

        self.cell_button.config(
            text="🔌  CONNECT PHOTO CELL",
            bg="#263640"
        )

        self.scan_button.config(
            text="▶  AUTOMATIC I-V SCAN",
            bg="#24506a"
        )

        self.status_var.set(
            "Experiment reset - apparatus ready."
        )

        self.refresh_all()


    # ========================================================
    # RESIZE
    # ========================================================

    def on_resize(self, event):

        if event.widget == self:

            try:
                self.draw_apparatus()
            except tk.TclError:
                pass


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    app = PlanckLab()

    app.mainloop()