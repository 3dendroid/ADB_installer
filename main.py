from ppadb.client import Client as AdbClient

APK_PATH = 'utilities/uptodown.apk'
PACKAGE_NAME = 'com.uptodown'  # dumpsys window displays | grep - E “mCurrentFocus” - get app package
DEVICE = 'R58R6133MRL'
ANY_COMMAND = 'screencap -p /sdcard/screenshot.jpeg'


class AppManager:
    def __init__(self):
        self.device = DEVICE
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.devices = self.client.devices()

    def get_api_version(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        print(f'API VERSION: {self.client.version()}')

    def connect(self):
        try:
            self.client = AdbClient(host="127.0.0.1", port=5037)
            self.device = self.client.device(DEVICE)
            print(f'DEVICE IS CONNECTED. \nSERIAL NUMBER: {self.device.serial}')
        except Exception as e:
            print(e, '\nDEVICE IS NOT CONNECTED. CHECK DEVICE CONNECTION AND TRY AGAIN')

    def install(self, apk_path):
        for device in self.devices:
            print("INSTALLING APP...")
            if device.install(apk_path):
                print("APP IS INSTALLED")
            else:
                print("APP IS NOT INSTALLED")

    # Check apk is installed
    def is_installed(self, package_name):
        for device in self.devices:
            if device.is_installed(package_name):
                print("APP IS ALREADY INSTALLED")
            else:
                print("APP IS NOT INSTALLED")

    # Uninstall
    def uninstall(self, package_name):
        for device in self.devices:
            print("UNINSTALLING APP...")
            if device.uninstall(package_name):
                print("APP IS UNINSTALLED")
            else:
                print("APP IS NOT UNINSTALLED")

    def adb_command(self, command):
        for device in self.devices:
            print(device.shell(command))
            print("COMMAND EXECUTED")


if __name__ == "__main__":
    app = AppManager()
    # app.connect()
    # app.is_installed(PACKAGE_NAME)
    # # app.install(APK_PATH)
    # app.uninstall(PACKAGE_NAME)
    app.adb_command(ANY_COMMAND)
