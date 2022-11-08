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

DRIVER_PORT = 'COM4'
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

# REG_CONTROLWORD = [ 0x3100, 1 ]
# REG_OP_MOED = [ 0x3500, 1 ]
# REG_INVERT_DIR = [ 0x4700, 1 ]
# REG_TARGET_POS = [ 0x4000, 2 ]
# REG_TARGET_SPEED = [ 0x6F00, 2 ]
# REG_MAX_SPEED = [ 0x4900, 1 ]
# REG_TARGET_TORQUE = [ 0x3C00, 1 ]

POLL_COUNT = 50
POLL_INTERVAL = 0.005

# from pymodbus.client import AsyncModbusSerialClient


def get_velocity(client):
    result_code = 0
    result = client.read_holding_registers(address=REG_REAL_SPEED[0],count=REG_REAL_SPEED[1], unit=DRIVER_NODEID)
    if not result.isError():
        raw_units = result.registers[0] | result.registers[1] << 16
        velocity_iu = raw_units
        bits = 32
        if (velocity_iu & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            velocity_iu = velocity_iu - (1 << bits)        # compute negative value
        velocity_rpm = ( ( velocity_iu * 1875 ) / 10000 ) / 512
        print(f"  Velocity (RPM): {velocity_rpm}")
    else:
        print("error: {}".format(result))
        result_code = 1
    return result_code


def get_current(client):
    result_code = 0
    result = client.read_holding_registers(address=REG_REAL_CURR[0],count=REG_REAL_CURR[1], unit=DRIVER_NODEID)
    if not result.isError():
        raw_units = result.registers[0]
        current_iu = raw_units
        bits = 16
        if (current_iu & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            current_iu = current_iu - (1 << bits)        # compute negative value
        drive_i_peak = 36;
        current_conversion_factor = (2048/drive_i_peak)/1.414;
        current_amp =  current_iu  / current_conversion_factor
        print(f"  Current (A): {current_amp}")
    else:
        print("error: {}".format(result))
        result_code = 1
    return result_code


def get_position(client):
    result_code = 0
    result = client.read_holding_registers(address=REG_POS_ACTUAL[0],count=REG_POS_ACTUAL[1], unit=DRIVER_NODEID)
    if not result.isError():
        raw_counts = result.registers[0] | result.registers[1] << 16
        bits = 32
        if (raw_counts & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            raw_counts = raw_counts - (1 << bits)        # compute negative value
        print(f"  Pos Actual (Counts): {raw_counts}")
    else:
        print("error: {}".format(result))
        result_code = 1
    return result_code


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


def run(client):
    result_code = 0
    result_code += get_velocity(client)
    result_code += get_current(client)
    result_code += get_position(client)
    return result_code


def main():
    count_total = 0
    count_error = 0
    print('Test')
    modbus_client = start_client()
    t_start = time.time()
    t_last_poll = 0
    t_now = 0
    # for i in range(POLL_COUNT):
    while count_total < POLL_COUNT:
        t_now = time.time()
        if t_now > t_last_poll + POLL_INTERVAL:
            print(f"Poll #{count_total}")
            count_total += 1
            count_error += run( modbus_client )
            t_last_poll = t_now
        else:
            time.sleep(0.001)
    t_end = time.time()
    t_total = t_end - t_start
    stop_client( modbus_client )
    print(f"Count total: {count_total}")
    print(f"Count error: {count_error}")
    print(f"Total time: {t_total}")
    print(f"Polling interval set to: {POLL_INTERVAL}")
    interval = t_total / count_total
    print(f"1 poll every {interval} seconds")
    print('Done')


if __name__ == '__main__':
    main()
