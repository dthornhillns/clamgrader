import numpy as np
import tensorflow as tf
from tkinter import *
import cv2
import clam_grade
import argparse
import time
import plc_integration
from video_get import VideoGet

class FieldOfView:
    regionOfInterest=((0.1,0.1),(0.9,0.9))
    regionOfMeasurement=((0.3,0.1),(0.7,0.9))
    regionOfInterestPixels=((0,0),(100,100))
    regionOfMeasurementPixels=((0,0),(100,100))


parser = argparse.ArgumentParser()
parser.add_argument("-m","--model", required=True, help="Path to model")
parser.add_argument("-l","--labels", required=True, help="Path to labels")
parser.add_argument("-s","--minscore", type=float, help="Minumum score to filter", default=0.7)
parser.add_argument("-b","--boxthickness", type=int, help="Line thickness of bounding box", default=1)
parser.add_argument("-f","--fontScale", type=float, help="Font scale of all text", default=1.0)
parser.add_argument("-W","--width", type=float, help="Real width in cm", required=True)
parser.add_argument("-H","--height", type=float, help="Real height in cm", required=True)
parser.add_argument("-c","--camera", type=int, help="Use Camera with ID", default=0, required=False)
parser.add_argument("-v","--video", help="Use Video or JPG instead of Camera")
parser.add_argument("-cr","--capturerate", type=float, help="Adjust capture rate", default=0.01, required=False)
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
capRate=args["capturerate"]
real_area=real_width*real_height
plcPollTime=0.001
plcIp="192.168.3.10"
plcDestNode=10
plcSrcNode=25

imgAdjust=clam_grade.ImageAdjustment()
imgAdjust.boxThickness=args["boxthickness"]
imgAdjust.fontScale=args["fontScale"]
dpsm=0

cap=None

fov=FieldOfView()

if videoFile:
    cap = cv2.VideoCapture(videoFile)
elif cameraID>=0:
    cap = cv2.VideoCapture(cameraID)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

stream=VideoGet(cap, capRate)

with open(labelsPath,"r") as labelFile:
    category_index=eval(labelFile.read())

plc= plc_integration.PlcIntegration(0.001, plcIp, plcDestNode, plcSrcNode)

# Helper code
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

def waitForKey(stream, imgAdjust):
    waitKey=  cv2.waitKey(1) & 0xFF
    if  waitKey == ord('*'):
        stream.stop()
        plc.stop()
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
        imgAdjust.surf_hue_H+=10
    elif waitKey == ord('g'):
        imgAdjust.surf_saturation_H+=10
    elif waitKey == ord('h'):
        imgAdjust.surf_value_H+=10
    elif waitKey == ord('v'):
        imgAdjust.surf_hue_H-=10
    elif waitKey == ord('b'):
        imgAdjust.surf_saturation_H-=10
    elif waitKey == ord('n'):
        imgAdjust.surf_value_H-=10
    elif waitKey == ord('j'):
        imgAdjust.surf_hue_L+=10
    elif waitKey == ord('k'):
        imgAdjust.surf_saturation_L+=10
    elif waitKey == ord('l'):
        imgAdjust.surf_value_L+=10
    elif waitKey == ord('m'):
        imgAdjust.surf_hue_L-=10
    elif waitKey == ord(','):
        imgAdjust.surf_saturation_L-=10
    elif waitKey == ord('.'):
        imgAdjust.surf_value_L-=10
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

plc.start()

# Detection
with tf.Session(graph=tf.Graph()) as sess:
    tf.saved_model.loader.load(sess, ['serve'], modelPath)
    detection_graph=tf.get_default_graph()
    stream.start()
    startTime = time.time()
    fpsProcess=0
    frameCount=0
    tensorFlowTime=0.000001
    areaTime=0.000001
    while True:
        # Read frame from camera
        image_np = stream.frame
        #print("Got Frame: %s" % (time.time()))
        if image_np is not None:
            targets=[]
            tensorFlowStartTime = time.time()
            if dpsm==0:
                dpsm=image_np.shape[0]*image_np.shape[1]/real_area

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

            destImg = image_np.copy()
            areaStartTime = time.time()
            for i in range(len(boxes[0])):
                if(scores[0,i]>MIN_SCORE):
                    box=boxes[0,i]
                    width=box[2]-box[0]
                    height=box[3]-box[1]
                    boxCenter=(box[0]+(width/2),box[1]+(height/2))
                    isOfInterest=(boxCenter[0]>fov.regionOfInterest[0][1] and
                                    boxCenter[0] < fov.regionOfInterest[1][1] and
                                    boxCenter[1]>fov.regionOfInterest[0][0] and
                                    boxCenter[1]<fov.regionOfInterest[1][0])
                    isOfMeasurement = (boxCenter[0] > fov.regionOfMeasurement[0][1] and
                                    boxCenter[0] < fov.regionOfMeasurement[1][1] and
                                    boxCenter[1] > fov.regionOfMeasurement[0][0] and
                                    boxCenter[1] < fov.regionOfMeasurement[1][0])
                    target=clam_grade.grade(isOfInterest,isOfMeasurement,boxCenter, image_np,destImg,boxes[0,i],classes[0,i],scores[0,i],dpsm, imgAdjust)
                    if not target is None:
                        if target.isOfInterest:
                            targets.append(target)

            frameCount+=1
            stopTime = time.time()
            tensorFlowTime+=areaStartTime-tensorFlowStartTime
            areaTime+=stopTime-areaStartTime

            if (stopTime >= 0.250):
                stop = time.time()
                elapsed = stopTime - startTime
                fpsProcess = frameCount / elapsed
                frameCount = 0
                startTime = time.time()
                totalTime=areaTime+tensorFlowTime
                percentTensorFlow=(tensorFlowTime/totalTime)*100
                percentArea=(areaTime/totalTime)*100
                tensorFlowTime=0
                areaTime=0
            # Display output
            cv2.putText(destImg, "FPS Cap: %.1f    FPS Proc: %.1f  TensorFlow: %.1f    Area: %.1f" % (stream.fps, fpsProcess, percentTensorFlow, percentArea), (0,20), cv2.FONT_HERSHEY_PLAIN, fontScale=imgAdjust.fontScale, color=(255, 255, 0),
                       thickness=1)

            roi_ul = (int(fov.regionOfInterest[0][0] * destImg.shape[1]), int(fov.regionOfInterest[0][1] * destImg.shape[0]))
            roi_lr = (int(fov.regionOfInterest[1][0] * destImg.shape[1]), int(fov.regionOfInterest[1][1] * destImg.shape[0]))
            fov.regionOfInterestPixels = (roi_ul, roi_lr)
            rom_ul = (int(fov.regionOfMeasurement[0][0] * destImg.shape[1]), int(fov.regionOfMeasurement[0][1] * destImg.shape[0]))
            rom_lr = (int(fov.regionOfMeasurement[1][0] * destImg.shape[1]), int(fov.regionOfMeasurement[1][1] * destImg.shape[0]))
            fov.regionOfMeasurementPixels = (rom_ul, rom_lr)

            cv2.rectangle(destImg,fov.regionOfInterestPixels[0],fov.regionOfInterestPixels[1],
                          color=(16,16,16),thickness=imgAdjust.boxThickness)
            cv2.rectangle(destImg, fov.regionOfMeasurementPixels[0], fov.regionOfMeasurementPixels[1],
                          color=(16, 64, 64), thickness=imgAdjust.boxThickness, )

            w1=destImg.shape[1]
            h1=destImg.shape[0]
            w2=1600
            h2=h1*w2/w1
            cv2.imshow('object detection', cv2.resize(destImg, (int(w2),int(h2) )))
            if plc.targetsRequested and len(targets)>0:
                plc.sendTargets(targets)

            if not waitForKey(stream,imgAdjust):
                break



