import sys, time, enum


exit = False
drv = 0
cmd = 0
val = 0.0

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


def get_user_input():
    global exit
    global drv
    global cmd
    global val
    try:
        drv = int(input("DRV: "))
        cmd = int(input("CMD: "))
        val = float(input("VAL: "))
    except KeyboardInterrupt:
        print(f'Exit')
        exit = True
        return 1
    return 0


def process_input():
    if cmd == 1:
        # set motor state (disable, enable, e-stop, power on)
        state_input = int(val)
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
    elif cmd == 2:
        # set motor mode (position, speed, torque control)
        mode_input = int(val)
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
    elif cmd == 3:
        # set target speed
        motor_target_speed = val
    elif cmd == 4:
        # set target torque
        motor_target_torque = val
        pass
    elif cmd == 6:
        # set max speed
        pass
    elif cmd == 9:
        # get (position, velocity, current) feedback
        param = int(val)
        if param == 0:
            # get all
            pass
        elif param == 1:
            # get position feedback
            pass
        elif param == 2:
            # get velocity feedback
            pass
        elif param == 3:
            # get current feedback
            pass
        else:
            # 
            pass
    else:
        pass


def main():
    while not exit:
        if get_user_input() == 0:
            print(f'Drive {drv}, Command {cmd}, Value {val}')
            process_input()
            

if __name__ == '__main__':
    main()
