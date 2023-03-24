import sys, time, logging
import serial

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *


# logging config
logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{'
)


APP_VERSION = 0.1

CONTROLLER_PORT = 'COM3'

controller_found = True
try:
    # ser_controller = serial.Serial(CONTROLLER_PORT, 57600, timeout=0)
    time.sleep(1)
    logging.info(f'Port {CONTROLLER_PORT} opened succesfully.')
    controller_found = True
except Exception as e:
    logging.warning(f'Error occurred while opening serial port.\nException: {e}')
    controller_found = False
    sys.exit( 1 )


class MountInterface():
    def __init__(self):
        self.mode = 0
        self.speed_setpoint = 0
        self.torque_setpoint = 0
        self.max_speed = 0
        self.control_word = 0

    def set_param(self, param, value):
        if(param == 'm'):
            self.mode = value
            serialCommand(0, value)
        elif(param == 's'):
            self.speed_setpoint = value
            # serialCommand(1, value)
        elif(param == 't'):
            self.torque_setpoint = value
            # serialCommand(2, value)
        elif(param == 'x'):
            self.max_speed = value
            serialCommand(3, value)
        elif(param == 'c'):
            self.control_word = value
            serialCommand(4, value)

    def update_speed_setpoint(self, direction):
        pass

    def update_target_setpoint(self, direction):
        pass


mount = MountInterface()


def modeHandler():
    if(modeSpeedButton.isChecked()):
        logging.debug('Set mode to Speed Control')
        mount.set_param('m', 0)
    elif(modeTorqueButton.isChecked()):
        logging.debug('Set mode to Torque Control')
        mount.set_param('m', 1)


def speedHandler():
    speed_value = int(setSpeedInput.text())
    logging.debug(f'Set speed setpoint to: {speed_value}')
    mount.set_param('s', speed_value)


def torqueHandler():
    torque_value = int(setTorqueInput.text())
    logging.debug(f'Set torque setpoint to: {torque_value}')
    mount.set_param('t', torque_value)


def maxSpeedHandler():
    max_speed_value = int(setMaxSpeedInput.text())
    logging.debug(f'Set Max Speed to: {max_speed_value}')
    mount.set_param('x', max_speed_value)


def upPressHandler():
    logging.debug(f'Up Button pressed')
    mount.update_speed_setpoint('u')
    mount.set_param('c', 0)


def downPressHandler():
    logging.debug(f'Down Button pressed')
    mount.update_speed_setpoint('d')
    mount.set_param('c', 0)


def upReleaseHandler():
    logging.debug(f'Up Button released')
    mount.set_param('s', 0)


def downReleaseHandler():
    logging.debug(f'Down Button released')
    mount.set_param('s', 0)


def serialCommand(param, value):
    command = f'{param} {value}\n'
    logging.debug(f'Command: {command}')
    # ser_controller.write(command.encode())


if(controller_found):
    # Set up and run the GUI
    app = QApplication([])
    mainWindow = QMainWindow()
    mainWindow.setWindowTitle( f'Mount Elevation GUI v{APP_VERSION}' )
    #mainWindow.resize(800,600)

    window = QWidget()
    vBoxLayout = QVBoxLayout()
    window.setLayout(vBoxLayout)

    mainWindow.setCentralWidget(window)

    # The Test Bench controls
    configLabel = QLabel("Options and configuration")
    configLabel.setStyleSheet("font-weight: bold; text-decoration: underline; font-size: 20;")

    # Controls to select the mode
    setModeLabel = QLabel(f"Servo Drive Mode:")
    modeRadio = QWidget()
    modeRadioLayout = QGridLayout()
    modeRadio.setLayout(modeRadioLayout)
    modeSpeedButton = QRadioButton("Speed Control")
    modeTorqueButton = QRadioButton("Torque Control")

    modeSpeedButton.toggled.connect(modeHandler)
    modeTorqueButton.toggled.connect(modeHandler)


    modeRadioLayout.addWidget(modeSpeedButton,  0, 0)
    modeRadioLayout.addWidget(modeTorqueButton,  0, 1)
    modeSpeedButton.setChecked(True) #default


    # Label
    speedLabel = QLabel("For use in speed control mode:")
    speedLabel.setStyleSheet("font-weight: bold; text-decoration: underline; font-size: 20;")

    setSpeedLabel = QLabel(f"Motor RPM")
    setSpeedControls = QWidget()
    hBoxLayout = QHBoxLayout()
    setSpeedControls.setLayout(hBoxLayout)
    setSpeedInput = QLineEdit("10")
    onlyInt = QIntValidator()
    setSpeedInput.setValidator(onlyInt)
    setSpeedButton = QPushButton("Set Speed")
    setSpeedButton.clicked.connect(speedHandler)
    hBoxLayout.addWidget(setSpeedLabel)
    hBoxLayout.addWidget(setSpeedInput)
    hBoxLayout.addWidget(setSpeedButton)


    # Label
    stepsLabel = QLabel("For use in the torque control mode:")
    stepsLabel.setStyleSheet("font-weight: bold; text-decoration: underline; font-size: 20;")

    setTorqueLabel = QLabel(f"Torque (%)")
    setTorqueControls = QWidget()
    hBoxLayout = QHBoxLayout()
    setTorqueControls.setLayout(hBoxLayout)
    setTorqueInput = QLineEdit("50")
    onlyInt = QIntValidator()
    setTorqueInput.setValidator(onlyInt)
    setTorqueButton = QPushButton("Set torque")
    setTorqueButton.clicked.connect(torqueHandler)
    hBoxLayout.addWidget(setTorqueLabel)
    hBoxLayout.addWidget(setTorqueInput)
    hBoxLayout.addWidget(setTorqueButton)


    setMaxSpeedLabel = QLabel(f"Max Speed")
    setMaxSpeedControls = QWidget()
    hBoxLayout = QHBoxLayout()
    setMaxSpeedControls.setLayout(hBoxLayout)
    setMaxSpeedInput = QLineEdit("1000")
    onlyInt = QIntValidator()
    setMaxSpeedInput.setValidator(onlyInt)
    setMaxSpeedButton = QPushButton("Set Max Speed")
    setMaxSpeedButton.clicked.connect(maxSpeedHandler)
    hBoxLayout.addWidget(setMaxSpeedLabel)
    hBoxLayout.addWidget(setMaxSpeedInput)
    hBoxLayout.addWidget(setMaxSpeedButton)

    directionLabel = QLabel("Direction:")
    directionLabel.setStyleSheet("font-weight: bold; text-decoration: underline; font-size: 20;")

    dirUpButton = QPushButton("Go Up")
    dirUpButton.pressed.connect(upPressHandler)
    dirUpButton.released.connect(upReleaseHandler)
    # hBoxLayout.addWidget(dirCWButton)

    dirDownButton = QPushButton("Go Down")
    # dirDownButton.clicked.connect(speedHandler)
    dirDownButton.pressed.connect(downPressHandler)
    dirDownButton.released.connect(downReleaseHandler)
    # hBoxLayout.addWidget(dirCCWButton)


    vBoxLayout.addWidget(configLabel)
    vBoxLayout.addWidget(setModeLabel)
    vBoxLayout.addWidget(modeRadio)



    vBoxLayout.addWidget(speedLabel)
    vBoxLayout.addWidget(setSpeedControls)
    vBoxLayout.addWidget(stepsLabel)
    vBoxLayout.addWidget(setTorqueControls)

    vBoxLayout.addWidget(setMaxSpeedControls)

    vBoxLayout.addWidget(directionLabel)
    vBoxLayout.addWidget(dirUpButton)
    vBoxLayout.addWidget(dirDownButton)


    # Run the GUI
    mainWindow.show()
    exitCode = app.exec()
    closeThread = True
    sys.exit( exitCode )