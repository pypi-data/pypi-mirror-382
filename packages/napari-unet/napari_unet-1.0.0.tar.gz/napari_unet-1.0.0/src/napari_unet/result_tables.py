from qtpy.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QApplication, QMainWindow,
                            QTableWidget, QTableWidgetItem, QFileDialog)
from PyQt5.QtGui import QColor, QFont
import csv

class ResultsTable(QMainWindow):
    def __init__(self, data, name='Data Table', parent=None):
        super(ResultsTable, self).__init__(parent)
        self.exp_name = f"{name.replace(' ', '')}.csv"
        self.setWindowTitle(name)
        self.font = QFont()
        self.font.setFamily("Arial Unicode MS, Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji")
        self.init_ui()
        self.set_data(data)

    def init_ui(self):
        # Central widget
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        # Layout
        self.layout = QVBoxLayout(self.centralWidget)

        # Table
        self.table = QTableWidget()
        self.layout.addWidget(self.table)  # Add table to layout

        # Export Button
        self.exportButton = QPushButton('💾 Save as CSV')
        self.exportButton.setFont(self.font)
        self.exportButton.clicked.connect(self.export_data)
        self.layout.addWidget(self.exportButton)

    def set_data(self, data):
        # Assume we have some data structure holding CSV-like data
        columnHeaders = ['Column 1', 'Column 2', 'Column 3']
        rowHeaders = ['Row 1', 'Row 2']
        rowData = [['Row1-Col1', 'Row1-Col2', 'Row1-Col3'],
                   ['Row2-Col1', 'Row2-Col2', 'Row2-Col3']]

        self.table.setColumnCount(len(columnHeaders))
        self.table.setRowCount(len(rowData))
        self.table.setHorizontalHeaderLabels(columnHeaders)
        self.table.setVerticalHeaderLabels(rowHeaders)

        for row, data in enumerate(rowData):
            for column, value in enumerate(data):
                item = QTableWidgetItem(value)
                # Set background color for the cell
                item.setBackground(QColor(255, 255, 200))  # Light yellow background
                self.table.setItem(row, column, item)

    def set_exp_name(self, name):
        self.exp_name = ".".join(name.replace(" ", "-").split('.')[:-1]) + ".csv"

    def export_data(self):
        options = QFileDialog.Options()
        try:
            fileName, _ = QFileDialog.getSaveFileName(
                self, 
                "QFileDialog.getSaveFileName()", 
                self.exp_name,
                "CSV Files (*.csv);;All Files (*)", 
                options=options
            )
        except:
            fileName = None

        if not fileName:
            print("No file selected")
            return
        
        self.export_table_to_csv(fileName)

    def export_table_to_csv(self, filename: str):
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            
            headers = [''] + [
                self.table.horizontalHeaderItem(i).text() if self.table.horizontalHeaderItem(i) is not None else "" 
                for i in range(self.table.columnCount())
            ]
            writer.writerow(headers)
            
            for row in range(self.table.rowCount()):
                row_header = self.table.verticalHeaderItem(row).text() if self.table.verticalHeaderItem(row) is not None else ""
                row_data = []
                for column in range(self.table.columnCount()):
                    item = self.table.item(row, column)
                    row_data.append(item.text() if item is not None else '')
                writer.writerow([row_header] + row_data)


class DataSanityResultsTable(ResultsTable):
    def __init__(self, data, parent=None):
        name = "Training data sanity"
        super(DataSanityResultsTable, self).__init__(data, name, parent)
        self.init_ui()
        self.set_data(data)

    def headers_from_data(self, data):
        for _, v in data.items():
            return list(v.keys())
        return []

    def set_data(self, data):
        columnHeaders = self.headers_from_data(data)
        rowHeaders    = sorted(list(data.keys()))
        
        self.table.setColumnCount(len(columnHeaders))
        self.table.setRowCount(len(rowHeaders))
        self.table.setHorizontalHeaderLabels(columnHeaders)
        self.table.setVerticalHeaderLabels(rowHeaders)

        for row_idx, image_name in enumerate(rowHeaders):
            for col_index, test_name in enumerate(columnHeaders):
                color = QColor(255, 200, 200, 100) if not all(data[image_name].values()) else QColor(200, 255, 200, 100)
                item = QTableWidgetItem("OK" if data[image_name][test_name] else "❌")
                item.setBackground(color)
                self.table.setItem(row_idx, col_index, item)
        self.table.resizeColumnsToContents()


class OneShotMetricsResultsTable(ResultsTable):
    def __init__(self, data, image_name=None, parent=None):
        name = "One-shot metrics"
        if image_name is not None:
            name += f" - {image_name}"
        super(OneShotMetricsResultsTable, self).__init__(data, name, parent)
        self.init_ui()
        self.set_data(data)

    def headers_from_data(self, data):
        for _, v in data.items():
            return list(v.keys())
        return []

    def set_data(self, data):
        columnHeaders = self.headers_from_data(data)
        rowHeaders    = sorted(list(data.keys()))
        
        self.table.setColumnCount(len(columnHeaders))
        self.table.setRowCount(len(rowHeaders))
        self.table.setHorizontalHeaderLabels(columnHeaders)
        self.table.setVerticalHeaderLabels(rowHeaders)

        for row_idx, image_name in enumerate(rowHeaders):
            for col_index, metric_name in enumerate(columnHeaders):
                value = data[image_name][metric_name]
                if isinstance(value, float):
                    display_value = f"{value:.4f}"
                else:
                    display_value = str(value)
                item = QTableWidgetItem(display_value)
                item.setBackground(QColor(255, 255, 200, 100))  # Light yellow background
                self.table.setItem(row_idx, col_index, item)
        self.table.resizeColumnsToContents()


class BatchMetricsResultsTable(ResultsTable):
    def __init__(self, data, metric_name=None, parent=None):
        name = "Batch metrics"
        if metric_name is not None:
            name += f" - {metric_name}"
        super(BatchMetricsResultsTable, self).__init__(data, name, parent)
        self.init_ui()
        self.set_data(data)

    def headers_from_data(self, data):
        for _, v in data.items():
            return list(v.keys())
        return []

    def set_data(self, data):
        columnHeaders = self.headers_from_data(data)
        rowHeaders    = sorted(list(data.keys()))
        
        self.table.setColumnCount(len(columnHeaders))
        self.table.setRowCount(len(rowHeaders))
        self.table.setHorizontalHeaderLabels(columnHeaders)
        self.table.setVerticalHeaderLabels(rowHeaders)

        for row_idx, image_name in enumerate(rowHeaders):
            for col_index, metric_name in enumerate(columnHeaders):
                value = data[image_name][metric_name]
                if isinstance(value, float):
                    display_value = f"{value:.4f}"
                else:
                    display_value = str(value)
                item = QTableWidgetItem(display_value)
                item.setBackground(QColor(255, 255, 200, 100))  # Light yellow background
                self.table.setItem(row_idx, col_index, item)
        self.table.resizeColumnsToContents()

class SkeletonMeasuresResultsTable(ResultsTable):
    def __init__(self, data, image_name=None, parent=None):
        name = "Skeleton measures"
        if image_name is not None:
            name += f" - {image_name}"
        super(SkeletonMeasuresResultsTable, self).__init__(data, name, parent)
        self.init_ui()
        self.set_data(data)

    def headers_from_data(self, data):
        return list(data.keys())

    def set_data(self, data):
        columnHeaders = self.headers_from_data(data)
        
        self.table.setColumnCount(len(columnHeaders))
        self.table.setHorizontalHeaderLabels(columnHeaders)
        self.table.setRowCount(1)

        for col_index, measure_name in enumerate(columnHeaders):
            value = data[measure_name]
            if isinstance(value, float):
                display_value = f"{value:.4f}"
            else:
                display_value = str(value)
            item = QTableWidgetItem(display_value)
            item.setBackground(QColor(255, 255, 200, 100))
            self.table.setItem(0, col_index, item)
        
        self.table.resizeColumnsToContents()

def main_sessions():
    import json
    from pprint import pprint

    r_path = "/tmp/batch.json"
    with open(r_path, "r") as f:
        data = json.load(f)

    pprint(data)
    app = QApplication([])
    table = BatchMetricsResultsTable(data, "accuracy")
    table.show()
    app.exec_()

    print("DONE.")


if __name__ == '__main__':
    main_sessions()