import sys
import os
import csv
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar, QLabel, QFileDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# CSV Data Loader
class DataLoader(QThread):
    progress_signal = pyqtSignal(int)  # Signal for the progress bar
    df_signal = pyqtSignal(pd.DataFrame)  # Signal for the DataFrame
    error_occurred = pyqtSignal(str)  # Signal for error handling

    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name

    def run(self):
        try:
            count = 0
            chunks = pd.read_csv(self.file_name, chunksize=50000)
            for chunk in chunks:
                self.df_signal.emit(chunk)
                count += 1
                self.progress_signal.emit(count*10)
        except FileNotFoundError:
            self.error_occurred.emit("File not found.")
        except pd.errors.EmptyDataError:
            self.error_occurred.emit("No data in the file.")
        except pd.errors.ParserError:
            self.error_occurred.emit("Error parsing the file.")
        except Exception as e:
            self.error_occurred.emit(str(e))

# Application Demo
class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced CSV Analyzer")
        self.resize(1000, 600)

        mainLayout = QVBoxLayout()
        
        self.progressBar = QProgressBar()
        mainLayout.addWidget(self.progressBar)

        self.statusLabel = QLabel('Select a CSV file to start analysis...')
        mainLayout.addWidget(self.statusLabel)

        btn = QPushButton('Load CSV Data')
        btn.clicked.connect(self.loadCSV)
        mainLayout.addWidget(btn)

        self.tableWidget = QTableWidget(0, 4)
        self.tableWidget.setHorizontalHeaderLabels(('RPM', 'CM-FF', 'CM-TCF', 'CM-TRF'))  # Add headers as needed
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        mainLayout.addWidget(self.tableWidget)

        self.setLayout(mainLayout)

    def loadCSV(self):
        self.statusLabel.setText('Loading data...')
        self.csvFileName, _ = QFileDialog.getOpenFileName(self, 'Open CSV file', '', 'CSV Files (*.csv);;All Files (*)')
        if self.csvFileName:
            self.dataLoader = DataLoader(self.csvFileName)
            self.dataLoader.progress_signal.connect(self.progressBar.setValue)
            self.dataLoader.df_signal.connect(self.addDFtoTable)
            self.dataLoader.error_occurred.connect(self.showError)
            self.dataLoader.start()
        else:
            self.statusLabel.setText("No file selected!")

    def addDFtoTable(self, df):
        if df is None:
            self.statusLabel.setText('Error occurred while loading data')
        else:
            row = self.tableWidget.rowCount()
            for i in df.index:
                self.tableWidget.insertRow(row)
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(df['RPM'][i])))  # Add items as needed
                self.tableWidget.setItem(row, 1, QTableWidgetItem(str(df['CM-FF'][i])))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(str(df['CM-TCF'][i])))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(str(df['CM-TRF'][i])))
                row += 1
            self.statusLabel.setText('Data loading complete!')

    def showError(self, error_message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error occurred!")
        error_dialog.setText(error_message)
        error_dialog.exec_()

app = QApplication(sys.argv)
demo = AppDemo()
demo.show()
sys.exit(app.exec_())