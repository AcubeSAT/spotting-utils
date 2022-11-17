from sys import exit

from PySide6.QtWidgets import QApplication

from GUI import GCodeUtilsGUI
from IOUtils import read_config
from paths import get_path

if __name__ == "__main__":
    CONFIG = read_config(get_path("config"))
    WINDOW_CONFIG = CONFIG["window"]

    app = QApplication([])

    window = GCodeUtilsGUI(CONFIG)
    window.resize(
        WINDOW_CONFIG["dimension"]["width"],
        WINDOW_CONFIG["dimension"]["height"]
    )
    window.show()

    exit(app.exec())
