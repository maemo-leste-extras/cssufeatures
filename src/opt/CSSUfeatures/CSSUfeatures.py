#!/usr/bin/python

# Copyright (c) 2011 Christos Zamantzas
# Licenced under GPLv2

########################################################################
## CSSU Features Configuration 
##
## Configuration UI for the Community SSU features
## for info on the features it provides access see: 
## http://wiki.maemo.org/Community_SSU/Features
########################################################################

##Author: Christos Zamantzas <christos.zamantzas@gmail.com>

Version = '2.5'

import os
import sys
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
#from PyQt4.QtMaemo5 import *
from CSSUfeaturesUI import *

#############################################################################################################

PathApp             = '/opt/CSSUfeatures/'            # application path
PathSystem          = '/usr/share/hildon-desktop/'    # main path
ConfigSystem        = 'transitions.ini'               # name of system config file
PathTheme           = '/etc/hildon/theme/'            # main path (if themes are in place)
ConfigTheme         = 'transitions.ini'               # name of system config file (if themes are in place)
PathTemp            = '/home/user/.CSSUfeatures/'     # temp path of files
ConfigTempSystem    = 'CSSUfeatures_temp_system'      # name of temp config file from/for system
ConfigTempTheme     = 'CSSUfeatures_temp_theme'       # name of temp config file from/for theme
PathSystemUi        = '/etc/systemui/'                # path to the storage of xml files for the power key menu
ConfigSystemUi      = 'CSSUfeatures.xml'              # name of the applications' xml file for the power key menu
updateSettings      = 'updateTransitions'             # name of the script used to pass root commands

#############################################################################################################

def checkFile(Path, File):
    ''' Check if a file exists. '''

    try:
       f = open(Path + File, 'r')
       f.close()
    except:
       return False
    else:
       return True

def showMessage(message):
    ''' Method to display a message to the user that waits for an action. '''

    os.system('dbus-send --type=method_call --dest=org.freedesktop.Notifications \
               /org/freedesktop/Notifications \
               org.freedesktop.Notifications.SystemNoteDialog \
               string:"%s" uint32:0 string:"OK"' % message)          

def showQuickMessage(message):   
    ''' Method to display shortly a message to the user. '''

    os.system('dbus-send --type=method_call --dest=org.freedesktop.Notifications \
               /org/freedesktop/Notifications \
               org.freedesktop.Notifications.SystemNoteInfoprint \
               string:"%s"' % message)          

def checkConfigFileAvailability():
    ''' Check for configuration files and select which one to be used. '''               

    global Path, Config
    if checkFile(PathTheme,ConfigTheme) == True:
       Path = PathTheme
       Config = ConfigTheme
    elif checkFile(PathSystem,ConfigSystem) == True:
       Path = PathSystem
       Config = ConfigSystem
    else:
       message = 'ERROR: Unable to find any configuration file. Exiting..'
       showMessage(message)
       sys.exit(1)

def checkCSSUinstalled():
    '''Check if the CSSU is installed in the system'''
     
    time.sleep(1)
    if os.popen('if dpkg -l | grep mp-fremantle-community-pr 1>/dev/null; then echo $?;fi').read() == '0\n':
       return True
    else: 
       return False

def checkTactileInstalled():
    '''Check if the Tactile package is installed in the system'''
     
    time.sleep(1)
    if os.popen('if dpkg -l | grep tactile 1>/dev/null; then echo $?;fi').read() == '0\n':
       return True
    else: 
       return False

def copyConfigFile():
    '''Copy the system/theme congiguration files for later editing'''
    
    os.system('cp %s %s' % (PathSystem + ConfigSystem, PathTemp + ConfigTempSystem))
    if checkFile(PathTheme,ConfigTheme) == True: 
       os.system('cp %s %s' % (PathTheme + ConfigTheme, PathTemp + ConfigTempTheme))
       message = 'INFO: The application found a settings file in the theme folder.\nThe application will update both system and theme files with any changes requested.'
       showMessage(message)
    else:
       pass
       
def getCurrent():
    '''Read the values currently in the config file'''

    if checkFile(PathTheme,ConfigTheme) == True:
       Path = PathTheme
       Config = ConfigTheme
       message = 'INFO: Reading the configuration from a theme folder..'
       showMessage(message)
    else:
       Path = PathSystem
       Config = ConfigSystem

    ##define variables to readout
    global dataVars
    dataVars={}
    configVars = ['zoom_on_press', 'parallax', 'blurless', 'blurless_saturation', 'taskswitcher', 'zaxisrotation', 'forcerotation', 'tactilepopups']

    ##readout the variables               
    try:
       f = open(Path + Config, 'r')
       string=f.read().replace(' ','')
       f.close()
       for line in string.splitlines():
          line=line.split('=')
          if line[0] in configVars:
             dataVars[line[0]]=line[1]
    except IOError:
       message = 'ERROR: Reading the configuration settings gave a FATAL ERROR while loading\nConfiguration file does not exist or cannot be read.'
       showMessage(message)
       sys.exit(1)
    except:
       message = 'ERROR: Reading the configuration settings gave a FATAL ERROR while loading\nSettings are corrupted.'
       showMessage(message)
       sys.exit(1)
       
    ##Check if variables exist in the file
    global fixNeeded
    fixNeeded = 'false'

    if 'zoom_on_press' not in dataVars: 
       fixNeeded = 'true'
    elif 'parallax' not in dataVars: 
       fixNeeded = 'true'
    elif 'blurless' not in dataVars: 
       fixNeeded = 'true'
    elif 'blurless_saturation' not in dataVars: 
       fixNeeded = 'true'
    elif 'taskswitcher' not in dataVars:
       fixNeeded = 'true'
    elif 'zaxisrotation' not in dataVars: 
       fixNeeded = 'true'
    elif 'forcerotation' not in dataVars: 
       fixNeeded = 'true'
    elif 'tactilepopups' not in dataVars: 
       fixNeeded = 'true'
    else: 
       fixNeeded = 'false'
   
def doUpdateConfigSystem():            
    ''' Update the config file of the system with the edited. '''

    time.sleep(1)
    try:
       os.system('sudo %s%s copyTempSystem' % (PathApp, updateSettings))
    except:
       return False
    else: 
       return True

def doUpdateConfigTheme():            
    ''' Update the config file of the theme with the edited. '''

    time.sleep(1)
    try:
       os.system('sudo %s%s copyTempTheme' % (PathApp, updateSettings))
    except:
       return False
    else: 
       return True

class CSSUfeaturesFixConfig(QMainWindow):

    def __init__(self, parent=None):
       QMainWindow.__init__(self,parent)
       self.parent = parent
       #self.setAttribute(Qt.WA_Maemo5AutoOrientation, True)
       self.window().setProperty("X-Maemo-Orientation", 2)
       #self.setAttribute(Qt.WA_Maemo5StackedWindow, True)
       self.window().setProperty("X-Maemo-StackedWindow", 1)

       self.setWindowTitle("Missing Configuration")
       self.showFullScreen()

       aboutScrollArea = QScrollArea(self)
       aboutScrollArea.setWidgetResizable(True)
       awidget = QWidget(aboutScrollArea)
       awidget.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
       aboutScrollArea.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
       try:
          QtWidgets.QScroller.grabGesture(aboutScrollArea.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture)
          #scroller = aboutScrollArea.property("kineticScroller").toPyObject()
          #scroller.setEnabled(True)
       except:
          pass

       aboutLayout = QVBoxLayout(awidget)

       aboutIcon = QLabel()
       aboutIcon.setPixmap( QIcon.fromTheme('CSSUfeatures').pixmap(64,64) )
       aboutIcon.setAlignment( Qt.AlignCenter or Qt.AlignHCenter )
       #aboutIcon.resize(128,128)
       aboutLayout.addWidget(aboutIcon)

       aboutLabel = QLabel('''<b>Warning: </b>The transitions.ini file in this system does not have all the expected options. <br> <br> <b>Disclaimer: </b>A repair operation can be initiated but the result cannot be guaranteed. That is, the system might enter in a reboot loop and a reflash of the OS might be needed. The safest option is to choose the restoration of the default file.''')
       aboutLabel.setWordWrap(True)
       aboutLabel.setAlignment( Qt.AlignCenter or Qt.AlignHCenter )
       aboutLayout.addWidget(aboutLabel)
       
       self.buttonFixConfig = QPushButton('Fix Config')
       self.buttonFixConfig.clicked.connect(self.fixConfigVariables)
       self.buttonRestoreConfig = QPushButton('Restore Default')
       self.buttonRestoreConfig.clicked.connect(self.restoreDefaultConfigFile)
       self.buttonExit = QPushButton('Exit')
       self.buttonExit.clicked.connect(self.cancel)

       awidget2 = QWidget()
       buttonLayout = QHBoxLayout(awidget2)        
       buttonLayout.addWidget(self.buttonFixConfig)
       buttonLayout.addWidget(self.buttonRestoreConfig)
       aboutLayout.addWidget(awidget2)

       awidget3 = QWidget()
       buttonLayout = QHBoxLayout(awidget3)
       buttonLayout.addWidget(self.buttonExit)
       aboutLayout.addWidget(awidget3)
        
       awidget.setLayout(aboutLayout)
       aboutScrollArea.setWidget(awidget)
       self.setCentralWidget(aboutScrollArea)
       
       self.show()        
    
    def cancel(self):
       
       sys.exit(1)

    def fixConfigVariables(self): ##FIXME: make a loop on variables than this spaghetti code!
       
       if Path == PathSystem:
          configLocation = 'configSystem'
       elif Path == PathTheme:
          configLocation = 'configTheme'
       else: 
          configLocation = ''
       print "fixing config file: ", configLocation
          
       message = 'Start of fixing\n'
       if 'zoom_on_press' not in dataVars:
          os.system('sudo %s%s addzoom_on_press %s' % (PathApp, updateSettings, configLocation))
          message += 'WARNING: Added the zoom_on_press option..\n'
          print message
       else:
          print 'zoom_on_press exists!!'

       if 'parallax' not in dataVars:
          os.system('sudo %s%s addparallax %s' % (PathApp, updateSettings, configLocation))
          message += 'WARNING: Added the parallax option..\n'
          print message
       else:
          print 'parallax exists!!'

       if 'blurless' not in dataVars:
          os.system('sudo %s%s addblurless %s' % (PathApp, updateSettings, configLocation))
          message += 'WARNING: Added the blurless option..\n'
          print message
       else:
          print 'blurless exists!!'
                      
       if 'blurless_saturation' not in dataVars:
          os.system('sudo %s%s addblurless_saturation %s' % (PathApp, updateSettings, configLocation))
          message += 'WARNING: Added the blurless_saturation option..\n'
          print message
       else:
          print 'blurless_saturation exists!!'
                      
       if 'taskswitcher' not in dataVars:
          os.system('sudo %s%s addtaskswitcher %s' % (PathApp, updateSettings, configLocation))
          message += 'WARNING: Added the taskswitcher option..\n'
          print message
       else:
          print 'taskswitcher exists!!'
                      
       if 'zaxisrotation' not in dataVars:
          os.system('sudo %s%s addzaxisrotation %s' % (PathApp, updateSettings, configLocation))
          message += 'WARNING: Added the zaxisrotation option..\n'
          print message
       else:
          print 'zaxisrotation exists!!'
                      
       if 'forcerotation' not in dataVars:
          os.system('sudo %s%s addforcerotation %s' % (PathApp, updateSettings, configLocation))
          message += 'WARNING: Added the forcerotation option..\n'
          print message
       else:
          print 'forcerotation exists!!'
                      
       if 'tactilepopups' not in dataVars:
          os.system('sudo %s%s addtactilepopups %s' % (PathApp, updateSettings, configLocation))
          message += 'WARNING: Added the tactilepopups option..\n'
          print message
       else:
          print 'tactilepopups exists!!'

       message += 'End of fixing\n\n'
       message += 'The application will now exit..'
       showMessage(message)
       # getCurrent()
       # copyConfigFile()
       time.sleep(5)
       # self.close()   
       sys.exit(1)

    def restoreDefaultConfigFile(self):
       ''' Restore the default configuration file.'''
      
       try:
          os.system('sudo %s%s copyDefault' % (PathApp, updateSettings))
       except:
          message = 'ERROR: The default transitions.ini file could not be restored to the system.\n\n'
       else: 
          message = 'The default transitions.ini file have been restored to the system.\nINFO: Some of its settings will appear on the next reboot.\n\n'

       message += 'The application will now exit..'
       showMessage(message)
       # getCurrent()
       # copyConfigFile()
       time.sleep(5)
       # self.close()   
       sys.exit(1)

class CSSUfeaturesAbout(QMainWindow):
    '''About Window'''
    def __init__(self, parent=None):
       QMainWindow.__init__(self,parent)
       self.parent = parent
       #self.setAttribute(Qt.WA_Maemo5AutoOrientation, True)
       self.window().setProperty("X-Maemo-Orientation", 2)
       #self.setAttribute(Qt.WA_Maemo5StackedWindow, True)
       self.window().setProperty("X-Maemo-StackedWindow", 1)
       self.setWindowTitle("About CSSU Features Configuration")

       aboutScrollArea = QScrollArea(self)
       aboutScrollArea.setWidgetResizable(True)
       awidget = QWidget(aboutScrollArea)
       #awidget.setMinimumSize(470,1000)
       awidget.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
       aboutScrollArea.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
       #Kinetic scroller is available on Maemo and should be on meego
       try:
          QtWidgets.QScroller.grabGesture(aboutScrollArea.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture)
          #scroller = aboutScrollArea.property("kineticScroller").toPyObject()
          #scroller.setEnabled(True)
       except:
          pass

       aboutLayout = QVBoxLayout(awidget)

       aboutIcon = QLabel()
       aboutIcon.setPixmap( QIcon.fromTheme('CSSUfeatures').pixmap(128,128))
       aboutIcon.resize(128,128)
       aboutIcon.setAlignment( Qt.AlignCenter or Qt.AlignHCenter )
       aboutLayout.addWidget(aboutIcon)

       aboutLabel = QLabel('''<center><b>CSSU Features Configuration</b> %s 
       <br><br><b>The CSSU Features application is a user interface to the configuration of several system parameters enabled by the Community SSU updates.</b>
       <br><br>Licenced under GPLv2
       <br>by <b>Christos Zamantzas</b> (Saturn)
       <br><br>It provides the ability to change a number of parameter values by modifing several options in the transitions.ini configuration file as well as in the GConf configuration system.
       <br><br><b>Additional information on the usage, settings and implications can be found in the wiki page</b>
       <br><br>Thanks go to: <b>Benoit HERVIER</b> at http://khertan.net/ for the example code used in this about window and the pyPackager utility.<br></center>''' % Version)
       aboutLabel.setWordWrap(True)
       aboutLabel.setAlignment( Qt.AlignCenter or Qt.AlignHCenter )
       aboutLayout.addWidget(aboutLabel)
       
       self.bugtracker_button = QPushButton('BugTracker')
       self.bugtracker_button.clicked.connect(self.open_bugtracker)
       self.website_button = QPushButton('Wiki Page')
       self.website_button.clicked.connect(self.open_website)
       awidget2 = QWidget()
       buttonLayout = QHBoxLayout(awidget2)        
       buttonLayout.addWidget(self.bugtracker_button)
       buttonLayout.addWidget(self.website_button)
       aboutLayout.addWidget(awidget2)
        
       awidget.setLayout(aboutLayout)
       aboutScrollArea.setWidget(awidget)
       self.setCentralWidget(aboutScrollArea)
       self.show()        
        
    def open_website(self):
       QDesktopServices.openUrl(QUrl('http://wiki.maemo.org/CSSU_Features_Configuration_Editor'))
    def open_bugtracker(self):
       QDesktopServices.openUrl(QUrl('https://bugs.maemo.org'))

class CSSUfeaturesMainWindow(QMainWindow):
    def __init__(self, parent=None):
       
       ##Build parent user interface
       QWidget.__init__(self, parent)
       self.ui = Ui_CSSUfeaturesUI()
       self.ui.setupUi(self)
       #self.setAttribute(Qt.WA_Maemo5AutoOrientation, True)
       self.window().setProperty("X-Maemo-Orientation", 2)
       #self.setAttribute(Qt.WA_Maemo5StackedWindow, True)
       self.window().setProperty("X-Maemo-StackedWindow", 1)
       
       ##Connect the GUI Buttons with actions
       ##Create Settings
       self.ui.btnCreateConfig.clicked.connect(self.doCreateConfig)
       self.ui.btnSetCurrent.clicked.connect(self.doSetCurrent)
       self.ui.btnSetDefault.clicked.connect(self.doSetDefault)
       
       ##Connect Menu Buttons 
       self.ui.actionQuit.triggered.connect(QtWidgets.qApp.quit)

       self.ui.actionAbout.triggered.connect(self.showAbout)
       self.ui.actionRestoreDefaults.triggered.connect(self.restoreDefaultConfigFile)
       self.ui.actionRebootDevice.triggered.connect(self.rebootDevice)
       self.ui.actionAddPowerKeyEntry.triggered.connect(self.addPowerKeyEntry)
       self.ui.actionRemovePowerKeyEntry.triggered.connect(self.removePowerKeyEntry)

         ##Enable only the valid menu entry 
       if checkFile(PathSystemUi, ConfigSystemUi) == True:
          self.ui.actionAddPowerKeyEntry.setEnabled(False)
       else:
          self.ui.actionRemovePowerKeyEntry.setEnabled(False)
       
       ##Check which config file to use.
       checkConfigFileAvailability()
       ##Get the values from the configuration file.
       getCurrent()
       
       ##Check if all values exist
       if fixNeeded == 'true':   
          print "fix is needed"
          self.fixConfigFileVariables()
       else:
          self.doSetCurrent()

       QtWidgets.QScroller.grabGesture(self.ui.scrollArea.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture)

    #def changeEvent(self, event):
    #   # TODO: this needs fixing
    #   print('event', event, event.type())
    #   if event.type() == QEvent.ActivationChange:
    #       print('windowActivate')
    #       QtWidgets.QScroller.grabGesture(self.ui.scrollArea.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture)

    #   QtWidgets.QWidget.changeEvent(self, event)
          
    ##Create Methods

    def showAbout(self):
  
       stackwindow = CSSUfeaturesAbout(self)
       stackwindow.show()

    def addPowerKeyEntry(self):
       '''Add entry in the Power Key menu'''
       
       os.system('sudo %s%s addPowerKeyEntry' % (PathApp, updateSettings) )
       self.ui.actionAddPowerKeyEntry.setEnabled(False)
       self.ui.actionRemovePowerKeyEntry.setEnabled(True)
       os.system('sudo %s%s updatePowerKeyEntry' % (PathApp, updateSettings) )
       message = 'Added entry in the Power Key Menu'
       showQuickMessage(message)

    def removePowerKeyEntry(self):
       '''Remove entry from the Power Key menu'''

       os.system('sudo %s%s deletePowerKeyEntry' % (PathApp, updateSettings) )
       self.ui.actionAddPowerKeyEntry.setEnabled(True)
       self.ui.actionRemovePowerKeyEntry.setEnabled(False)
       os.system('sudo %s%s updatePowerKeyEntry' % (PathApp, updateSettings) )
       message = 'Removed entry from the Power Key Menu'
       showQuickMessage(message)

    def restoreDefaultConfigFile(self):
       ''' Restore the default configuration file.'''
       
       message = 'Please wait. Update in progress..'
       showQuickMessage(message)
       
       try:
          os.system('sudo %s%s copyDefault' % (PathApp, updateSettings))
       except:
          message = 'WARNING: The default transitions.ini file could not be restored to the system.'
       else: 
          message = 'The default transitions.ini file have been restored to the system.\n\nINFO: Some of its settings will appear on the next reboot.'
       showMessage(message)

    def rebootDevice(self):
       '''Reboot Device for the settings to take effect.'''
       
       message = 'INFO: Device is going to be restarted.\nThe application is exiting..'
       showQuickMessage(message)
       
       os.system('sudo %s%s rebootDevice &' % (PathApp, updateSettings))
       sys.exit(1)

    def doSetCurrent(self):
       ''' Set CURRENT values in the GUI''' 
       
       ##Check if the tactile package is installed
       if checkTactileInstalled() == False:
          self.ui.comboBoxTactile.setEnabled(False)
       else:
          pass
          
       ##Get the values from the configuration file.
       getCurrent()
          
       ##Set them in the GUI.
       try:
          self.ui.comboBoxZoomPress.setCurrentIndex(int(dataVars['zoom_on_press']))
          self.ui.comboBoxBlurless.setCurrentIndex(int(dataVars['blurless']))
          self.ui.comboBoxBlurlessSaturation.setCurrentIndex(int(dataVars['blurless_saturation']))
          self.ui.comboBoxTaskSwitcher.setCurrentIndex(int(dataVars['taskswitcher']))
          self.ui.comboBoxRotationAxis.setCurrentIndex(int(dataVars['zaxisrotation']))
          self.ui.comboBoxForcedRotation.setCurrentIndex(int(dataVars['forcerotation']))
          self.ui.comboBoxTactile.setCurrentIndex(int(dataVars['tactilepopups']))
          self.ui.doubleSpinBoxParallax.setValue(float(dataVars['parallax']))
      
          message = 'The CURRENT configuration options are shown.'
          showQuickMessage(message)
       except:
          message = 'ERROR: Reading the configuration settings gave a FATAL ERROR while loading the transitions.ini file. Not all settings are available.\n\nExiting..'
          showMessage(message)
          sys.exit(1)
           
       try:
          FMTX = os.popen('gconftool-2 -g /apps/osso/maemo-statusmenu-fmtx/always_visible').read()
          AppMenuEditor = os.popen('gconftool-2 -g /apps/osso/hildon-desktop/menu_edit_disabled').read()
          DesktopEditor = os.popen('gconftool-2 -g /apps/osso/hildon-desktop/key-actions/disable_edit').read()
          RowsStatusMenu = os.popen('gconftool-2 -g /apps/osso/hildon-status-menu/view/number_of_rows').read()
          RowsStatusMenuPortrait = os.popen('gconftool-2 -g /apps/osso/hildon-status-menu/view/number_of_rows_portrait').read()
          DesktopScroll = os.popen('gconftool-2 -g /apps/osso/hildon-desktop/scroll_vertical').read()
           
          # print FMTX, AppMenuEditor, DesktopEditor, DesktopScroll, RowsStatusMenu, RowsStatusMenuPortrait
           
          if FMTX == 'false\n':
             self.ui.comboBoxFMTX.setCurrentIndex(0)
          else:
             self.ui.comboBoxFMTX.setCurrentIndex(1)
          if AppMenuEditor == 'false\n':
             self.ui.comboBoxAppMenuEditor.setCurrentIndex(0)
          else:
             self.ui.comboBoxAppMenuEditor.setCurrentIndex(1)
          if DesktopEditor == 'false\n':
             self.ui.comboBoxDesktopEditor.setCurrentIndex(0)
          else:   
             self.ui.comboBoxDesktopEditor.setCurrentIndex(1)
          if DesktopScroll == 'false\n':
             self.ui.comboBoxDesktopScroll.setCurrentIndex(0)
          else:   
             self.ui.comboBoxDesktopScroll.setCurrentIndex(1)

          self.ui.doubleSpinBoxRowsStatusMenu.setValue(int(RowsStatusMenu))
          self.ui.doubleSpinBoxRowsStatusMenuPortrait.setValue(int(RowsStatusMenuPortrait))
       except:
          message = 'ERROR: Reading the configuration settings gave a FATAL ERROR while reading the gconf values. Not all settings are available.\n\nExiting..'
          showMessage(message)
          sys.exit(1)
       
    def doSetDefault(self):  
       '''Set DEFAULT values in the GUI''' 

       self.ui.comboBoxBlurless.setCurrentIndex(0)
       self.ui.comboBoxBlurlessSaturation.setCurrentIndex(0)
       self.ui.comboBoxTaskSwitcher.setCurrentIndex(0)
       self.ui.comboBoxRotationAxis.setCurrentIndex(0)
       self.ui.comboBoxForcedRotation.setCurrentIndex(0)
       self.ui.comboBoxTactile.setCurrentIndex(0)
       self.ui.comboBoxZoomPress.setCurrentIndex(0)
       self.ui.doubleSpinBoxParallax.setValue(float('1.3'))
       self.ui.comboBoxFMTX.setCurrentIndex(0)
       self.ui.comboBoxAppMenuEditor.setCurrentIndex(0)
       self.ui.comboBoxDesktopEditor.setCurrentIndex(0)
       self.ui.comboBoxDesktopScroll.setCurrentIndex(0)
       self.ui.doubleSpinBoxRowsStatusMenu.setValue(int('6'))
       self.ui.doubleSpinBoxRowsStatusMenuPortrait.setValue(int('8'))

       message = 'The DEFAULT configuration options are shown.'
       showQuickMessage(message)
          
    def doCreateConfig(self):        
       '''Create the new configuration file'''
       
       message = 'Please wait. Update in progress..'
       showQuickMessage(message)

       ##Read GUI.
       Blurless            = self.ui.comboBoxBlurless.currentIndex()
       BlurlessSaturation  = self.ui.comboBoxBlurlessSaturation.currentIndex()
       TaskSwitcher        = self.ui.comboBoxTaskSwitcher.currentIndex()
       RotationAxis        = self.ui.comboBoxRotationAxis.currentIndex()
       ForcedRotation      = self.ui.comboBoxForcedRotation.currentIndex()
       Tactile             = self.ui.comboBoxTactile.currentIndex()
       ZoomPress           = self.ui.comboBoxZoomPress.currentIndex()
       Parallax            = self.ui.doubleSpinBoxParallax.value()

       if self.ui.comboBoxFMTX.currentIndex() == 0:
          FMTX = 'false'
       else:
          FMTX = 'true'    
       if self.ui.comboBoxAppMenuEditor.currentIndex() == 0:
          AppMenuEditor = 'false'
       else:    
          AppMenuEditor = 'true'
       if self.ui.comboBoxDesktopEditor.currentIndex() == 0:
          DesktopEditor = 'false'
       else:
          DesktopEditor = 'true'
       if self.ui.comboBoxDesktopScroll.currentIndex() == 0:
          DesktopScroll = 'false'
       else:
          DesktopScroll = 'true'
          
       RowsStatusMenu = self.ui.doubleSpinBoxRowsStatusMenu.value()
       RowsStatusMenuPortrait = self.ui.doubleSpinBoxRowsStatusMenuPortrait.value()
       
       ##Update of the gconf entries
       os.system('gconftool-2 -s /apps/osso/maemo-statusmenu-fmtx/always_visible -t bool %s' % FMTX)
       os.system('gconftool-2 -s /apps/osso/hildon-desktop/menu_edit_disabled -t bool %s' % AppMenuEditor)
       os.system('gconftool-2 -s /apps/osso/hildon-desktop/key-actions/disable_edit -t bool %s' % DesktopEditor)
       os.system('gconftool-2 -s /apps/osso/hildon-status-menu/view/number_of_rows -t int %s' % RowsStatusMenu)
       os.system('gconftool-2 -s /apps/osso/hildon-status-menu/view/number_of_rows_portrait -t int %s' % RowsStatusMenuPortrait)
       os.system('gconftool-2 -s /apps/osso/hildon-desktop/scroll_vertical -t bool %s' % DesktopScroll)
       
       ##Update of the System config file.
       os.rename( PathTemp + ConfigTempSystem, PathTemp + ConfigTempSystem + "~" )
       destination = open( PathTemp + ConfigTempSystem, "w" )
       source = open( PathTemp + ConfigTempSystem + "~", "r" )
       for Line in source:
          if   Line.startswith("zoom_on_press"):
             destination.write('zoom_on_press = %s\n' % ZoomPress)
          elif Line.startswith("parallax"):
             destination.write('parallax = %s\n' % Parallax)
          elif Line.startswith("blurless ") or Line.startswith("blurless="):
             destination.write('blurless = %s\n' % Blurless)
          elif Line.startswith("blurless_saturation"):
             destination.write('blurless_saturation = %s\n' % BlurlessSaturation)
          elif Line.startswith("taskswitcher"):
             destination.write('taskswitcher = %s\n' % TaskSwitcher)
          elif Line.startswith("zaxisrotation"):
             destination.write('zaxisrotation = %s\n' % RotationAxis)
          elif Line.startswith("forcerotation"):
             destination.write('forcerotation = %s\n' % ForcedRotation)
          elif Line.startswith("tactilepopups"):
             destination.write('tactilepopups = %s\n' % Tactile)
          else: 
             destination.write( Line )
       source.close()
       destination.close()

       doUpdateConfigSystem()
       message = 'The new settings have been successfully saved.'
       
       ##Update of the Theme config file (if it exists).
       if checkFile(PathTheme,ConfigTheme) == True:

          os.rename( PathTemp + ConfigTempTheme, PathTemp + ConfigTempTheme + "~" )
          destination = open( PathTemp + ConfigTempTheme, "w" )
          source = open( PathTemp + ConfigTempTheme + "~", "r" )
          for Line in source:
             if   Line.startswith("zoom_on_press"):
                destination.write('zoom_on_press = %s\n' % ZoomPress)
             elif Line.startswith("parallax"):
                destination.write('parallax = %s\n' % Parallax)
             elif Line.startswith("blurless ") or Line.startswith("blurless="):
                destination.write('blurless = %s\n' % Blurless)
             elif Line.startswith("blurless_saturation"):
                destination.write('blurless_saturation = %s\n' % BlurlessSaturation)
             elif Line.startswith("taskswitcher"):
                destination.write('taskswitcher = %s\n' % TaskSwitcher)
             elif Line.startswith("zaxisrotation"):
                destination.write('zaxisrotation = %s\n' % RotationAxis)
             elif Line.startswith("forcerotation"):
                destination.write('forcerotation = %s\n' % ForcedRotation)
             elif Line.startswith("tactilepopups"):
                destination.write('tactilepopups = %s\n' % Tactile)
             else: 
                destination.write( Line )
          source.close()
          destination.close()
       
          doUpdateConfigTheme()
          message = 'The new settings have been successfully saved to the system and theme folders.'

       showQuickMessage(message)

    def fixConfigFileVariables(self): 
       '''show window with fix options'''
       
       stackwindow = CSSUfeaturesFixConfig(self)
       stackwindow.show()

class CSSUfeaturesMain(): 
     
    ##Check with what priviledges the GUI has been executed
    if os.geteuid() == 0:
       message = 'ERROR: The CSSU Features Configuration application cannot be executed as root. Exiting..'
       showMessage(message)
       sys.exit(1)
    else:
       pass
    
    ##Check if CSSU is installed
    #if checkCSSUinstalled() == False:
    #   message = 'WARNING: The Community SSU is not installed.\nSome features might not work correctly..'
    #   showMessage(message)
    #   #sys.exit(1)
    #else:
    #   pass
     
    ##Check if temp folder is available
    if os.path.exists(PathTemp) == False:
       os.system('mkdir %s' % PathTemp)
    else:
       pass
     
    ##Copy the system/theme congiguration files for later editing
    copyConfigFile()
    
    ##Open Main Window
    app = QApplication(sys.argv)
    myapp = CSSUfeaturesMainWindow()
    myapp.show()
    sys.exit(app.exec_())
