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
MIN_DAC_VOLTAGE = 0
MAX_DAC_VOLTAGE = 5

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


class StepperController():
    def __init__(self):
        self.mode = 0
        self.step_angle = 0
        self.step_direction = 0
        self.step_speed = 0
        self.stop_mode = 0

    def set_param(self, param, value):
        if(param == 'm'):
            self.mode = value
            serialCommand(0, value)
        elif(param == 'a'):
            self.step_angle = value
            serialCommand(1, value)
        elif(param == 'd'):
            self.step_direction = value
            serialCommand(2, value)
        elif(param == 's'):
            self.step_speed = value
            serialCommand(3, value)
        elif(param == 'p'):
            self.stop_mode = value
            serialCommand(4, value)


stepper = StepperController()

def directionHandler():
    if(dirCWButton.isChecked()):
        logging.debug('CW')
        stepper.set_param('d', 0)
    elif(dirCCWButton.isChecked()):
        logging.debug('CCW')
        stepper.set_param('d', 1)


def stepHandler():
    if(stepFullButton.isChecked()):
        logging.debug('Full step')
        stepper.set_param('a', 0)
    elif(stepHalfButton.isChecked()):
        logging.debug('Half step')
        stepper.set_param('a', 1)


def modeHandler():
    if(modeIdleButton.isChecked()):
        logging.debug('Idle')
        stepper.set_param('m', 0)
    elif(modeStepButton.isChecked()):
        logging.debug('Step')
        stepper.set_param('m', 1)
    elif(modeSlewButton.isChecked()):
        logging.debug('Slew')
        stepper.set_param('m', 2)


def speedHandler():
    speed_value = int(setSpeedInput.text())
    logging.debug(f'Speed button press: {speed_value}')
    stepper.set_param('s', speed_value)


def stepsHandler():
    steps_value = int(setStepsInput.text())
    logging.debug(f'Steps button press: {steps_value}')
    serialCommand(5, steps_value)


def stopHandler():
    if(stopSoftButton.isChecked()):
        logging.debug('Soft stop')
        stepper.set_param('p', 0)
    elif(stopHardButton.isChecked()):
        logging.debug('Hard stop')
        stepper.set_param('p', 1)


def serialCommand(param, value):
    command = f'{param} {value}\n'
    logging.debug(f'Command: {command}')
    # ser_controller.write(command.encode())



if(controller_found):
    # Set up and run the GUI
    app = QApplication([])
    mainWindow = QMainWindow()
    mainWindow.setWindowTitle( f'Stepper controller GUI v{APP_VERSION}' )
    #mainWindow.resize(800,600)

    window = QWidget()
    vBoxLayout = QVBoxLayout()
    window.setLayout(vBoxLayout)

    mainWindow.setCentralWidget(window)

    # The Test Bench controls
    configLabel = QLabel("Options and configuration")
    configLabel.setStyleSheet("font-weight: bold; text-decoration: underline; font-size: 20;")

    # Controls to select the mode
    setModeLabel = QLabel(f"Select mode to use")
    modeRadio = QWidget()
    modeRadioLayout = QGridLayout()
    modeRadio.setLayout(modeRadioLayout)
    modeIdleButton = QRadioButton("Idle")
    modeStepButton = QRadioButton("Step")
    modeSlewButton = QRadioButton("Slew")

    modeIdleButton.toggled.connect(modeHandler)
    modeStepButton.toggled.connect(modeHandler)
    modeSlewButton.toggled.connect(modeHandler)


    modeRadioLayout.addWidget(modeIdleButton,  0, 0)
    modeRadioLayout.addWidget(modeStepButton,  0, 1)
    modeRadioLayout.addWidget(modeSlewButton,  0, 2)
    modeIdleButton.setChecked(True) #default


    # Controls to select the step size
    setStepLabel = QLabel(f"Select step size to use")
    stepRadio = QWidget()
    stepRadioLayout = QGridLayout()
    stepRadio.setLayout(stepRadioLayout)
    stepFullButton = QRadioButton("Full step")
    stepHalfButton = QRadioButton("Half step")

    stepFullButton.toggled.connect(stepHandler)
    stepHalfButton.toggled.connect(stepHandler)

    stepRadioLayout.addWidget(stepFullButton,  0, 0)
    stepRadioLayout.addWidget(stepHalfButton,  0, 1)
    stepFullButton.setChecked(True) #default


    # Controls to select the direction
    setDirLabel = QLabel(f"Select motion direction")
    dirRadio = QWidget()
    dirRadioLayout = QGridLayout()
    dirRadio.setLayout(dirRadioLayout)
    dirCWButton = QRadioButton("CW")
    dirCCWButton = QRadioButton("CCW")

    dirCWButton.toggled.connect(directionHandler)
    dirCCWButton.toggled.connect(directionHandler)

    dirRadioLayout.addWidget(dirCWButton,  0, 0)
    dirRadioLayout.addWidget(dirCCWButton,  0, 1)
    dirCWButton.setChecked(True) #default


    # Controls to select the stop mode
    setStopLabel = QLabel(f"Select stopping mode")
    stopRadio = QWidget()
    stopRadioLayout = QGridLayout()
    stopRadio.setLayout(stopRadioLayout)
    stopSoftButton = QRadioButton("Soft stop")
    stopHardButton = QRadioButton("Hard stop")

    stopSoftButton.toggled.connect(stopHandler)
    stopHardButton.toggled.connect(stopHandler)

    stopRadioLayout.addWidget(stopSoftButton,  0, 0)
    stopRadioLayout.addWidget(stopHardButton,  0, 1)
    stopSoftButton.setChecked(True) #default


    # Label
    speedLabel = QLabel("For use in all modes:")
    speedLabel.setStyleSheet("font-weight: bold; text-decoration: underline; font-size: 20;")

    setSpeedLabel = QLabel(f"Motor speed in steps/sec")
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
    stepsLabel = QLabel("For use in the Step mode:")
    stepsLabel.setStyleSheet("font-weight: bold; text-decoration: underline; font-size: 20;")

    setStepsLabel = QLabel(f"Number of steps")
    setStepsControls = QWidget()
    hBoxLayout = QHBoxLayout()
    setStepsControls.setLayout(hBoxLayout)
    setStepsInput = QLineEdit("1")
    onlyInt = QIntValidator()
    setStepsInput.setValidator(onlyInt)
    setStepsButton = QPushButton("Set Steps")
    setStepsButton.clicked.connect(stepsHandler)
    hBoxLayout.addWidget(setStepsLabel)
    hBoxLayout.addWidget(setStepsInput)
    hBoxLayout.addWidget(setStepsButton)


    vBoxLayout.addWidget(configLabel)
    vBoxLayout.addWidget(setModeLabel)
    vBoxLayout.addWidget(modeRadio)
    vBoxLayout.addWidget(setStepLabel)
    vBoxLayout.addWidget(stepRadio)
    vBoxLayout.addWidget(setDirLabel)
    vBoxLayout.addWidget(dirRadio)
    vBoxLayout.addWidget(setStopLabel)
    vBoxLayout.addWidget(stopRadio)


    vBoxLayout.addWidget(speedLabel)
    vBoxLayout.addWidget(setSpeedControls)
    vBoxLayout.addWidget(stepsLabel)
    vBoxLayout.addWidget(setStepsControls)


    # Run the GUI
    mainWindow.show()
    exitCode = app.exec()
    closeThread = True
    sys.exit( exitCode )