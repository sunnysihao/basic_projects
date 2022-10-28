# _*_ coding=: utf-8 _*_
#coding:utf-8

import roslib
import rosbag
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from cv_bridge import CvBridgeError

path = '/tmp/root//model_saas_data/uploadfile/zhangsihao (admin)/image_rect_color/' #存放图片的位置
class ImageCreator():


    def __init__(self):
        self.bridge = CvBridge()
        with rosbag.Bag('/tmp/root//model_saas_data/uploadfile/zhangsihao (admin)/data2.bag', 'r') as bag:   #要读取的bag文件；
            for topic, msg, t in bag.read_messages():
                if topic == "/usb_cam/image_rect_color":  #图像的topic；
                        try:
                            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
                        except CvBridgeError as e:
                            print(e)
                        timestr = "%.6f" % msg.header.stamp.to_sec()
                        #%.6f表示小数点后带有6位，可根据精确度需要修改；
                        image_name = timestr + ".jpg" #图像命名：时间戳.jpg
                        cv2.imwrite(path+image_name, cv_image)  #保存；


if __name__ == '__main__':

    #rospy.init_node(PKG)

    try:
        image_creator = ImageCreator()
    except rospy.ROSInterruptException:
        pass
