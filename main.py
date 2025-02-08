import os
import time

from ppadb.client import Client as AdbClient

APK_PATH = 'utilities/uptodown.apk'
PACKAGE_NAME = 'com.uptodown' # dumpsys window displays | grep - E “mCurrentFocus” - get app package
DEVICE = 'R58R6133MRL'

REMOTE_SCREENSHOT_PATH = '/sdcard/screenshot_{timestamp}.jpeg'  # Путь скриншота на устройстве
LOCAL_SCREENSHOT_FOLDER = 'screenshots'  # Локальная папка для сохранения

class AppManager:
    def __init__(self):
        self.device = DEVICE
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.devices = self.client.devices()

    def get_api_version(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        print(f'API VERSION: {self.client.version()}')

    def connect_to_app(self):
        try:
            self.client = AdbClient(host="127.0.0.1", port=5037)
            self.device = self.client.device(DEVICE)
            print(f'DEVICE IS CONNECTED. \nSERIAL NUMBER: {self.device.serial}')
        except Exception as e:
            print(e, '\nDEVICE IS NOT CONNECTED. CHECK DEVICE CONNECTION AND TRY AGAIN')

    def install_app(self, apk_path):
        for device in self.devices:
            print("INSTALLING APP...")
            if device.install(apk_path):
                print("APP IS INSTALLED")
            else:
                print("APP IS NOT INSTALLED")

    # Check apk is installed
    def app_is_installed(self, package_name):
        for device in self.devices:
            if device.is_installed(package_name):
                print("APP IS ALREADY INSTALLED")
            else:
                print("APP IS NOT INSTALLED")

    # Uninstall
    def uninstall_app(self, package_name):
        for device in self.devices:
            print("UNINSTALLING APP...")
            if device.uninstall(package_name):
                print("APP IS UNINSTALLED")
            else:
                print("APP IS NOT UNINSTALLED")

    # Making a screenshot
    def take_screenshot(self):
        try:
            # Получаем текущую метку времени
            timestamp = time.strftime("%d_%m_%Y_%H-%M-%S")

            # Указываем пути с учётом метки времени
            remote_file = REMOTE_SCREENSHOT_PATH.format(timestamp=timestamp)
            local_file = os.path.join(LOCAL_SCREENSHOT_FOLDER, f'screenshot_{timestamp}.jpeg')

            print("TAKING SCREENSHOT...")
            # Выполняем команду screencap
            self.device.shell(f'screencap -p {remote_file}')
            print(f'SCREENSHOT SAVED ON DEVICE: {remote_file}')

            # Проверяем локальную папку и создаем её, если её нет
            if not os.path.exists(LOCAL_SCREENSHOT_FOLDER):
                os.makedirs(LOCAL_SCREENSHOT_FOLDER)

            # Загружаем скриншот с устройства на локальный ПК
            self.device.pull(remote_file, local_file)
            print(f'SCREENSHOT SAVED LOCALLY: {local_file}')
        except Exception as e:
            print(f"ERROR WHILE TAKING SCREENSHOT: {e}")


if __name__ == "__main__":
    app = AppManager()
    app.connect_to_app()
    # app.app_is_installed(PACKAGE_NAME)
    # app.install_app(APK_PATH)
    # app.uninstall_app(PACKAGE_NAME)
    app.take_screenshot()
