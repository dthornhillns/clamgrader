import numpy as np
import tensorflow as tf
from tkinter import *
import cv2
import clam_grade
import argparse
import time
import acapture


parser = argparse.ArgumentParser()
parser.add_argument("-m","--model", required=True, help="Path to model")
parser.add_argument("-l","--labels", required=True, help="Path to labels")
parser.add_argument("-s","--minscore", type=float, help="Minumum score to filter", default=0.7)
parser.add_argument("-W","--width", type=float, help="Real width in cm", required=True)
parser.add_argument("-H","--height", type=float, help="Real height in cm", required=True)
parser.add_argument("-c","--camera", type=int, help="Use Camera with ID", default=0, required=False)
parser.add_argument("-v","--video", help="Use Video or JPG instead of Camera")
args=vars(parser.parse_args())
# Path to frozen detection graph. This is the actual model that is used for the object detection.
modelPath = args["model"]

# List of the strings that is used to add correct label for each box.
labelsPath = args["labels"]

# Number of classes to detect
NUM_CLASSES = 2
MIN_SCORE=args["minscore"]
real_width=args["width"]
real_height=args["height"]
videoFile=args["video"]
cameraID=args["camera"]
real_area=real_width*real_height

imgAdjust=clam_grade.ImageAdjustment()
dpsm=0

cap=None

if videoFile:
    cap = acapture.AsyncVideo(videoFile)
elif cameraID>=0:
    cap = acapture.AsyncCamera(cameraID)

stream=cap

with open(labelsPath,"r") as labelFile:
    category_index=eval(labelFile.read())

# Helper code
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

def waitForKey(stream, imgAdjust):
    waitKey=  cv2.waitKey(1) & 0xFF
    if  waitKey == ord('*'):
        stream.stop()
        cv2.destroyAllWindows()
        return False
    elif waitKey == ord('x'):
        imgAdjust.contrast+=10
    elif waitKey == ord('z'):
        imgAdjust.contrast-=10
    elif waitKey == ord('s'):
        imgAdjust.brightness += 10
    elif waitKey == ord('a'):
        imgAdjust.brightness -= 10
    elif waitKey == ord('w'):
        imgAdjust.minThreshold+=10
    elif waitKey == ord('q'):
        imgAdjust.minThreshold-=10
    elif waitKey == ord('2'):
        imgAdjust.maxThreshold+=10
    elif waitKey == ord('1'):
        imgAdjust.maxThreshold-=10
    elif waitKey == ord('f'):
        imgAdjust.hue_H+=10
    elif waitKey == ord('g'):
        imgAdjust.saturation_H+=10
    elif waitKey == ord('h'):
        imgAdjust.value_H+=10
    elif waitKey == ord('v'):
        imgAdjust.hue_H-=10
    elif waitKey == ord('b'):
        imgAdjust.saturation_H-=10
    elif waitKey == ord('n'):
        imgAdjust.value_H-=10
    elif waitKey == ord('j'):
        imgAdjust.hue_L+=10
    elif waitKey == ord('k'):
        imgAdjust.saturation_L+=10
    elif waitKey == ord('l'):
        imgAdjust.value_L+=10
    elif waitKey == ord('m'):
        imgAdjust.hue_L-=10
    elif waitKey == ord(','):
        imgAdjust.saturation_L-=10
    elif waitKey == ord('.'):
        imgAdjust.value_L-=10
    elif waitKey == ord('3'):
        imgAdjust.blur-=1
    elif waitKey == ord('4'):
        imgAdjust.blur+=1
    elif waitKey == ord('u'):
        imgAdjust.showEnhanced="hue"
    elif waitKey == ord('i'):
        imgAdjust.showEnhanced="threshold"
    elif waitKey == ord('o'):
        imgAdjust.showEnhanced="blur"
    elif waitKey == ord('p'):
        imgAdjust.showEnhanced="original"
    elif waitKey == ord('7'):
        imgAdjust.channel = 0
    elif waitKey == ord('8'):
        imgAdjust.channel = 1
    elif waitKey == ord('9'):
        imgAdjust.channel = 2
    elif waitKey == ord('0'):
        imgAdjust.channel = -1
    elif waitKey == ord(' '):
        imgAdjust.withContours ^= True

    return True


isImage= not videoFile is None and (videoFile.endswith(".png") or videoFile.endswith(".jpg"))
# Detection
with tf.Session(graph=tf.Graph()) as sess:
    tf.saved_model.loader.load(sess, ['serve'], modelPath)
    detection_graph=tf.get_default_graph()
    startTime = time.time()
    fpsProcess=0
    frameCount=0
    tensorFlowTime=0.1
    areaTime=0.1
    while True:
        # Read frame from camera
        _ret, image_np = stream.read()
        #print("Got Frame: %s", time.time())
        if image_np is not None:
            #detectTime = time.time()
            if dpsm==0:
                dpsm=image_np.shape[0]*image_np.shape[1]/real_area
            image_np=cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            # Extract image tensor
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            # Extract detection boxes
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            # Extract detection scores
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            # Extract detection classes
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            # Extract number of detections
            num_detections = detection_graph.get_tensor_by_name(
                'num_detections:0')
            # Actual detection.
            (boxes, scores, classes, num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})


            for i in range(len(boxes[0])):
                if(scores[0,i]>MIN_SCORE):
                   clam_grade.grade(image_np,boxes[0,i],classes[0,i],scores[0,i],dpsm, imgAdjust)

            frameCount+=1
            stopTime = time.time()
            if (stopTime >= 0.250):
                stop = time.time()
                elapsed = stopTime - startTime
                fpsProcess = frameCount / elapsed
                frameCount = 0
                #print("FPS Cap: %.1f    FPS Proc: %.1f" % (stream.fps, fpsProcess))
                startTime = time.time()
            # Display output
            cv2.putText(image_np, "FPS Cap: %.1f    FPS Proc: %.1f" % (stream.fps, fpsProcess), (0,20), cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(255, 255, 0),
                       thickness=1)
            cv2.imshow('object detection', cv2.resize(image_np, (800, 600)))

            if not waitForKey(stream,imgAdjust):
                break



