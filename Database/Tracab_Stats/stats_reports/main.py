import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QVBoxLayout, QWidget, QSizePolicy
from report_generator import main  # Import the main function from your script


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tracab Stats Reports")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.button = QPushButton("Run Stats Report", self)
        self.button.clicked.connect(self.run_script)
        self.button.setFixedSize(200, 50)  # Adjust the button size (width, height)
        self.button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.button)

    def run_script(self):
        self.thread = threading.Thread(target=self.execute_script)
        self.thread.start()

    def execute_script(self):
        try:
            main()
            self.show_message("Success", "The stats report has been generated successfully.")
        except Exception as e:
            self.show_message("Error", f"An error occurred: {e}")

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
