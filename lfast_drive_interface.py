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
DRIVER_BAUDRATE = 19200
DRIVER_BYTESIZE = 8
DRIVER_PARITY = 'N'
DRIVER_STOPBITS = 1

DRIVER_NODEID = 1

# Registers
# ADDR_REG = [STARTING_ADDR_HEX, LENGTH_INT]
REG_STATUSWORD = [ 0x3200, 1 ]
REG_POS_ACTUAL = [ 0x3700, 2 ]
REG_REAL_SPEED = [ 0x3B00, 2 ]

POLL_COUNT = 100
POLL_INTERVAL = 0.050

# from pymodbus.client import AsyncModbusSerialClient

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
    result = client.read_holding_registers(address=REG_POS_ACTUAL[0],count=REG_POS_ACTUAL[1], unit=DRIVER_NODEID)
    if not result.isError():
        print(result.registers)
    else:
        print("error: {}".format(result))
        result_code = 1
    return result_code


def main():
    count_total = 0
    count_error = 0
    print('Test')
    modbus_client = start_client()
    t_start = time.time()
    for i in range(POLL_COUNT):
        count_total += 1
        count_error += run( modbus_client )
        time.sleep(POLL_INTERVAL)
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
