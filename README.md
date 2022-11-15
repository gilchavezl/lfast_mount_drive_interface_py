# LFAST - Tracking Mount Servo Motor Drive Interface Utilities
This repository contains software for testing communication with a Servo Motor Drive that controls the motors on the telescope's tracking mount.

Files:
`lfast_drive_interface.py` contains functions to read and write the Kinco Servo Drive registers related to a select set of functions.

`lfast_drive_command.py` contains code to demonstrate the use of the functions, by calling them in response to user input.

This is the list of commands:
DRV: (int)	select which drive to interface with
CMD: (int)	select which command to execute
VAL: (float)	the value that goes along with the command

DRV	CMD	FUNCTION		VALUE	RESULT			DESC
1		drive 1
2		drive 2
	
	1	set motor mode to	0	Position Mode (1)
				        	1	Speed Mode (3)
					        2	Torque Mode (4)
					        3	Home Mode (6)
	
	2	set motor state		0	Disabled (0x02)
					        1	Enabled (0x06)
				    	    2	Power on (0x0F)
			    		    3	E-Stop (0x0B)
	
	3	set target speed to	val	in RPM
	
	4	set target torque	val	in percent (-100 <= 0 <= 100)
	
	6	set max speed to	val	in RPM

	9	get feedback values	0	Get All
	    				    1	Get Position
    					    2	Get Velocity
		    			    3	Get Current
