# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 23:12:06 2017

@author: Tongwei
"""

import sys
from PyQt4 import QtCore, QtGui, uic
import BaiduAPI
import FangTianXia
import xlwings as xw
import pandas as pd

stdi,stdo,stde = sys.stdin,sys.stdout,sys.stderr
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdin,sys.stdout,sys.stderr = stdi,stdo,stde
 
qtCreatorFile = 'mainwindow.ui' # Enter file here.
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.Search_button.clicked.connect(self.search)
        
    def search(self):
        target_city = self.City_inputText.toPlainText()
        target_district = self.District_inputText.toPlainText()
        target_county = self.County_inputText.toPlainText()
        target_location = self.Location_inputText.toPlainText()
        target_category = '商业/办公用地'
        target_search = target_city + target_district + target_county + target_location
        fangtianxia = FangTianXia.FangTianXia(target_city, target_district, target_county, target_location, target_category)
        a = fangtianxia.main()
        for each in a:
            each[1] = BaiduAPI.Distance(target_search, each[0], target_city).main()
        self.write_toexcel(a)
        
    def write_toexcel(self, data):
        app = xw.App(visible = False, add_book = False)
        wb = app.books.add()
        df = pd.DataFrame(data, columns=['Name', 'Distance/km', 'Area/m2', 'Deal_Status', 'Deal_date', 'Deal_amount/万元', 'url_search'])
        wb.sheets['sheet1'].range('A1').value = df
        wb.sheets['sheet1'].range('A1').options(pd.DataFrame, expand='table').value
        wb.save(r'comp_data_' + self.County_inputText.toPlainText() +'.xlsx')
        wb.close()
        app.quit()
 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())