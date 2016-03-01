#!/usr/bin/env python

import yaml
import rospy
import sys

from gummi_interface.antagonist import Antagonist
from gummi_interface.gummi import Gummi

def main(args):

    pi = 3.1416
    print("Please enter path to folder where you want calibration file saved:")
    path =  raw_input()

    rospy.init_node('gummiCalibrate', anonymous=True)
    r = rospy.Rate(60)  
    
    gummi = Gummi()

    anglesToTry = [x / 100.0 for x in range(-48, 49, 12)]
    cocontractionsToTry = [x / 100.0 for x in range(80, -1, -10)] 

    gummi.setCocontraction(0.6, 0.6, 0.6, 0.6, 0.6)

    print('WARNING: Moving joints sequentially to equilibrium positions.')
    gummi.doGradualStartup()
    
    print('WARNING: Moving to resting pose, hold arm!')
    rospy.sleep(3)

    for i in range(0, 400):
        gummi.goRestingPose()
        r.sleep()

    print("GummiArm is live!")

    for i in range (0,300):
        gummi.elbow.servoTo(0, 0.5)
        r.sleep()
    
    thetas = list()
    ccs = list()
    equilibriums = list()
    for cocont in cocontractionsToTry: 

        for i in range (0,300):
            gummi.elbow.servoTo(0, cocont)
            r.sleep()

        for angle in anglesToTry:
            print("Moving arm to angle: " + str(angle) + " and cocontraction: " + str(cocont) + ".")
            for i in range (0,300):
                gummi.elbow.servoTo(angle, cocont)
                r.sleep()

            joint = gummi.elbow
            thetas.append(round(joint.angle.getEncoder(), 3))
            ccs.append(round(cocont, 3))
            equilibriums.append(round(joint.getDesiredEquilibrium(), 3))

        for i in range (0,300):
            gummi.elbow.servoTo(0, cocont)
            r.sleep()

    data = {'thetas': thetas, 'ccs': ccs, 'equilibriums': equilibriums}
    text = yaml.dump(data,
                     default_flow_style = False,
                     explicit_start = True)
    print text

    fileName = path + "/calibration_" + joint.getName() + ".yaml"
    with open(fileName, 'w') as outfile:
        outfile.write(text)
        print("Calibration data written to: " + fileName)

if __name__ == '__main__':
    main(sys.argv)