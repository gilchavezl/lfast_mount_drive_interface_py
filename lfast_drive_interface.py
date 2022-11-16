import serial
# import pymodbus
# from pymodbus import client as mbc

import time

from pymodbus.client.sync import ModbusSerialClient

from pymodbus.transaction import (
    ModbusAsciiFramer,
    ModbusBinaryFramer,
    ModbusRtuFramer,
    ModbusSocketFramer,
    ModbusTlsFramer,
)

# DRIVER_PORT = 'COM4'
DRIVER_PORT = 'COM9'
# DRIVER_BAUDRATE = 19200
# DRIVER_BAUDRATE = 38400
DRIVER_BAUDRATE = 115200
DRIVER_BYTESIZE = 8
DRIVER_PARITY = 'N'
DRIVER_STOPBITS = 1

DRIVER_NODEID = 1

# Registers
# ADDR_REG = [STARTING_ADDR_HEX, LENGTH_INT]
REG_STATUSWORD = [ 0x3200, 1 ]
REG_POS_ACTUAL = [ 0x3700, 2 ]
REG_REAL_SPEED = [ 0x3B00, 2 ]
REG_REAL_CURR = [ 0x3E00, 1 ]

REG_CONTROLWORD = [ 0x3100, 1 ]
REG_OP_MODE = [ 0x3500, 1 ]
# REG_INVERT_DIR = [ 0x4700, 1 ]
# REG_TARGET_POS = [ 0x4000, 2 ]
REG_TARGET_SPEED = [ 0x6F00, 2 ]
# REG_MAX_SPEED = [ 0x4900, 1 ]
REG_TARGET_TORQUE = [ 0x3C00, 1 ]

POLL_COUNT = 100
POLL_INTERVAL = 0.025

# from pymodbus.client import AsyncModbusSerialClient


def get_twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val


def get_velocity_feedback(client, drive_id):
    result_code = 0
    result = client.read_holding_registers(address=REG_REAL_SPEED[0],count=REG_REAL_SPEED[1], unit=drive_id)
    if not result.isError():
        raw_units = result.registers[0] | result.registers[1] << 16
        velocity_iu = get_twos_comp(val=raw_units, bits=32)
        velocity_rpm = ( ( velocity_iu * 1875 ) / 10000 ) / 512
        print(f"  Velocity (RPM): {velocity_rpm}")
    else:
        print("error: {}".format(result))
        result_code = 1
    return result_code


def get_current_feedback(client, drive_id):
    result_code = 0
    result = client.read_holding_registers(address=REG_REAL_CURR[0],count=REG_REAL_CURR[1], unit=drive_id)
    if not result.isError():
        raw_units = result.registers[0]
        current_iu = raw_units
        current_iu = get_twos_comp(val=raw_units, bits=16)
        drive_i_peak = 36;
        current_conversion_factor = (2048/drive_i_peak)/1.414;
        current_amp =  current_iu  / current_conversion_factor
        print(f"  Current (A): {current_amp}")
    else:
        print("error: {}".format(result))
        result_code = 1
    return result_code


def get_position_feedback(client, drive_id):
    result_code = 0
    result = client.read_holding_registers(address=REG_POS_ACTUAL[0],count=REG_POS_ACTUAL[1], unit=drive_id)
    if not result.isError():
        raw_counts = result.registers[0] | result.registers[1] << 16
        encoder_counts = get_twos_comp(val=raw_counts, bits=32)
        print(f"  Pos Actual (Counts): {encoder_counts}")
    else:
        print("error: {}".format(result))
        result_code = 1
    return result_code


def set_velocity_setpoint(client, drive_id, setpoint_rpm):
    setpoint_units =  int( ( ( setpoint_rpm * 512 ) * 10000 ) / 1875 )
    register_high_word = setpoint_units & 0xFFFF
    register_low_word = ( setpoint_units & 0xFFFF0000 ) >> 16
    register_values = [register_high_word, register_low_word]
    client.write_registers(address=REG_TARGET_SPEED[0], values=register_values, unit=drive_id)


def set_torque_setpoint(client, drive_id, setpoint_torque):
    torque_value = int( setpoint_torque * 10 )
    client.write_registers(address=REG_TARGET_TORQUE[0], values=torque_value, unit=drive_id)


def set_motor_mode(client, drive_id, set_mode):
    client.write_registers(address=REG_OP_MODE[0], values=set_mode, unit=drive_id)


def set_motor_state(client, drive_id, set_state):
    client.write_registers(address=REG_CONTROLWORD[0], values=set_state, unit=drive_id)


def start_client():
    # client = pymodbus.client.ModbusSerialClient(
    client = ModbusSerialClient(
        method='rtu',
    # client = AsyncModbusSerialClient(
        port=DRIVER_PORT,  # serial port
        # Common optional paramers:
        #    modbus_decoder=ClientDecoder,
        # framer=ModbusRtuFramer,
        #    timeout=10,
        #    retries=3,
        #    retry_on_empty=False,
        #    close_comm_on_error=False,
        #    strict=True,
        # Serial setup parameters
        baudrate=DRIVER_BAUDRATE,
        bytesize=DRIVER_BYTESIZE,
        parity=DRIVER_PARITY,
        stopbits=DRIVER_STOPBITS,
        #    handle_local_echo=False,
    )
    client.connect()
    return client


def stop_client(client):
    client.close()


def main():
    print(f"main() call, should not happen when using as import")


if __name__ == '__main__':
    main()
