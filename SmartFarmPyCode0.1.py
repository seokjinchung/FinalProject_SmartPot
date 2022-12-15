from PyQt5 import QtCore
import time,schedule
import sys,serial,csv
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QIcon
import numpy as np
from mplwidget import MplWidget
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from PyQt5.QtGui import QMovie
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, MultipleLocator
import matplotlib.ticker as mtick
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

py_serial = serial.Serial(
    port='COM5',         
    baudrate=9600,
)

form_class = uic.loadUiType("smartpot.ui")[0]
form_class2 = uic.loadUiType("mainsetup.ui")[0]
form_class4 = uic.loadUiType("Graph.ui")[0]


class Temp_Humi_Thread(QThread): #온습도 쓰레드 클래스
    temp_humi_soil_waterlv_update = QtCore.pyqtSignal(float, float, float, int)  
    DN_update = QtCore.pyqtSignal(int)
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        while True:
            if py_serial.is_open == True:
                try:
                    serial_line=py_serial.readline()

                    serial_line_list = serial_line.split(b',')

                    temp_float =float(serial_line_list[0].decode()) 
                    humi_float = float(serial_line_list[1].decode()) 
                    soil_float = float(serial_line_list[2].decode()) 
                    waterlv_int = int(serial_line_list[3].decode()) 
                    DN_int = int(serial_line_list[4].decode()) 

                    self.temp_humi_soil_waterlv_update.emit(temp_float, humi_float, soil_float, waterlv_int)
                    self.DN_update.emit(DN_int)

                except:
                    serial_line=py_serial.readline()

                    temp_float = 0.0
                    humi_float = 0.0

                    soil_float = float(serial_line_list[2].decode()) 
                    waterlv_int = int(serial_line_list[3].decode()) 
                    DN_int = int(serial_line_list[4].decode()) 

                    self.temp_humi_soil_waterlv_update.emit(temp_float, humi_float, soil_float, waterlv_int) #온도, 습도 데이터를 실시간으로 thread에서 꺼내어 외부로 전송
                    self.DN_update.emit(DN_int)
    
class Mainsetwindow(QMainWindow, form_class2):
    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.btn_PlantControl.clicked.connect(self.MyWindowshow)
        self.btn_Graph.clicked.connect(self.Graphshow)
        self.btn_PlantControl.setStyleSheet('border-image:url(C:/Users/KOSTA/Desktop/Finalproject/pyqt5/pyqt_final/lettuce.gif);border:0px;')
        self.btn_Graph.setStyleSheet('border-image:url(C:/Users/KOSTA/Desktop/Finalproject/pyqt5/pyqt_final/graph.jpeg);border:0px;')

    def MyWindowshow(self):

        window.show()
        mainsetwindow.close()

    def Graphshow(self):

        graph.show()
        mainsetwindow.close()
    

class MyWindow(QWidget, form_class):
    

    def __init__(self):
        self.toggle = True
        self.toggle_2 = 1

        self.humi_flag = True
        self.temp_flag = True
        self.soil_flag = True
        self.DN_flag = True
        super().__init__()

        self.setupUi(self)

        self.t =np.array([],dtype=float)
        self.signal1 =np.array([],dtype=float)
        self.signal2 =np.array([],dtype=float)
        self.i =0
        self.interval = 60

        self.TH_Thread = Temp_Humi_Thread()
        self.TH_Thread.start()
        self.Fan.setCheckable(True)
        self.Fan.clicked.connect(self.Fan_clicked)
        self.Fan.setDisabled(True)
        self.Fan_2.setCheckable(True)
        self.Fan_2.setDisabled(True)
        self.Fan_2.clicked.connect(self.fan_2clicked)
        self.InputWater.setCheckable(True)
        self.InputWater.setDisabled(True)
        self.InputWater.clicked.connect(self.InputWater_clicked)
        self.OutputWater.setCheckable(True)
        self.OutputWater.setDisabled(True)
        self.OutputWater.clicked.connect(self.OutputWaterclicked)
        self.btn_back.clicked.connect(self.back_clicked)
        self.Clear.clicked.connect(self.clear_clicked)
        self.TH_Thread.temp_humi_soil_waterlv_update.connect(self.Update_Temp_Humi_Soil_Display_and_Logs)
        self.TH_Thread.temp_humi_soil_waterlv_update.connect((self.update_temp_humi_graph))
        self.TH_Thread.DN_update.connect(self.DayandNight)
        self.EventLogs.clicked.connect(self.EventLogsSave)
        self.MODE.setCheckable(True)
        self.MODE.clicked.connect(self.ModeChange)
        self.Mode_display.append("Auto")
        self.LED_MODE.clicked.connect(self.LedModeChange)
        self.LED_MODE.setDisabled(True)
        self.Fan.setStyleSheet("background-color:rgb(0,0,0);color:rgb(0,0,0);")
        self.Fan_2.setStyleSheet("background-color:rgb(0,0,0);color:rgb(0,0,0);")
        self.InputWater.setStyleSheet("background-color:rgb(0,0,0);color:rgb(0,0,0);")
        self.OutputWater.setStyleSheet("background-color:rgb(0,0,0);color:rgb(0,0,0);")


    #캐릭터 애니메이션 포함
    def Update_Temp_Humi_Soil_Display_and_Logs(self, temp_float, humi_float,soil_float, waterlv_int):  #습도 디스플레이 및 로그 업데이트 함수    

        self.TempNow.display(temp_float)
        currentdate = QDate.currentDate()
        currenttime = QTime.currentTime()
        if temp_float > 20 and self.temp_flag == True:
            self.textBrowser.append(currentdate.toString(Qt.ISODate) + " " + currenttime.toString() + " Temp High -> OutFan On") 
            self.temp_flag = False   
        elif 10 < temp_float <=20 and self.temp_flag == False :
            self.temp_flag = True
        elif temp_float <= 10 and self.temp_flag == True:
            self.textBrowser.append(currentdate.toString(Qt.ISODate) + " " + currenttime.toString() + " Temp Low -> InFan On") 
            self.temp_flag = False

       
        self.HumiNow.display(humi_float)
        currentdate = QDate.currentDate()
        currenttime = QTime.currentTime()
        if humi_float >= 65 and self.humi_flag == True:
            self.textBrowser.append(currentdate.toString(Qt.ISODate) + " " + currenttime.toString() + " humidity too high!")    
            self.humi_flag = False
        elif humi_float < 65 :
            self.humi_flag = True

        
        self.SoilhumiNow.display(soil_float)
        if soil_float < 25.7 and self.soil_flag == True:
            self.textBrowser.append(currentdate.toString(Qt.ISODate) + " " + currenttime.toString() + " Soil dry -> InPump On")    
            self.soil_flag = False
        elif 25.7 < soil_float <= 53 and self.soil_flag == False:
            self.soil_flag = True   
        elif soil_float > 53 and waterlv_int > 100 and self.soil_flag == True:
            self.textBrowser.append(currentdate.toString(Qt.ISODate) + " " + currenttime.toString() + " Soil wet -> InPump Off and OutPump On")
            self.soil_flag = False
        elif soil_float > 53 and waterlv_int < 100  and self.soil_flag == False :
            self.textBrowser.append(currentdate.toString(Qt.ISODate) + " " + currenttime.toString() + " WaterLv low -> OutPump Off")    
            self.soil_flag = True

        #캐릭터 애니메이션
        self.movie1 = QMovie("happycharacter.gif")
        self.movie2 = QMovie("sadcharacter.gif")
        if self.temp_flag == True and self.humi_flag == True:
            graph.label.setMovie(self.movie1)
            self.movie1.start()
        else :
            graph.label.setMovie(self.movie2)
            self.movie2.start()

    def DayandNight(self, DN_int):

        # global DN_flag
        currentdate = QDate.currentDate()
        currenttime = QTime.currentTime()
        if DN_int == 9 and self.DN_flag == True:
            self.textBrowser.append(currentdate.toString(Qt.ISODate) + " " + currenttime.toString() + " NightMode On")
            self.DN_flag = False
        elif DN_int == 9 and self.DN_flag == False:
            self.textBrowser.append(currentdate.toString(Qt.ISODate) + " " + currenttime.toString() + " DayMode On")
            self.DN_flag = True

    def EventLogsSave(self):   #로그 저장 함수

        f = open('write.csv','w', newline='')
        wr = csv.writer(f)
        textcontent = self.textBrowser.toPlainText()
        print(textcontent)
        wr.writerow([textcontent+"\n"])
        f.close()

    def Fan_clicked(self):

       if self.Fan.isChecked():
            py_serial.write(b'1') #send 1
            self.MODE.setDisabled(True)
       else :
            py_serial.write(b'1')
            self.SetEnable()

    def fan_2clicked(self): 

       if self.Fan_2.isChecked():
            py_serial.write(b'2')
            self.MODE.setDisabled(True)
       else :
            py_serial.write(b'2')
            self.SetEnable()
    
    def SetEnable(self):

        if(self.Fan_2.isChecked() or self.Fan.isChecked() or self.InputWater.isChecked() or self.OutputWater.isChecked()):
            self.MODE.setDisabled(True)
        else :
            self.MODE.setEnabled(True)

    def InputWater_clicked(self):

       if self.InputWater.isChecked():
            py_serial.write(b'3')
            self.MODE.setDisabled(True) 
       else :
            py_serial.write(b'3')
            self.SetEnable()

    def OutputWaterclicked(self):

       if self.OutputWater.isChecked():
            py_serial.write(b'4')
            self.MODE.setDisabled(True) 
       else :
            py_serial.write(b'4')
            self.SetEnable()
    
    def ModeChange(self):

        # global DN_flag
        # global toggle_2
        if self.MODE.isChecked():
            py_serial.write(b'6')
            self.Mode_display.clear()
            self.Mode_display.append("Manual")
            self.Fan.setEnabled(True)
            self.Fan_2.setEnabled(True)
            self.LED_MODE.setEnabled(True)
            self.InputWater.setEnabled(True)
            self.OutputWater.setEnabled(True)
            self.Fan.setStyleSheet("background-color:rgb(255, 170, 0);color:rgb(255,255,255);")
            self.Fan_2.setStyleSheet("background-color:rgb(255, 170, 0);color:rgb(255,255,255);")
            self.InputWater.setStyleSheet("background-color:rgb(0, 85, 255);color:rgb(255,255,255);")
            self.OutputWater.setStyleSheet("background-color:rgb(0, 85, 255);color:rgb(255,255,255);")             
            if self.toggle_2 == 2:
                self.LED_MODE.setStyleSheet("background-color:rgb(153,51,255);color:rgb(255,255,255);")
            elif self.toggle_2 == 3:
                self.LED_MODE.setStyleSheet("background-color:rgb(255,0,0);color:rgb(255,255,255);")
            elif self.toggle_2 == 1:
                self.LED_MODE.setStyleSheet("background-color:rgb(192,192,192);color:rgb(255,255,255);")
        else :
            py_serial.write(b'6')
            self.Mode_display.clear()
            self.Mode_display.append("Auto")
            self.Fan.setDisabled(True)
            self.Fan_2.setDisabled(True)
            self.LED_MODE.setDisabled(True)
            self.InputWater.setDisabled(True)
            self.OutputWater.setDisabled(True)
            if(self.DN_flag == True):
                self.LED_MODE.setStyleSheet("background-color:rgb(153,51,255);color:rgb(255,255,255);")
            elif(self.DN_flag == False):
                self.LED_MODE.setStyleSheet("background-color:rgb(192,192,192);color:rgb(255,255,255);")
            self.Fan.setStyleSheet("background-color:rgb(0,0,0);color:rgb(0,0,0);")
            self.Fan_2.setStyleSheet("background-color:rgb(0,0,0);color:rgb(0,0,0);")
            self.InputWater.setStyleSheet("background-color:rgb(0,0,0);color:rgb(0,0,0);")
            self.OutputWater.setStyleSheet("background-color:rgb(0,0,0);color:rgb(0,0,0);")

    def LedModeChange(self):

        if self.toggle_2 == 1:
            py_serial.write(b'5')
            self.LED_MODE.setStyleSheet("background-color:rgb(153,51,255);color:rgb(255,255,255);")
            self.toggle_2 = 2
        elif self.toggle_2 == 2:
            py_serial.write(b'5')
            self.LED_MODE.setStyleSheet("background-color:rgb(255,0,0);color:rgb(255,255,255);")
            self.toggle_2 = 3
        elif self.toggle_2 == 3:
            py_serial.write(b'5')
            self.LED_MODE.setStyleSheet("background-color:rgb(192,192,192);color:rgb(255,255,255);")
            self.toggle_2 = 1

    def clear_clicked(self):

        self.textBrowser.clear()
        
    def back_clicked(self):

        window.close()
        mainsetwindow.show()

    def update_temp_humi_graph(self, temp_float, humi_float): 

                # if self.interval % 60 == 0:
                    
                    self.t=np.append(self.t, self.i)
                    self.signal1=np.append(self.signal1, temp_float)
                    self.signal2=np.append(self.signal2, humi_float)

                    self.signal1 = self.signal1[-30:]
                    self.signal2 = self.signal2[-30:]
                    self.t = self.t[-30:]        

                    graph.MplWidget.canvas.axes.clear()
                    graph.MplWidget.canvas.axes.plot(self.t, self.signal1,color='r',linewidth = '3',marker='*')
                    graph.MplWidget.canvas.axes.grid(True, axis='y')
                    graph.MplWidget.canvas.axes.grid(True, axis='x')
                    graph.MplWidget.canvas.axes.yaxis.set_major_locator(MaxNLocator(10))
                    graph.MplWidget.canvas.axes.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f'))                                                                                                                                                                                                               
                    graph.MplWidget.canvas.axes.set_ylabel('Celsious (°C) ')
                    graph.MplWidget.canvas.axes.set_title('TEMPERATURE DATA ')
                    graph.MplWidget.canvas.draw()

                    graph.MplWidget.canvas2.axes.clear()
                    graph.MplWidget.canvas2.axes.plot(self.t, self.signal2,linewidth = '3',marker='*')
                    graph.MplWidget.canvas2.axes.grid(True, axis='y')
                    graph.MplWidget.canvas2.axes.grid(True, axis='x')          
                    graph.MplWidget.canvas2.axes.set_ylabel('Humidity (%)')
                    graph.MplWidget.canvas2.axes.set_title('HUMIDITY DATA')
                    graph.MplWidget.canvas2.axes.set_ylim([10, 100])
                    graph.MplWidget.canvas2.axes.set_xlabel('Time')
                    graph.MplWidget.canvas2.draw()

                    self.i += 1
                    graph.btn_reset.clicked.connect(self.reset_clicked)
                # self.interval += 1

    def reset_clicked(self):

        graph.MplWidget.canvas.axes.clear()
        graph.MplWidget.canvas2.axes.clear()
        self.t =np.array([],dtype=float)
        self.signal1 =np.array([],dtype=float)
        self.signal2 =np.array([],dtype=float)
        self.i =0
    
class Graphwindow(QWidget,form_class4):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.btn_back.clicked.connect(self.back_clicked)

    def back_clicked(self):

        graph.close()
        mainsetwindow.show()

class MplWidget(QWidget):
    def __init__(self, parent = None):

        QWidget.__init__(self, parent)
        
        self.canvas = FigureCanvas(Figure())
        self.canvas2 = FigureCanvas(Figure())
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        vertical_layout.addWidget(self.canvas2)
       # self.canvas.axes = self.canvas.figure.plot()
     #   self.canvas2.axes = self.canvas2.figure.plot()
        self.setLayout(vertical_layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    mainsetwindow = Mainsetwindow()
    graph = Graphwindow()
    mainsetwindow.show()
    app.exec_()
