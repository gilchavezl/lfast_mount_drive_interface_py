import sys, time, logging
import enum
import serial
import lfast_drive_interface

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

SERIAL_ADAPTER_PORT = 'COM5'

controller_found = True
try:
    # ser_controller = serial.Serial(CONTROLLER_PORT, 57600, timeout=0)
    modbus_client = lfast_drive_interface.start_client()
    time.sleep(2)
    controller_found = True
    controller_found = modbus_client.is_socket_open()
    assert(controller_found)
    # if not controller_found:
    #     raise ValueError('Could not initialize Modbus client')
    logging.info(f'Port {SERIAL_ADAPTER_PORT} opened succesfully.')
except Exception as e:
    logging.warning(f'Error occurred while opening serial port.\nException: {e}')
    controller_found = False
    sys.exit( 1 )


class Motor_State(enum.Enum):
    DISABLED = 0x02
    ENABLED = 0x06
    E_STOP = 0x0B
    POWER_ON = 0x0F


class Motor_Mode(enum.Enum):
    POSITION_MODE = 1
    SPEED_MODE = 3
    TORQUE_MODE = 4
    HOME_MODE = 6


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
            driveCommand(1, value)
        elif(param == 's'):
            self.speed_setpoint = value
        elif(param == 't'):
            self.torque_setpoint = value
        elif(param == 'x'):
            self.max_speed = value
            driveCommand(6, value)
        elif(param == 'c'):
            self.control_word = value
            driveCommand(2, value)

    def update_speed_setpoint(self, direction):
        if(direction == 'u'):
            speed = self.speed_setpoint
            driveCommand(3, speed)
        elif(direction == 'd'):
            speed = self.speed_setpoint * -1
            driveCommand(3, speed)
        elif(direction == 'i'):
            pass

    def update_torque_setpoint(self, direction):
        if(direction == 'u'):
            torque = self.torque_setpoint
            driveCommand(4, torque)
        elif(direction == 'd'):
            torque = self.torque_setpoint * -1
            driveCommand(4, torque)
        elif(direction == 'i'):
            pass


mount = MountInterface()


def modeHandler():
    if(modeSpeedButton.isChecked()):
        logging.debug('Set mode to Speed Control')
        mount.set_param('m', 1)
    elif(modeTorqueButton.isChecked()):
        logging.debug('Set mode to Torque Control')
        mount.set_param('m', 2)


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
    logging.debug(f'\nUP BUTTON PRESSED\n')
    mount.update_speed_setpoint('u')
    mount.update_torque_setpoint('u')
    mount.set_param('c', 2)


def downPressHandler():
    logging.debug(f'Down Button pressed')
    mount.update_speed_setpoint('d')
    mount.update_torque_setpoint('d')
    mount.set_param('c', 2)


def upReleaseHandler():
    logging.debug(f'\nUP BUTTON RELEASED\n')
    mount.set_param('c', 1)


def downReleaseHandler():
    logging.debug(f'Down Button released')
    mount.set_param('c', 1)


def driveCommand(param, value):
    client = modbus_client
    command = f'{param} {value}\n'
    logging.debug(f'Command: {command}')
    # ser_controller.write(command.encode())
    d1 = 3
    d2 = 4
    if param == 1:
        # set motor mode (position, speed, torque control)
        mode_input = int(value)
        if mode_input == 0:
            motor_set_mode = Motor_Mode.POSITION_MODE.value
        elif mode_input == 1:
            motor_set_mode = Motor_Mode.SPEED_MODE.value
        elif mode_input == 2:
            motor_set_mode = Motor_Mode.TORQUE_MODE.value
        elif mode_input == 3:
            motor_set_mode = Motor_Mode.HOME_MODE.value
        else:
            motor_set_mode = Motor_Mode.POSITION_MODE.value
        print(f'Motor Mode input: {motor_set_mode}')
        lfast_drive_interface.set_motor_mode(client, d1, motor_set_mode)
        lfast_drive_interface.set_motor_mode(client, d2, motor_set_mode)
    elif param == 2:
        # set motor state (disable, enable, e-stop, power on)
        state_input = int(value)
        if state_input == 0:
            motor_set_state = Motor_State.DISABLED.value
        elif state_input == 1:
            motor_set_state = Motor_State.ENABLED.value
        elif state_input == 2:
            motor_set_state = Motor_State.POWER_ON.value
        elif state_input == 3:
            motor_set_state = Motor_State.E_STOP.value
        else:
            motor_set_state = Motor_State.DISABLED.value
        print(f'Motor State input: {motor_set_state}')
        lfast_drive_interface.set_motor_state(client, d1, motor_set_state)
        lfast_drive_interface.set_motor_state(client, d2, motor_set_state)
    elif param == 3:
        # set target speed
        motor_target_speed = value
        lfast_drive_interface.set_velocity_setpoint(client, d1, motor_target_speed)
        lfast_drive_interface.set_velocity_setpoint(client, d2, (motor_target_speed * -1 ))
        print(f'Target speed: {motor_target_speed}')
    elif param == 4:
        # set target torque
        motor_target_torque = value
        print(f'Target torque: {motor_target_torque}')
        lfast_drive_interface.set_torque_setpoint(client, d1, motor_target_torque)
        lfast_drive_interface.set_torque_setpoint(client, d2, (motor_target_torque * -1))
    elif param == 6:
        # set max speed
        pass


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
    # hBoxLayout.addWidget(setMaxSpeedLabel)
    # hBoxLayout.addWidget(setMaxSpeedInput)
    # hBoxLayout.addWidget(setMaxSpeedButton)

    directionLabel = QLabel("Direction:")
    directionLabel.setStyleSheet("font-weight: bold; text-decoration: underline; font-size: 20;")

    dirUpButton = QPushButton("UP")
    dirUpButton.setMinimumHeight(80)
    dirUpButton.pressed.connect(upPressHandler)
    dirUpButton.released.connect(upReleaseHandler)
    # hBoxLayout.addWidget(dirCWButton)

    dirDownButton = QPushButton("DOWN")
    dirDownButton.setMinimumHeight(80)
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
    lfast_drive_interface.stop_client( modbus_client )
    sys.exit( exitCode )