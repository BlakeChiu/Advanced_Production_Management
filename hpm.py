import sys
import random
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QFileDialog)

class Sequence:
    def __init__(self, machine1, machine2, machine3):
        self.machine1 = machine1
        self.machine2 = machine2
        self.machine3 = machine3

    def calculate(self):
        machine1=self.machine1[:]
        machine2=self.machine2[:]
        machine3=self.machine3[:]
        order = [0] * (len(machine1))
        left = 0
        right = -1
        for i in range(len(machine1)):
            if min(machine1) < min(machine2):
                index = machine1.index(min(machine1))  #最小元素在數組1中
                #從左邊填充表格
                order[left] = index + 1
                left += 1
            elif min(machine2) < min(machine3):
                index = machine2.index(min(machine2))  #最小元素在數組1中
                #從左邊填充表格
                order[left] = index + 1
                left += 1
            else:
                #從右邊填充表格
                index = machine3.index(min(machine3))  #最小元素在數組3中
                order[right] = index + 1
                right -= 1

            #用最大值填充，以便在後續迭代中不能將它們選為最小值
            machine1[index] = max(machine1) + max(machine2) + max(machine3)
            machine2[index] = max(machine1) + max(machine2) + max(machine3)
            machine3[index] = max(machine1) + max(machine2) + max(machine3)

        return order

    def get_time(self):
        order=self.calculate()
        time1 = 0
        time2 = self.machine1[order[0] - 1]
        time3 = self.machine2[order[1] - 1]
        for i in order:
            time1 +=self.machine1[i - 1]
            if time1 > time2:
                time2 += time1 - time2
                time2 +=  self.machine2[i - 1]
            elif time2 > time3:
                time3 += time2 - time3

        return time3

class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Johnson's algorithm")

        """創造要用的物件(表格、邊輯文字、按鈕)"""

        self.j1 = []
        self.j2 = []
        self.j3 = []
        self.W = 0

        self.jobs1 = QLineEdit()
        self.jobs2 = QLineEdit()
        self.tasks_count = QLineEdit()
        self.tasks_table = QTableWidget()
        self.file_name = QLineEdit()

        self.from_keys = QPushButton("輸入資料")
        self.random = QPushButton("生成隨機值")
        self.from_file = QPushButton("從文件中選擇資料")
        self.clear = QPushButton("清除")
        self.quit = QPushButton("關閉")

        self.solve = QPushButton("解決")
        self.save = QPushButton("將儲存格中數值存檔")

        self.result = QLabel()
        self.time = QLabel()

        """創造佈局，然後添加小部件"""

        self.left = QVBoxLayout()
        self.left.addWidget(QLabel("工作數"))
        self.left.addWidget(self.tasks_count)
        self.left.addWidget(self.from_keys)
        self.left.addWidget(self.random)
        self.left.addWidget(self.from_file)
        self.left.addWidget(self.clear)
        self.left.addWidget(self.quit)
        self.center = QVBoxLayout()
        self.right = QVBoxLayout()

        """創造一個佈局，然後將左中右的東西加進來"""

        self.layout = QHBoxLayout()
        self.layout.addLayout(self.left)
        self.layout.addLayout(self.center)
        self.layout.addLayout(self.right)

        self.setLayout(self.layout)

        """物件的監聽"""
        
        self.from_keys.clicked.connect(self.create_table)

        self.random.clicked.connect(self.create_table)
        self.random.clicked.connect(self.random_values)

        self.from_file.clicked.connect(self.create_table)
        self.from_file.clicked.connect(self.values_from_file)

        self.tasks_count.textChanged[str].connect(self.check_disable)

        self.solve.clicked.connect(self.solve_problem)
        self.clear.clicked.connect(self.clear_table)
        self.save.clicked.connect(self.save_to_file)
        self.quit.clicked.connect(self.quit_application)

    """在佈局中添加按鈕以選擇計算方法"""

    def create_right_layout(self):
        self.layout.addLayout(self.right)
        self.right.addWidget(self.solve)
        self.right.addWidget(self.save)
        self.right.addWidget(self.result)
        self.right.addWidget(self.time)

        self.result.hide()  # 將結果隱藏，直到解決按鈕發出請求

    @Slot()
    def create_table(self):
        self.tasks_table.setColumnCount(int(self.tasks_count.text()))
        self.tasks_table.setRowCount(3)
        self.tasks_table.setVerticalHeaderLabels(["機器1","機器2","機器3"]) 

        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tasks_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.center.addWidget(self.tasks_table)
        self.create_right_layout()

    @Slot()
    def random_values(self):
        for i in range(self.tasks_table.columnCount()):
            self.tasks_table.setItem(0, i, QTableWidgetItem( 
                str(random.randint(1, 100))))
            self.tasks_table.setItem(1, i, QTableWidgetItem(
                str(random.randint(1, 100))))
            self.tasks_table.setItem(2, i, QTableWidgetItem(
                str(random.randint(1, 100))))
            
    @Slot()
    def values_from_file(self):
        self.left.insertWidget(9, self.file_name)  # 添加一個顯示文件名稱的物件
        self.file_name.setText(QFileDialog.getOpenFileName()[0])

        with open(self.file_name.text(), 'r') as f:
            for idx_line, line in enumerate(f):
                for idx, item in enumerate(line.split(' ')):
                    self.tasks_table.setItem(idx_line, idx, QTableWidgetItem(str(item)))

    """將表保存至文件"""

    @Slot()
    def save_to_file(self):

        self.file_name.setText(QFileDialog.getSaveFileName()[0])

        with open(self.file_name.text(), 'w') as f:
            for i in range(self.tasks_table.columnCount()):
                f.write(self.tasks_table.item(0, i).text() + ' ')
            f.write('\n')
            for j in range(self.tasks_table.columnCount()):
                f.write(self.tasks_table.item(1, j).text() + ' ')
            f.write('\n')
            for j in range(self.tasks_table.columnCount()):
                f.write(self.tasks_table.item(2, j).text() + ' ')

    def convert_to_lists(self):
        for i in range(self.tasks_table.columnCount()):
            self.j1.append(int(self.tasks_table.item(0, i).text()))
        for j in range(self.tasks_table.columnCount()):
            self.j2.append(int(self.tasks_table.item(1, j).text()))
        for j in range(self.tasks_table.columnCount()):
            self.j3.append(int(self.tasks_table.item(2, j).text()))
    
    @Slot()
    def solve_problem(self):
        self.convert_to_lists()
        best_sequence = Sequence(self.j1, self.j2, self.j3)
        best = best_sequence.calculate()
        str_best = [str(i) for i in best]
        self.result.setText("最佳順序: " + " ".join(str_best))
        self.time.setText("時間: " + str(best_sequence.get_time()) + "小時")
        self.result.show()
        self.time.show()

    @Slot()
    def check_disable(self):
        actions = [self.from_keys, self.random, self.from_file]
        for action in actions:
            if not self.tasks_count.text():
                action.setEnabled(False)
            else:
                action.setEnabled(True)

    def clear_result(self):
        self.W = 0
        self.x = []
        self.y = []
    
    @Slot()
    def clear_table(self):
        self.tasks_count.setText(" ")
        self.tasks_table.setColumnCount(0)
        self.tasks_table.setRowCount(0)
        self.result.setText(" ")
        self.time.setText(" ")
        self.file_name.setText(" ")

        self.j1 = []
        self.j2 = []
        self.j3 = []

    @Slot()
    def quit_application(self):
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.resize(1000, 200)
    widget.show()
    sys.exit(app.exec_())