import sys
import os
import time
import subprocess
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QProgressBar, QComboBox
from ppadb.client import Client as AdbClient
from PySide6.QtCore import QTimer

APK_PATH = 'utilities/uptodown.apk'
PACKAGE_NAME = 'com.uptodown'

REMOTE_SCREENSHOT_PATH = '/sdcard/screenshot_{timestamp}.jpeg'
LOCAL_SCREENSHOT_FOLDER = 'screenshots'


def get_connected_devices():
    """Get a list of serial numbers of all connected devices using adb devices."""
    try:
        result = subprocess.check_output(["adb", "devices"]).decode("utf-8")
        lines = result.splitlines()
        devices = []

        # Start parsing from the second line (skipping the header)
        for line in lines[1:]:
            if line.strip():  # Skip empty lines
                serial_number = line.split()[0]
                devices.append(serial_number)

        return devices

    except Exception as e:
        print(f"Error getting device serials: {e}")
        return []


class AppManager:
    def __init__(self, selected_device=None):
        self.device_serials = get_connected_devices()
        if selected_device and selected_device in self.device_serials:
            self.device_serial = selected_device
        elif self.device_serials:
            self.device_serial = self.device_serials[0]  # Select the first device by default
        else:
            self.device_serial = None  # No device connected
        self.client = AdbClient(host="127.0.0.1", port=5037)

    def connect_to_app(self, progress_callback):
        if not self.device_serial:
            progress_callback(0)
            return "No device connected."

        try:
            self.device = self.client.device(self.device_serial)  # Connect to the selected device
            progress_callback(100)  # Task completed
            return f'Device is connected. \nSerial number: {self.device.serial}'
        except Exception as e:
            progress_callback(0)  # Task failed
            return f'{str(e)}\nDevice is not connected. Check device connection and try again.'

    def install_app(self, apk_path, progress_callback):
        for i, device in enumerate(self.client.devices()):
            progress_callback(50)  # Progress of 50% during installation
            if device.install(apk_path):
                progress_callback(100)  # Task completed
                return "App is installed."
            else:
                progress_callback(0)  # Task failed
                return "App is not installed."

    def app_is_installed(self, package_name):
        for device in self.client.devices():
            if device.is_installed(package_name):
                return "App is already installed."
            else:
                return "App is not installed."

    def uninstall_app(self, package_name, progress_callback):
        for i, device in enumerate(self.client.devices()):
            progress_callback(50)  # Progress of 50% during uninstallation
            if device.uninstall(package_name):
                progress_callback(100)  # Task completed
                return "App is uninstalled."
            else:
                progress_callback(0)  # Task failed
                return "App is not uninstalled."

    def take_screenshot(self, progress_callback):
        try:
            timestamp = time.strftime("%d_%m_%Y_%H-%M-%S")
            remote_file = REMOTE_SCREENSHOT_PATH.format(timestamp=timestamp)
            local_file = os.path.join(LOCAL_SCREENSHOT_FOLDER, f'screenshot_{timestamp}.jpeg')

            progress_callback(30)  # Progress of 30% before taking the screenshot
            self.device.shell(f'screencap -p {remote_file}')
            if not os.path.exists(LOCAL_SCREENSHOT_FOLDER):
                os.makedirs(LOCAL_SCREENSHOT_FOLDER)

            progress_callback(60)  # Progress of 60% during file transfer
            self.device.pull(remote_file, local_file)
            progress_callback(100)  # Task completed
            return f'Screenshot saved locally: {local_file}'
        except Exception as e:
            progress_callback(0)  # Task failed
            return f"Error while taking screenshot: {e}"


class AppUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ADB App Manager")
        self.setGeometry(100, 100, 500, 300)

        self.app_manager = None  # Initially, no device is selected

        self.init_ui()

        # Set up a timer to periodically check for device connectivity
        self.device_check_timer = QTimer(self)
        self.device_check_timer.timeout.connect(self.check_device_connection)
        self.device_check_timer.start(5000)  # Check every 5 seconds

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.status_label = QLabel("Status: Not connected", self)
        self.layout.addWidget(self.status_label)

        # Dropdown for selecting device
        self.device_combobox = QComboBox(self)
        self.device_combobox.addItem("Select a device")
        self.device_combobox.currentIndexChanged.connect(self.select_device)
        self.layout.addWidget(self.device_combobox)

        self.connect_button = QPushButton("Connect to Device", self)
        self.connect_button.clicked.connect(self.connect_device)
        self.layout.addWidget(self.connect_button)

        self.install_button = QPushButton("Install App", self)
        self.install_button.clicked.connect(self.install_app)
        self.layout.addWidget(self.install_button)

        self.uninstall_button = QPushButton("Uninstall App", self)
        self.uninstall_button.clicked.connect(self.uninstall_app)
        self.layout.addWidget(self.uninstall_button)

        self.screenshot_button = QPushButton("Take Screenshot", self)
        self.screenshot_button.clicked.connect(self.take_screenshot)
        self.layout.addWidget(self.screenshot_button)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFormat("%p%")  # Display percentage inside the progress bar
        self.layout.addWidget(self.progress_bar)

        self.setLayout(self.layout)

        # Get available devices and populate combobox
        self.populate_devices()

    def populate_devices(self):
        devices = get_connected_devices()

        # Clear existing items first
        self.device_combobox.clear()

        if devices:
            self.device_combobox.addItem("Select a device")
            self.device_combobox.addItems(devices)
        else:
            self.device_combobox.addItem("No devices connected")

    def check_device_connection(self):
        """Periodically check for connected devices and refresh the list if needed."""
        connected_devices = get_connected_devices()
        current_device = self.device_combobox.currentText()

        # If device is disconnected, refresh the list
        if current_device not in connected_devices:
            self.populate_devices()
            self.status_label.setText("Device disconnected. Please select a new one.")

    def select_device(self):
        selected_device = self.device_combobox.currentText()
        if selected_device != "Select a device" and selected_device != "No devices connected":
            self.app_manager = AppManager(selected_device)
            self.status_label.setText(f"Device {selected_device} selected.")
        else:
            self.status_label.setText("No device selected.")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def connect_device(self):
        if not self.app_manager:
            self.status_label.setText("Please select a device first.")
            return
        self.progress_bar.setValue(0)  # Reset progress bar
        message = self.app_manager.connect_to_app(self.update_progress)
        self.status_label.setText(f"Status: {message}")

    def install_app(self):
        if not self.app_manager:
            self.status_label.setText("Please select a device first.")
            return
        self.progress_bar.setValue(0)  # Reset progress bar
        message = self.app_manager.install_app(APK_PATH, self.update_progress)
        self.status_label.setText(message)

    def uninstall_app(self):
        if not self.app_manager:
            self.status_label.setText("Please select a device first.")
            return
        self.progress_bar.setValue(0)  # Reset progress bar
        message = self.app_manager.uninstall_app(PACKAGE_NAME, self.update_progress)
        self.status_label.setText(message)

    def take_screenshot(self):
        if not self.app_manager:
            self.status_label.setText("Please select a device first.")
            return
        self.progress_bar.setValue(0)  # Reset progress bar
        message = self.app_manager.take_screenshot(self.update_progress)
        self.status_label.setText(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set the Fusion style
    app.setStyle("Fusion")

    window = AppUI()
    window.show()
    sys.exit(app.exec())
