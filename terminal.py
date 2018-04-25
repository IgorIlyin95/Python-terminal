# Terminal with filters and gain
# Terminal with filters for visualization signal from ELEMIO sensor (version for Arduino)
# 2018-04-18 by ELEMIO (https://github.com/eadf)
# 
# Changelog:
#     2018-04-18 - initial release

# Code is placed under the MIT license
# Copyright (c) 2018 ELEMIO
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ===============================================

from PyQt5 import QtCore, QtWidgets, QtGui
import sys
import serial
import pyqtgraph as pg
import numpy as np
import time
from scipy.signal import butter, lfilter

# Main window
class MYO(QtWidgets.QMainWindow):
    # Initialize constructor
    def __init__(self):
          super(MYO, self).__init__()
          self.initUI()
    # Custom constructor
    def initUI(self): 
        self.setWindowTitle("MYO")
        # Values
        COM = "COM23"
        self.l = 1 #Current point
        self.dt = 1 #Update time in ms
        self.fs = 1 / self.dt #Sample frequency
        self.passLowFrec = 30.0 #Low frequency for passband filter
        self.passHighFrec = 100.0 #Low frequency for passband filter
        self.stopLowFrec = 40.0 #High frequency for stopband filter
        self.stopHighFrec = 60.0 #Low frequency for stopband filter
        self.Time = np.array([0]) #Tine array
        self.Data1 = np.array([0]) #Data array
        self.dataWidth = 20000 #Maximum count of data points
        self.timeWidth = 10 #Time width of plot
        # Menu panel
        startAction = QtGui.QAction(QtGui.QIcon('img/start.png'), 'Start', self)
        startAction.setShortcut('Ctrl+O')
        startAction.triggered.connect(self.start)
        stopAction = QtGui.QAction(QtGui.QIcon('img/pause.png'), 'Stop', self)
        stopAction.setShortcut('Ctrl+P')
        stopAction.triggered.connect(self.stop)
        exitAction = QtGui.QAction(QtGui.QIcon('img/out.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        # Toolbar
        toolbar = self.addToolBar('Tool')
        toolbar.addAction(startAction)
        toolbar.addAction(stopAction)
        toolbar.addAction(exitAction)
        # Plot widget
        self.pw = pg.PlotWidget(background = (35 , 35, 35, 255))
        self.pw.showGrid(x = True, y = True, alpha = 0.7) 
        self.p1 = self.pw.plot()
        self.p1.setPen(color=(255,255*0.2,255*0.2), width=1)
        # Styles
        centralStyle = "color: rgb(255, 255, 255); background-color: rgb(35, 35, 35);"
        editStyle = "border-style: solid; border-width: 1px;"
        # Settings zone
        gainText = QtWidgets.QLabel("GAIN")
        filtersText = QtWidgets.QLabel("FILTERS")
        updateText = QtWidgets.QLabel("TIME UPDATE (IN MS): ")
        passLowFrecText = QtWidgets.QLabel("LOW FREQUENCY: ")
        passHighFrecText = QtWidgets.QLabel("HIGH FREQUENCY: ")
        stopLowFrecText = QtWidgets.QLabel("LOW FREQUENCY: ")
        stopHighFrecText = QtWidgets.QLabel("HIGH FREQUENCY: ")
        self.timeUpdate = QtWidgets.QLineEdit('1', self)
        self.timeUpdate.setMaximumWidth(100)
        self.timeUpdate.setStyleSheet(editStyle)
        self.passLowFreq = QtWidgets.QLineEdit('30', self)
        self.passLowFreq.setMaximumWidth(100)
        self.passLowFreq.setStyleSheet(editStyle)
        self.passHighFreq = QtWidgets.QLineEdit('100', self)
        self.passHighFreq.setMaximumWidth(100)
        self.passHighFreq.setStyleSheet(editStyle)
        self.stopLowFreq = QtWidgets.QLineEdit('40', self)
        self.stopLowFreq.setMaximumWidth(100)
        self.stopLowFreq.setStyleSheet(editStyle)
        self.stopHighFreq = QtWidgets.QLineEdit('60', self)
        self.stopHighFreq.setMaximumWidth(100)
        self.stopHighFreq.setStyleSheet(editStyle)
        self.bandpass = QtWidgets.QCheckBox("BANDPASS")
        self.bandstop = QtWidgets.QCheckBox("BANDSTOP")
        gainx1 = QtWidgets.QRadioButton('x1')
        gainx1.setChecked(True)
        gainx1.Value = 1
        gainx2 = QtWidgets.QRadioButton('x2')
        gainx2.Value = 2
        gainx4 = QtWidgets.QRadioButton('x4')
        gainx4.Value = 4
        gainx5 = QtWidgets.QRadioButton('x5')
        gainx5.Value = 5
        gainx8 = QtWidgets.QRadioButton('x8')
        gainx8.Value = 8
        gainx10 = QtWidgets.QRadioButton('x10')
        gainx10.Value = 10
        gainx16 = QtWidgets.QRadioButton('x16')
        gainx16.Value = 16
        gainx32 = QtWidgets.QRadioButton('x32')
        gainx32.Value = 32
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.addButton(gainx1)
        self.button_group.addButton(gainx2)
        self.button_group.addButton(gainx4)
        self.button_group.addButton(gainx5)
        self.button_group.addButton(gainx8)
        self.button_group.addButton(gainx10)
        self.button_group.addButton(gainx16)
        self.button_group.addButton(gainx32)
        self.button_group.buttonClicked.connect(self._on_radio_button_clicked)
        # Main widget
        centralWidget = QtWidgets.QWidget()
        centralWidget.setStyleSheet(centralStyle)
        # Image logo
        logo = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap('img/logo.png')
        logo.setPixmap(pixmap)
        # Layout
        vbox = QtWidgets.QHBoxLayout()
        hbox = QtWidgets.QVBoxLayout()
        hbox.addWidget(logo)
        hbox.addWidget(self.pw)
        gainLayout = QtWidgets.QGridLayout()
        gainLayout.addWidget(gainx1,0,0)
        gainLayout.addWidget(gainx2,0,1)
        gainLayout.addWidget(gainx4,0,2)
        gainLayout.addWidget(gainx5,1,0)
        gainLayout.addWidget(gainx8,1,1)
        gainLayout.addWidget(gainx10,1,2)
        gainLayout.addWidget(gainx16,2,0)
        gainLayout.addWidget(gainx32,2,1) 
        layout = QtWidgets.QGridLayout()
        layout.addWidget(gainText,0,0) 
        layout.addWidget(filtersText,0,1) 
        layout.addWidget(updateText,0,2) 
        layout.addWidget(self.timeUpdate,0,3) 
        layout.addLayout(gainLayout,1,0,2,1)
        layout.addWidget(self.bandpass,1,1) 
        layout.addWidget(passLowFrecText,1,2)
        layout.addWidget(self.passLowFreq,1,3) 
        layout.addWidget(passHighFrecText,1,4) 
        layout.addWidget(self.passHighFreq,1,5)  
        layout.addWidget(self.bandstop,2,1) 
        layout.addWidget(stopLowFrecText,2,2) 
        layout.addWidget(self.stopLowFreq,2,3) 
        layout.addWidget(stopHighFrecText,2,4) 
        layout.addWidget(self.stopHighFreq,2,5) 
        hbox.addLayout(layout)
        vbox.addLayout(hbox)
        centralWidget.setLayout(vbox)
        self.setCentralWidget(centralWidget)  
        self.showMaximized()
        self.show()
        # Serial monitor
        self.monitor = SerialMonitor(COM)
        self.monitor.bufferUpdated.connect(self.updateListening, QtCore.Qt.QueuedConnection)
    # Start working
    def start(self):
        self.monitor.running = True
        self.monitor.start()
    # Pause
    def stop(self):
        self.monitor.running = False       
    # Update
    def updateListening(self, msg):
        # Update variables
        self.dt = float(self.timeUpdate.text()) / 1000;
        self.fs = 1 / self.dt
        self.passLowFrec = float(self.passLowFreq.text())
        self.passHighFrec = float(self.passHighFreq.text())
        self.stopLowFrec = float(self.stopLowFreq.text())
        self.stopHighFrec = float(self.stopHighFreq.text())
        # Parsing data from serial buffer
        msg = msg.decode()
        l_old = self.l
        for s in msg.split('\r\n'):
            if (s != '') :
                self.Data1 = np.append(self.Data1, int(s))
                self.Time = np.append(self.Time, self.Time[self.l-1] + self.dt)
                self.l = self.l + 1
        self.Data1[l_old] = self.Data1[l_old + 1] #Delete extra information
        self.Data1[self.l-1] = self.Data1[self.l-2]
        if ( len(self.Data1) > self.dataWidth) :
            index = list(range(0, len(self.Data1) - self.dataWidth))
            self.Data1 = np.delete(self.Data1, index)
            self.Time = np.delete(self.Time, index)
            self.l = self.l - len(index)
        # Filtering
        if self.bandpass.isChecked() == 1 and self.bandstop.isChecked() == 0:
            Data = self.butter_bandpass_filter(self.Data1, self.passLowFrec, self.passHighFrec, self.fs)
        if self.bandpass.isChecked() == 0 and self.bandstop.isChecked() == 1:
            Data = self.butter_bandstop_filter(self.Data1, self.stopLowFrec, self.stopHighFrec, self.fs)
        if self.bandpass.isChecked() == 1 and self.bandstop.isChecked() == 1:
            Data_temp = self.butter_bandpass_filter(self.Data1, self.passLowFrec, self.passHighFrec, self.fs)
            Data = self.butter_bandstop_filter(Data_temp, self.stopLowFrec, self.stopHighFrec, self.fs)
        if self.bandpass.isChecked() == 0 and self.bandstop.isChecked() == 0:
            Data = self.Data1
        # Shift the boundaries of the graph
        timeCount = self.Time[self.l-1] // self.timeWidth
        # Update plot
        self.pw.setXRange(self.timeWidth * timeCount, self.timeWidth * ( timeCount + 1))
        self.p1.setData(y=Data, x=self.Time)
    # Values for butterworth bandpass filter
    def butter_bandpass(self, lowcut, highcut, fs, order=2):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype = 'bandpass')
        return b, a
    # Butterworth bandpass filter
    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=3):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y
    # Values for butterworth bandstop filter
    def butter_bandstop(self, lowcut, highcut, fs, order=2):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype = 'bandstop')
        return b, a
    # Butterworth bandstop filter
    def butter_bandstop_filter(self, data, lowcut, highcut, fs, order=3):
        b, a = self.butter_bandstop(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y
    # Change gain
    def _on_radio_button_clicked(self, button):
        self.monitor.ser.write(bytearray([button.Value]))
    # Exit event
    def closeEvent(self, event):
        self.monitor.ser.close()
        event.accept()
        
# Serial monitor class
class SerialMonitor(QtCore.QThread):
    bufferUpdated = QtCore.pyqtSignal(bytes)
    # Custom constructor
    def __init__(self, COM):
        QtCore.QThread.__init__(self)
        self.ser = serial.Serial(COM, 115200)
        self.running = False
        self.filter = False
    # Listening port
    def run(self):
        while self.running is True:
            # Waiting for data
            while (self.ser.inWaiting() == 0):
                pass
            # Reading data
            msg = self.ser.read( self.ser.inWaiting() )
            if msg:
                # Parsing data
                self.bufferUpdated.emit(msg)
                time.sleep(0.05)
                
# Starting program       
if __name__ == '__main__':
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    window = MYO()
    window.show()
    sys.exit(app.exec_())