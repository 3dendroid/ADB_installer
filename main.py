from ppadb.client import Client as AdbClient

APK_PATH = 'utilities/uptodown.apk'
PACKAGE_NAME = 'com.uptodown'  # dumpsys window displays | grep - E “mCurrentFocus” - get app package


class AppManager:
    def __init__(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.devices = self.client.devices()

    def get_api_version(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        print(f'API VERSION IS: {self.client.version()}')

    def connect(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.device = self.client.device('R58R6133MRL')
        print(f'DEVICE IS CONNECTED. SERIAL NUMBER IS: {self.device.serial}')

    def install(self, apk_path):
        for device in self.devices:
            device.install(apk_path)
        print("APP IS INSTALLED")

    # Check apk is installed
    def is_installed(self, package_name):
        for device in self.devices:
            print(device.is_installed(package_name))
        print("APP IS ALREADY INSTALLED")

    # Uninstall
    def uninstall(self, package_name):
        for device in self.devices:
            device.uninstall(package_name)
        print("APP IS UNINSTALLED")


if __name__ == "__main__":
    app = AppManager()
    app.get_api_version()
    app.connect()
    # app.is_installed(PACKAGE_NAME)
    # app.install(APK_PATH)
    app.uninstall(PACKAGE_NAME)
