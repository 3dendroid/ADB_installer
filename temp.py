import subprocess

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

# Usage example
devices = get_connected_devices()

if devices:
    print(f"Connected devices: {', '.join(devices)}")
else:
    print("No devices connected.")


class AppManager:
    def __init__(self):
        self.device_serials = get_connected_devices()  # Get a list of connected device serials
        if self.device_serials:
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
