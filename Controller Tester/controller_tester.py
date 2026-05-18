import ctypes
import sys
import tkinter as tk
from tkinter import ttk


BUTTON_NAMES = [
    "Triangle",
    "Circle",
    "Cross",
    "Square",
    "L1",
    "L2",
    "R1",
    "R2",
    "L3",
    "R3",
    "Select",
    "Start",
    "B13",
    "B14",
    "B15",
    "B16",
]

JOY_RETURNX = 0x00000001
JOY_RETURNY = 0x00000002
JOY_RETURNZ = 0x00000004
JOY_RETURNR = 0x00000008
JOY_RETURNU = 0x00000010
JOY_RETURNV = 0x00000020
JOY_RETURNPOV = 0x00000040
JOY_RETURNBUTTONS = 0x00000080
JOY_RETURNALL = (
    JOY_RETURNX
    | JOY_RETURNY
    | JOY_RETURNZ
    | JOY_RETURNR
    | JOY_RETURNU
    | JOY_RETURNV
    | JOY_RETURNPOV
    | JOY_RETURNBUTTONS
)
JOYERR_NOERROR = 0
JOYERR_UNPLUGGED = 167
MAXPNAMELEN = 32
MAX_JOYSTICKOEMVXDNAME = 260


class JOYINFOEX(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_uint32),
        ("dwFlags", ctypes.c_uint32),
        ("dwXpos", ctypes.c_uint32),
        ("dwYpos", ctypes.c_uint32),
        ("dwZpos", ctypes.c_uint32),
        ("dwRpos", ctypes.c_uint32),
        ("dwUpos", ctypes.c_uint32),
        ("dwVpos", ctypes.c_uint32),
        ("dwButtons", ctypes.c_uint32),
        ("dwButtonNumber", ctypes.c_uint32),
        ("dwPOV", ctypes.c_uint32),
        ("dwReserved1", ctypes.c_uint32),
        ("dwReserved2", ctypes.c_uint32),
    ]


class JOYCAPSW(ctypes.Structure):
    _fields_ = [
        ("wMid", ctypes.c_uint16),
        ("wPid", ctypes.c_uint16),
        ("szPname", ctypes.c_wchar * MAXPNAMELEN),
        ("wXmin", ctypes.c_uint32),
        ("wXmax", ctypes.c_uint32),
        ("wYmin", ctypes.c_uint32),
        ("wYmax", ctypes.c_uint32),
        ("wZmin", ctypes.c_uint32),
        ("wZmax", ctypes.c_uint32),
        ("wNumButtons", ctypes.c_uint32),
        ("wPeriodMin", ctypes.c_uint32),
        ("wPeriodMax", ctypes.c_uint32),
        ("wRmin", ctypes.c_uint32),
        ("wRmax", ctypes.c_uint32),
        ("wUmin", ctypes.c_uint32),
        ("wUmax", ctypes.c_uint32),
        ("wVmin", ctypes.c_uint32),
        ("wVmax", ctypes.c_uint32),
        ("wCaps", ctypes.c_uint32),
        ("wMaxAxes", ctypes.c_uint32),
        ("wNumAxes", ctypes.c_uint32),
        ("wMaxButtons", ctypes.c_uint32),
        ("szRegKey", ctypes.c_wchar * MAXPNAMELEN),
        ("szOEMVxD", ctypes.c_wchar * MAX_JOYSTICKOEMVXDNAME),
    ]


def winmm():
    if sys.platform != "win32":
        return None
    return ctypes.WinDLL("winmm")


def list_devices():
    mm = winmm()
    if mm is None:
        return []

    devices = []
    for device_id in range(mm.joyGetNumDevs()):
        state, _ = read_device(device_id)
        if state is not None:
            devices.append((device_id, state["name"]))
    return devices


def read_device(device_id=0):
    mm = winmm()
    if mm is None:
        return None, "This tester uses the Windows joystick API."

    info = JOYINFOEX()
    info.dwSize = ctypes.sizeof(JOYINFOEX)
    info.dwFlags = JOY_RETURNALL

    result = mm.joyGetPosEx(device_id, ctypes.byref(info))
    if result == JOYERR_UNPLUGGED:
        return None, "Selected device is not connected."
    if result != JOYERR_NOERROR:
        return None, f"Device read failed with Windows error {result}."

    caps = JOYCAPSW()
    name = f"Joystick {device_id}"
    if mm.joyGetDevCapsW(device_id, ctypes.byref(caps), ctypes.sizeof(caps)) == JOYERR_NOERROR:
        name = caps.szPname or name

    return {
        "name": name,
        "buttons": [(info.dwButtons >> index) & 1 == 1 for index in range(16)],
        "x": info.dwXpos,
        "y": info.dwYpos,
        "z": info.dwZpos,
        "r": info.dwRpos,
        "u": info.dwUpos,
        "v": info.dwVpos,
        "pov": info.dwPOV,
    }, None


class ControllerTester(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BLE Controller Tester")
        self.geometry("760x470")
        self.minsize(620, 420)

        self.status = tk.StringVar(value="Select a connected input device.")
        self.selected_device = tk.StringVar()
        self.axis_text = tk.StringVar(value="Axes: waiting for data")
        self.pov_text = tk.StringVar(value="D-Pad: centered")
        self.device_ids = {}

        ttk.Label(self, text="BLE Controller Tester", font=("Segoe UI", 18, "bold")).pack(
            anchor="w", padx=18, pady=(16, 4)
        )
        ttk.Label(self, textvariable=self.status).pack(anchor="w", padx=18)

        selector = ttk.Frame(self)
        selector.pack(fill="x", padx=18, pady=(12, 0))
        ttk.Label(selector, text="Device").pack(side="left")
        self.device_menu = ttk.Combobox(
            selector,
            textvariable=self.selected_device,
            state="readonly",
            width=54,
        )
        self.device_menu.pack(side="left", padx=(10, 8), fill="x", expand=True)
        ttk.Button(selector, text="Refresh", command=self.refresh_devices).pack(side="left")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=18, pady=16)

        dpad = ttk.LabelFrame(body, text="D-Pad")
        dpad.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(dpad, textvariable=self.pov_text, font=("Segoe UI", 13)).pack(padx=18, pady=34)

        buttons = ttk.LabelFrame(body, text="Buttons")
        buttons.grid(row=0, column=1, sticky="nsew")

        self.button_labels = []
        for index, name in enumerate(BUTTON_NAMES):
            label = tk.Label(buttons, text=name, width=12, height=2, bg="#505866", fg="white")
            label.grid(row=index // 4, column=index % 4, padx=6, pady=6, sticky="nsew")
            self.button_labels.append(label)

        axes = ttk.LabelFrame(self, text="Axes")
        axes.pack(fill="x", padx=18, pady=(0, 18))
        ttk.Label(axes, textvariable=self.axis_text).pack(anchor="w", padx=12, pady=10)

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self.refresh_devices()
        self.after(33, self.poll)

    def refresh_devices(self):
        devices = list_devices()
        self.device_ids = {f"{name} [{device_id}]": device_id for device_id, name in devices}
        values = list(self.device_ids.keys())
        self.device_menu.configure(values=values)

        if values and self.selected_device.get() not in self.device_ids:
            self.selected_device.set(values[0])
        elif not values:
            self.selected_device.set("")
            self.status.set("No connected input devices found.")

    def poll(self):
        selected = self.selected_device.get()
        if not selected:
            self.status.set("No connected input devices found. Connect or pair a Bluetooth controller, then refresh.")
            self.pov_text.set("D-Pad: centered")
            for label in self.button_labels:
                label.configure(bg="#505866")
            self.after(250, self.poll)
            return

        state, error = read_device(self.device_ids[selected])
        if error:
            self.status.set(error)
            self.pov_text.set("D-Pad: centered")
            for label in self.button_labels:
                label.configure(bg="#505866")
        else:
            self.status.set(f"Connected: {state['name']}")
            self.axis_text.set(
                "Axes: "
                f"X={state['x']}  Y={state['y']}  Z={state['z']}  "
                f"R={state['r']}  U={state['u']}  V={state['v']}"
            )
            self.pov_text.set(format_pov(state["pov"]))
            for index, pressed in enumerate(state["buttons"]):
                self.button_labels[index].configure(bg="#1fb974" if pressed else "#505866")

        self.after(33, self.poll)


def format_pov(value):
    if value == 0xFFFF:
        return "D-Pad: centered"

    directions = {
        0: "Up",
        4500: "Up Right",
        9000: "Right",
        13500: "Down Right",
        18000: "Down",
        22500: "Down Left",
        27000: "Left",
        31500: "Up Left",
    }
    return f"D-Pad: {directions.get(value, value)}"


def self_test():
    devices = list_devices()
    if not devices:
        print("No connected input devices found.")
        return 0

    device_id, name = devices[0]
    state, error = read_device(device_id)
    if error:
        print(error)
        return 0
    pressed = [name for name, active in zip(BUTTON_NAMES, state["buttons"]) if active]
    print(f"Connected: {state['name']}")
    print(format_pov(state["pov"]))
    print("Pressed buttons:", ", ".join(pressed) if pressed else "none")
    return 0


def main():
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())

    app = ControllerTester()
    app.mainloop()


if __name__ == "__main__":
    main()
