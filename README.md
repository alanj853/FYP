# FYP
All of the Code For My Final Year Project.

This repo contains the 3 applications use for my FYP
  1. Crazyflie flight Controller - Used to fly the Crazyflie
  2. Image Processing Program - Used to detect and track object, and to free space in an area
  3. UDP Server - Used for communicating Data between Crazyflie and Image Processing Program
  
Applications 2 & 3 are eclipse projects so they can be downloaded and run directly in eclipse
  Note: for Image Processing Program, the user will have to install and build OpenCV
  and then add the libraries and include directories to the programs path. Also, this 
  application runs a UDP client for sending data to the UDP server. However, this client
  uses include header files that are only available on windows machines.

The UDP server can be run by simply double-clicking the jar file.

To run the Crazyflie Flight Controller, the user must first 
  1. install crazyflie python client requirements found at       https://github.com/bitcraze/crazyflie-clients-python
  2. Then the user must navigate to the 'programs' directory through a command line
  3. open up the main.py file and fix system.append() parts, as per comments in code
  4. Go back to command line, and type 'python main.py <arg1> <arg2>'
    4.1 arg1 is either 'linux or 'windows' depeding on your OS. Linux is default
    4.2 arg2 is either 'off' or 'on', to start motors on start up. On is default



