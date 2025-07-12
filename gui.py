# file: ground_station_multitab.py

import sys
import csv
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import pandas as pd
from datetime import datetime
import random

TEAM_ID = "1000" #change accordingly to the team number we get

class GroundStation(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TMU CanSat Ground Station")
        self.setGeometry(100, 100, 1300, 800)
        self.packet_count = 0
        self.sim_mode_active = False
        self.telemetry_data = []

        self.init_ui()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.read_simulated_telemetry)

    def init_ui(self):
        self.tabs = QtWidgets.QTabWidget()

        # Tabs
        self.telemetry_tab = QtWidgets.QWidget()
        self.command_tab = QtWidgets.QWidget()
        self.log_tab = QtWidgets.QWidget()

        self.tabs.addTab(self.telemetry_tab, "📊 Telemetry")
        self.tabs.addTab(self.command_tab, "🛰 Commands")
        self.tabs.addTab(self.log_tab, "📄 Logs")

        self.setup_telemetry_tab()
        self.setup_command_tab()
        self.setup_log_tab()

        self.setCentralWidget(self.tabs)

    def setup_telemetry_tab(self):
        layout = QtWidgets.QVBoxLayout()
        self.plot_widget = pg.PlotWidget(title="Altitude vs Time")
        self.plot_widget.setLabel('left', 'Altitude', 'm')
        self.plot_widget.setLabel('bottom', 'Time', 's')
        self.altitude_curve = self.plot_widget.plot(pen='r')
        layout.addWidget(self.plot_widget)

        # Control buttons
        btns = QtWidgets.QHBoxLayout()
        self.btn_start = QtWidgets.QPushButton("▶ Start Simulation")
        self.btn_save = QtWidgets.QPushButton("💾 Save CSV")
        self.btn_start.clicked.connect(self.toggle_sim_mode)
        self.btn_save.clicked.connect(self.save_csv)
        btns.addWidget(self.btn_start)
        btns.addWidget(self.btn_save)

        layout.addLayout(btns)
        self.telemetry_tab.setLayout(layout)

    def setup_command_tab(self):
        layout = QtWidgets.QFormLayout()

        self.cmd_input = QtWidgets.QLineEdit()
        self.cmd_send = QtWidgets.QPushButton("Send Manual Command")
        self.cmd_send.clicked.connect(self.send_manual_command)

        layout.addRow("Custom Command:", self.cmd_input)
        layout.addRow("", self.cmd_send)

        # Predefined buttons
        predefined_layout = QtWidgets.QHBoxLayout()
        self.btn_cxon = QtWidgets.QPushButton("CXON")
        self.btn_sim_enable = QtWidgets.QPushButton("SIM ENABLE")
        self.btn_sim_activate = QtWidgets.QPushButton("SIM ACTIVATE")
        self.btn_cal = QtWidgets.QPushButton("CAL")
        self.btn_mech = QtWidgets.QPushButton("Activate Heatshield")

        self.btn_cxon.clicked.connect(lambda: self.send_command("CMD,{0},CX,ON".format(TEAM_ID)))
        self.btn_sim_enable.clicked.connect(lambda: self.send_command("CMD,{0},SIM,ENABLE".format(TEAM_ID)))
        self.btn_sim_activate.clicked.connect(lambda: self.send_command("CMD,{0},SIM,ACTIVATE".format(TEAM_ID)))
        self.btn_cal.clicked.connect(lambda: self.send_command("CMD,{0},CAL".format(TEAM_ID)))
        self.btn_mech.clicked.connect(lambda: self.send_command("CMD,{0},MEC,HEATSHIELD,ON".format(TEAM_ID)))

        predefined_layout.addWidget(self.btn_cxon)
        predefined_layout.addWidget(self.btn_sim_enable)
        predefined_layout.addWidget(self.btn_sim_activate)
        predefined_layout.addWidget(self.btn_cal)
        predefined_layout.addWidget(self.btn_mech)

        layout.addRow("Quick Commands:", predefined_layout)
        self.command_tab.setLayout(layout)

    def setup_log_tab(self):
        layout = QtWidgets.QVBoxLayout()
        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)
        self.log_tab.setLayout(layout)

    def toggle_sim_mode(self):
        if not self.sim_mode_active:
            self.sim_mode_active = True
            self.timer.start(1000)
            self.log("Simulation started.")
        else:
            self.sim_mode_active = False
            self.timer.stop()
            self.log("Simulation stopped.")

    def read_simulated_telemetry(self):
        self.packet_count += 1
        time_str = datetime.utcnow().strftime("%H:%M:%S")
        altitude = round(100 + random.uniform(-5, 5), 2)
        temperature = round(25 + random.uniform(-2, 2), 2)
        pressure = round(101.3 + random.uniform(-1, 1), 2)
        voltage = round(7.4 + random.uniform(-0.2, 0.2), 2)

        data = [TEAM_ID, time_str, self.packet_count, "S", "ASCENT",
                altitude, temperature, pressure, voltage,
                "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "SIM ENABLE"]
        self.telemetry_data.append(data)
        self.update_plot()
        self.log(f"[{time_str}] Packet {self.packet_count}: Alt={altitude}m, Temp={temperature}°C")

    def update_plot(self):
        altitudes = [float(d[5]) for d in self.telemetry_data]
        self.altitude_curve.setData(altitudes)

    def send_command(self, cmd):
        # In real app: serial.write((cmd + '\n').encode())
        self.log(f"[SENT] {cmd}")

    def send_manual_command(self):
        cmd = self.cmd_input.text().strip()
        if cmd:
            self.send_command(cmd)
            self.cmd_input.clear()

    def save_csv(self):
        filename = f"Flight_{TEAM_ID}.csv"
        headers = ["TEAM_ID", "MISSION_TIME", "PACKET_COUNT", "MODE", "STATE",
                   "ALTITUDE", "TEMPERATURE", "PRESSURE", "VOLTAGE",
                   "GYRO_R", "GYRO_P", "GYRO_Y",
                   "ACCEL_R", "ACCEL_P", "ACCEL_Y",
                   "MAG_R", "MAG_P", "MAG_Y",
                   "AUTO_GYRO_ROTATION_RATE",
                   "GPS_TIME", "GPS_ALTITUDE", "GPS_LAT", "GPS_LON", "GPS_SATS",
                   "CMD_ECHO"]
        with open(filename, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(self.telemetry_data)
        self.log(f"[SAVED] Data saved to {filename}")

    def log(self, message):
        self.log_box.append(message)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gs = GroundStation()
    gs.show()
    sys.exit(app.exec_())
