import time
import lfast_drive_interface


POLL_COUNT = 10
POLL_INTERVAL = 0.100


def main():
    global velocity_add
    count_total = 0
    count_error = 0
    print('Test')
    modbus_client = lfast_drive_interface.start_client()
    t_start = time.time()
    t_last_poll = 0
    t_now = 0
    # for i in range(POLL_COUNT):
    while count_total < POLL_COUNT:
        velocity_add = ( count_total // 20 )
        t_now = time.time()
        if t_now > t_last_poll + POLL_INTERVAL:
            # print(f"Poll #{count_total}")
            count_total += 1
            count_error += lfast_drive_interface.run( modbus_client )
            t_last_poll = t_now
        else:
            time.sleep(0.001)
    t_end = time.time()
    t_total = t_end - t_start
    lfast_drive_interface.stop_client( modbus_client )
    print(f"Count total: {count_total}")
    print(f"Count error: {count_error}")
    print(f"Total time: {t_total}")
    print(f"Polling interval set to: {POLL_INTERVAL}")
    interval = t_total / count_total
    print(f"1 poll every {interval} seconds")
    print('Done')

if __name__ == '__main__':
    main()
