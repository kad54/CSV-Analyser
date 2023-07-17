import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar, QLabel, QFileDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox, QGridLayout, QScrollArea, QComboBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class DataLoader(QThread):
    progress_signal = pyqtSignal(int)
    df_signal = pyqtSignal(pd.DataFrame)
    error_occurred = pyqtSignal(str)

    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name

    def run(self):
        try:
            df = pd.read_csv(self.file_name)
            self.df_signal.emit(df)
        except FileNotFoundError:
            self.error_occurred.emit("File not found.")
        except pd.errors.EmptyDataError:
            self.error_occurred.emit("No data in the file.")
        except pd.errors.ParserError:
            self.error_occurred.emit("Error parsing the file.")
        except Exception as e:
            self.error_occurred.emit(str(e))

class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced CSV Analyzer")
        self.resize(1200, 800)
        
        self.gridLayout = QGridLayout()
        
        self.postProcessingButton = QPushButton('Postprocessing')
        self.postProcessingButton.clicked.connect(self.plotData)
        self.gridLayout.addWidget(self.postProcessingButton, 0, 0)

        self.IPTButton = QPushButton('IPT Operating Range 0 - 5000 rpm')
        self.IPTButton.clicked.connect(self.plotData)
        self.gridLayout.addWidget(self.IPTButton, 0, 1)

        self.HPTButton = QPushButton('HPT Operating Range 0 - 12000 rpm')
        self.HPTButton.clicked.connect(self.plotData)
        self.gridLayout.addWidget(self.HPTButton, 0, 2)

        self.FPTButton = QPushButton('FPT Operating Range 0 - 5000 rpm')
        self.FPTButton.clicked.connect(self.plotData)
        self.gridLayout.addWidget(self.FPTButton, 0, 3)

        self.BOButton = QPushButton('BO')
        self.BOButton.clicked.connect(self.plotData)
        self.gridLayout.addWidget(self.BOButton, 1, 0)

        self.HCFButton = QPushButton('HCF')
        self.HCFButton.clicked.connect(self.plotData)
        self.gridLayout.addWidget(self.HCFButton, 1, 1)

        self.L10Button = QPushButton('L10')
        self.L10Button.clicked.connect(self.plotData)
        self.gridLayout.addWidget(self.L10Button, 1, 2)

        self.LimitButton = QPushButton('Limit')
        self.LimitButton.clicked.connect(self.plotData)
        self.gridLayout.addWidget(self.LimitButton, 1, 3)

        self.excitationLabel = QLabel("Excitation:")
        self.gridLayout.addWidget(self.excitationLabel, 2, 0)

        self.excitationList = QComboBox()
        self.excitationList.addItems(["Excitation 1", "Excitation 2", "Excitation 3"])
        self.gridLayout.addWidget(self.excitationList, 2, 1)

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(100)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Station Name", "Maximum value", "RPM"])

        for i in range(100):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(f"Station {i+1}"))
            self.tableWidget.setItem(i, 1, QTableWidgetItem("[Maximum value]"))
            self.tableWidget.setItem(i, 2, QTableWidgetItem("[RPM]"))

        self.gridLayout.addWidget(self.tableWidget, 3, 0, 1, 4)

        self.figure = plt.figure(figsize=(10,10))
        self.canvas = FigureCanvas(self.figure)
        self.gridLayout.addWidget(self.canvas, 0, 4, 4, 1)

        self.setLayout(self.gridLayout)

    def loadCSV(self, file_name):
        self.csvFileName = file_name
        self.dataLoader = DataLoader(self.csvFileName)
        self.dataLoader.df_signal.connect(self.handleDataFrame)
        self.dataLoader.error_occurred.connect(self.showError)
        self.dataLoader.start()

    def handleDataFrame(self, df):
        self.df = df

    def plotData(self):
        if hasattr(self, 'df'):
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(self.df['RPM'], self.df['CM-FF DEFL (MIL DA)'])
            ax.set_xlabel('RPM')
            ax.set_ylabel('CM-FF DEFL (MIL DA)')
            self.canvas.draw()
        else:
            QMessageBox.critical(self, "Error", "No data loaded")

    def showError(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

app = QApplication(sys.argv)
demo = AppDemo()
demo.loadCSV('data.csv')  # Load your data here
demo.show()
sys.exit(app.exec_())
