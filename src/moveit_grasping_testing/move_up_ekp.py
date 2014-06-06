#!/usr/bin/env python

# Software License Agreement (BSD License)
#
# Copyright (c) 2013, SRI International
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of SRI International nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Author: Acorn Pooley

## BEGIN_SUB_TUTORIAL imports
##
## To use the python interface to move_group, import the moveit_commander
## module.  We also import rospy and some messages that we will use.
import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
from moveit_msgs.srv import ExecuteKnownTrajectory, ExecuteKnownTrajectoryRequest, ExecuteKnownTrajectoryResponse
import geometry_msgs.msg
## END_SUB_TUTORIAL

from std_msgs.msg import String

def move_group_python_interface_tutorial():
    ## BEGIN_TUTORIAL
    ##
    ## Setup
    ## ^^^^^
    ## CALL_SUB_TUTORIAL imports
    ##
    ## First initialize moveit_commander and rospy.
    print "============ Starting tutorial setup"
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('move_group_python_interface_tutorial',
                    anonymous=True)
    
    ## Instantiate a RobotCommander object.  This object is an interface to
    ## the robot as a whole.
    robot = moveit_commander.RobotCommander()
    
    ## Instantiate a PlanningSceneInterface object.  This object is an interface
    ## to the world surrounding the robot.
    scene = moveit_commander.PlanningSceneInterface()
    
    ## Instantiate a MoveGroupCommander object.  This object is an interface
    ## to one group of joints.  In this case the group is the joints in the left
    ## arm.  This interface can be used to plan and execute motions on the left
    ## arm.
    group = moveit_commander.MoveGroupCommander("right_arm")
    #group.set_planner_id("PRMkConfigDefault")
    
    
    ## We create this DisplayTrajectory publisher which is used below to publish
    ## trajectories for RVIZ to visualize.
    display_trajectory_publisher = rospy.Publisher(
                                        '/move_group/display_planned_path',
                                        moveit_msgs.msg.DisplayTrajectory)
    
    
    ## Getting Basic Information
    ## ^^^^^^^^^^^^^^^^^^^^^^^^^
    ##
    ## We can get the name of the reference frame for this robot
    print "============ Reference frame: %s" % group.get_planning_frame()
    
    ## We can also print the name of the end-effector link for this group
    print "============ Reference frame: %s" % group.get_end_effector_link()
    
    ## We can get a list of all the groups in the robot
    print "============ Robot Groups:"
    print robot.get_group_names()
    
    ## Sometimes for debugging it is useful to print the entire state of the
    ## robot.
    print "============ Printing robot state"
    print robot.get_current_state()
    print "============"
    
    rospy.sleep(5)
    print "Going to compute a cartesian path from where we are to z + 0.3"
    
    ## Cartesian Paths
    ## ^^^^^^^^^^^^^^^
    ## You can plan a cartesian path directly by specifying a list of waypoints 
    ## for the end-effector to go through.
    waypoints = []
    
    # start with the current pose
    rospy.sleep(1)
    waypoints.append(group.get_current_pose().pose)
    
    # first orient gripper and move forward (+x)
    wpose = geometry_msgs.msg.Pose()
    wpose.orientation.w = 1.0
    wpose.position.x = waypoints[0].position.x
    wpose.position.y = waypoints[0].position.y
    wpose.position.z = waypoints[0].position.z + 0.15
    waypoints.append(copy.deepcopy(wpose))
    
    
    # fourth move to the side a lot
    wpose.position.z += 0.15
    waypoints.append(copy.deepcopy(wpose))
    
    ## We want the cartesian path to be interpolated at a resolution of 1 cm
    ## which is why we will specify 0.01 as the eef_step in cartesian
    ## translation.  We will specify the jump threshold as 0.0, effectively
    ## disabling it.
    fraction = 0.0
    jump_threshold = 0
    eef_step = 0.01
    while fraction < 0.9:
        (plan3, fraction) = group.compute_cartesian_path(
                                     waypoints,   # waypoints to follow
                                     eef_step,        # eef_step
                                     jump_threshold)         # jump_threshold
        print "Fraction is: " + str(fraction) + " if it's less than 0.9 we will continue calculating"
        print "changing jump_threshold + 10 it was: " + str(jump_threshold)
        print "(Seems to make no difference)"
        jump_threshold += 10
        print "eef-step is: " + str(eef_step) + " adding 1cm"
        eef_step += 0.01
    
                                 
    
    print "plan looks like: " + str(plan3)
    print "with fraction being: " + str(fraction)
    print "Fraction should be 1, less than that, is that we went out of the straight line, i think"
    
    print "Moving arm to cartesian path thing"
    #group.go(wait=True)
    
    rospy.sleep(1)
    
    print "this did for sure not work, so lets try with executeknowntrajectory thing"
    ekp = rospy.ServiceProxy('/execute_kinematic_path', ExecuteKnownTrajectory)
    ekp.wait_for_service()
    
    print "!!!! Gonna send goal to execute_kinematic_path (waiting 3s)"
    rospy.sleep(3)
    ektr = ExecuteKnownTrajectoryRequest()
    ektr.trajectory = plan3
    ektr.wait_for_execution = True
    print "Sending call"
    ekp.call(ektr)
    print "!!!! Call done"
    
    
    ## Adding/Removing Objects and Attaching/Detaching Objects
    ## ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ## First, we will define the collision object message
    collision_object = moveit_msgs.msg.CollisionObject()
    
    
    
    ## When finished shut down moveit_commander.
    moveit_commander.roscpp_shutdown()
    
    ## END_TUTORIAL
    
    print "============ STOPPING"


if __name__=='__main__':
    try:
        move_group_python_interface_tutorial()
    except rospy.ROSInterruptException:
        pass
