#!/usr/bin/env python

import roslib; roslib.load_manifest('aries')
import rospy
from  lib_robotis import USB2Dynamixel_Device, Robotis_Servo
from math import *
from std_msgs.msg import Float32, String
from aries.srv import LidarPivotAngle, LidarPivotAngleResponse, LidarPivotAngleRequest

'''
This module is responsible for interfacing with lidar pivot motor.
'''
INITIAL_ANGLE = 0   # Angle servo initializes to
DYNAMIXEL_ID = 1    # ID for dynamixel servo

class lidar_pivot_controller(object):

    def __init__(self):
        '''
        lidar pivot controller constructor
        '''
        # Creates the ROS node.
        rospy.init_node("lidar_pivot_controller")

        # Load relevant parameters from ROS parameter server
        dyn_port = rospy.get_param("ports/dynamixel", "/dev/ttyUSB1")
        dyn_baud = rospy.get_param("baudrates/dynamixel_baud", 1000000)

        self.target_angle = rospy.get_param("dynamixel_settings/laying_angle", INITIAL_ANGLE)       # Target angle in radians
        self.move_request = False
        dyn_id = rospy.get_param("dynamixel_settings/id", DYNAMIXEL_ID)
        CMDS_TOPIC = rospy.get_param("topics/lidar_pivot_cmds", "lidar_pivot_control")
        TARGET_ANGLE_TOPIC = rospy.get_param("topics/lidar_pivot_target_angles", "lidar_pivot_target_angles")
        POS_SERV = rospy.get_param("services/lidar_pivot_position", "get_lidar_pivot_position")
        # Servo Motor Setup
        self.dyn = USB2Dynamixel_Device(dev_name = dyn_port, baudrate = dyn_baud)
        self.servo = Robotis_Servo(self.dyn, dyn_id)

        # Inits the LIDAR pivot controller Subscriber
        rospy.Subscriber(TARGET_ANGLE_TOPIC, Float32, self.angle_callback)
        rospy.Subscriber(CMDS_TOPIC, String, self.cmds_callback)

        # Initialize service that gets the current angle of the lidar
        self.get_angle_service = rospy.Service(POS_SERV, LidarPivotAngle, self.handle_get_lidar_pivot_position)

        # Send servo to default position
        self.servo.move_angle(self.target_angle)
        self.current_angle = self.servo.read_angle()

    def angle_callback(self, angle):
        '''
        lidar_pivot_angle topic callback function
        '''
        self.target_angle = angle.data
        self.move_request = True

    def cmds_callback(self, data):
        '''
        '''
        pass

    def handle_get_lidar_pivot_position(self, req):
        '''
        get_lidar_pivot_position Service handler.
        '''
        response = LidarPivotAngleResponse(self.servo.read_angle())
        return response

    def run(self):
        # #Runs while shut down message is not recieved.
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():

            # Sends command to move Dynamixel to absolute position.
            if self.move_request: 
                self.move_request = False
                self.servo.move_angle(self.target_angle)
                
            rate.sleep()    # Keeps ROS from crashing

if __name__ == "__main__":
    controller = lidar_pivot_controller()
    controller.run()