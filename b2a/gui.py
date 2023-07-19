#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  main.py
@Date    :  2021/07/23
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""
import sys
import _thread
import b2a
import importlib


def enableGui():
    try:
        importlib.import_module('PyQt5')
        importlib.import_module('qt_material')
        return True
    except Exception as e:
        return False
    

if not enableGui():
    def startGui():
        print("Not support gui. Please type: `pip3 install PyQt5 qt_material`")
else:
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets

    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from qt_material import apply_stylesheet

    class MainView(QWidget):
        s_async_finish = pyqtSignal()

        def __init__(self):
            super().__init__()
            self._fileAttrs = [[], []]
            self.plat = [b2a.bdyplat, b2a.aliplat]
            self.setFixedSize(800, 600)
            self.__initView__()
            self.s_async_finish.connect(self.__asyncFinishSlot__)

        def __initView__(self):
            self.label = []
            self.returnbtn = []
            self.tableView = []
            self.tableLayout = []

            for index, name in enumerate([self.plat[0].name, self.plat[1].name]):
                label = QLabel(f"{name}:/")
                label.setFixedWidth(332)
                btn = QPushButton('')
                btn.setStyleSheet("QPushButton{border:none;}")
                btn.setIcon(QApplication.style().standardIcon(QStyle.SP_ArrowLeft))
                btn.setFixedWidth(30)
                btn.clicked.connect(self.__returnSlot__)
                table = QTableView()
                table.setSelectionBehavior(QAbstractItemView.SelectRows)
                table.setEditTriggers(QAbstractItemView.NoEditTriggers)
                table.verticalHeader().setVisible(False)
                table.horizontalHeader().setStretchLastSection(True)
                table.doubleClicked.connect(self.__inSlot__)

                self.label.append(label)
                self.returnbtn.append(btn)
                self.tableView.append(table)

                headlayout = QHBoxLayout()
                headlayout.addWidget(btn, QtCore.Qt.AlignLeft)
                headlayout.addWidget(label, QtCore.Qt.AlignLeft)

                layout = QVBoxLayout()
                layout.addLayout(headlayout)
                layout.addWidget(table)

                self.tableLayout.append(layout)

            self.asyncbtn = QPushButton('')
            self.asyncbtn.setIcon(QApplication.style().standardIcon(QStyle.SP_ArrowRight))
            self.asyncbtn.setFixedWidth(50)
            self.asyncbtn.clicked.connect(self.__asyncSlot__)
            bottomlayout = QHBoxLayout(self)
            bottomlayout.addLayout(self.tableLayout[0])
            bottomlayout.addWidget(self.asyncbtn)
            bottomlayout.addLayout(self.tableLayout[1])

            self.setWindowTitle('B2A')
            self.setMinimumSize(400, 400)
            self.show()

            self.listPath('/', 0)
            self.listPath('/', 1)

        def __returnSlot__(self):
            idx = self.returnbtn.index(self.sender())
            path = self.label[idx].text().replace(f"{self.plat[idx].name}:", "")
            array = path.rstrip('/').split('/')
            newPath = '/'.join(array[0:-1])
            self.listPath(newPath, idx)

        def __asyncSlot__(self):
            index = self.tableView[0].currentIndex()
            if index.row() < 0:
                QMessageBox.warning(self, '同步失败', '请先选择要同步的文件或目录')
                return
            attr = self._fileAttrs[0][index.row()]
            if attr.isfile:
                QMessageBox.warning(self, '同步失败', '只支持同步文件夹')
                return

            srcPath = attr.path
            toPath = self.label[1].text().replace(f"{self.plat[1].name}:", "") + f'/{attr.name}'
            toPath = toPath.replace('//', '/')
            
            ret = QMessageBox.information(self,
                                        "是否同步", f"百度云 [{srcPath}]\n\n到阿里云 [{toPath}]",
                                        QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                return

            self.asyncbtn.setDisabled(True)

            def __thread_download__(model: MainView, srcPath: str, toPath: str):
                b2a.asyncPath(srcPath, toPath)
                model.s_async_finish.emit()
            _thread.start_new_thread(__thread_download__, (self, srcPath, toPath))

        def __asyncFinishSlot__(self):
            self.asyncbtn.setDisabled(False)
            QMessageBox.information(self, '提示', '同步结束')

        def __inSlot__(self):
            idx = self.tableView.index(self.sender())
            index = self.tableView[idx].currentIndex()
            if not index.isValid() or index.row() < 0:
                return
            item = self._fileAttrs[idx][index.row()]
            if item.isfile:
                return
            self.listPath(item.path, idx)

        def listPath(self, path: str, idx=0):
            self._fileAttrs[idx] = self.plat[idx].list(path)
            model = QStandardItemModel()
            dlgIcon = QApplication.style().standardIcon(QStyle.SP_DialogOpenButton)
            fileIcon = QApplication.style().standardIcon(QStyle.SP_FileIcon)
            for index, name in enumerate(['#', '文件名']):
                model.setHorizontalHeaderItem(index, QStandardItem(name))
            for index, item in enumerate(self._fileAttrs[idx]):
                model.setItem(index, 0, QStandardItem(str(index + 1)))
                st = QStandardItem(item.name)
                st.setIcon(fileIcon if item.isfile else dlgIcon)
                model.setItem(index, 1, st)
            self.tableView[idx].setModel(model)
            self.tableView[idx].setColumnWidth(0, 30)

            self.label[idx].setText(f"{self.plat[idx].name}:" + path)
       

    def login() -> bool:
        if not b2a.loginAli(b2a.config.aliKey):
            return False
        if not b2a.loginBdy(b2a.config.bdyKey):
            return False
        return True


    def startGui():
        app = QtWidgets.QApplication(sys.argv)
        apply_stylesheet(app, theme='dark_teal.xml')

        if not login():
            qmb = QMessageBox()
            qmb.setWindowTitle('错误')
            qmb.setText('<h2>登录失败</h2>')
            qmb.setInformativeText('请先正确登录阿里云与百度云！')
            qmb.addButton(QPushButton('确定', qmb), QMessageBox.YesRole)
            qmb.open()
        else:
            ex = MainView()
        sys.exit(app.exec_())
    


if __name__ == '__main__':
    startGui()
