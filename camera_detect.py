import numpy as np
import tensorflow as tf
from tkinter import *
import cv2
import clam_grade
import argparse
import time
import plc_integration
import configuration as cfg
from video_get import VideoGet

class FieldOfView:
    regionOfInterestPixels=((0,0),(100,100))
    regionOfMeasurementPixels=((0,0),(100,100))


parser = argparse.ArgumentParser()
parser.add_argument("-f","--config", help="Config file for detection environment in JSON format", required=True)
args=vars(parser.parse_args())

configFile=args["config"]

config = cfg.loadConfig(configFile)

real_area=config.real_height*config.real_width

dpsm=0

cap=None
plc=None

fov=FieldOfView()

if config.videoFile:
    cap = cv2.VideoCapture(config.videoFile)
elif config.cameraID>=0:
    cap = cv2.VideoCapture(config.cameraID)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

stream=VideoGet(cap, config.capRate)

with open(config.labelsPath,"r") as labelFile:
    category_index=eval(labelFile.read())

if config.plcEnabled:
    plc = plc_integration.PlcIntegration(0.001, config.plcIp, config.plcDestNode, config.plcSrcNode)

# Helper code
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

def waitForKey(stream, config):
    waitKey=  cv2.waitKey(1) & 0xFF
    if  waitKey == ord('*'):
        stream.stop()
        if plc:
            plc.stop()
        cv2.destroyAllWindows()
        return False
    elif waitKey == ord('x'):
        config.contrast+=10
    elif waitKey == ord('z'):
        config.contrast-=10
    elif waitKey == ord('s'):
        config.brightness += 10
    elif waitKey == ord('a'):
        config.brightness -= 10
    elif waitKey == ord('w'):
        config.minThreshold+=10
    elif waitKey == ord('q'):
        config.minThreshold-=10
    elif waitKey == ord('2'):
        config.maxThreshold+=10
    elif waitKey == ord('1'):
        config.maxThreshold-=10
    elif waitKey == ord('f'):
        config.surf_hue_H+=10
    elif waitKey == ord('g'):
        config.surf_saturation_H+=10
    elif waitKey == ord('h'):
        config.surf_value_H+=10
    elif waitKey == ord('v'):
        config.surf_hue_H-=10
    elif waitKey == ord('b'):
        config.surf_saturation_H-=10
    elif waitKey == ord('n'):
        config.surf_value_H-=10
    elif waitKey == ord('j'):
        config.surf_hue_L+=10
    elif waitKey == ord('k'):
        config.surf_saturation_L+=10
    elif waitKey == ord('l'):
        config.surf_value_L+=10
    elif waitKey == ord('m'):
        config.surf_hue_L-=10
    elif waitKey == ord(','):
        config.surf_saturation_L-=10
    elif waitKey == ord('.'):
        config.surf_value_L-=10
    elif waitKey == ord('3'):
        config.blur-=1
    elif waitKey == ord('4'):
        config.blur+=1
    elif waitKey == ord('u'):
        config.showEnhanced= "hue"
    elif waitKey == ord('i'):
        config.showEnhanced= "threshold"
    elif waitKey == ord('o'):
        config.showEnhanced= "blur"
    elif waitKey == ord('p'):
        config.showEnhanced= "original"
    elif waitKey == ord('7'):
        config.channel = 0
    elif waitKey == ord('8'):
        config.channel = 1
    elif waitKey == ord('9'):
        config.channel = 2
    elif waitKey == ord('0'):
        config.channel = -1
    elif waitKey == ord(' '):
        config.withContours ^= True

    return True


isImage = not config.videoFile is None and (config.videoFile.endswith(".png") or config.videoFile.endswith(".jpg"))

if config.plcEnabled:
    plc.start()

# Detection
with tf.Session(graph=tf.Graph()) as sess:
    tf.saved_model.loader.load(sess, ['serve'], config.modelPath)
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
                if(scores[0,i]>config.min_score):
                    box=boxes[0,i]
                    width=box[2]-box[0]
                    height=box[3]-box[1]
                    boxCenter=(box[0]+(width/2),box[1]+(height/2))
                    isOfInterest=(boxCenter[0]>config.regionOfInterest[1] and
                                    boxCenter[0] < config.regionOfInterest[3] and
                                    boxCenter[1]>config.regionOfInterest[0] and
                                    boxCenter[1]<config.regionOfInterest[2])
                    isOfMeasurement = (boxCenter[0] > config.regionOfMeasurement[1] and
                                    boxCenter[0] < config.regionOfMeasurement[3] and
                                    boxCenter[1] > config.regionOfMeasurement[0] and
                                    boxCenter[1] < config.regionOfMeasurement[2])
                    target=clam_grade.grade(isOfInterest,isOfMeasurement,boxCenter, image_np,destImg,boxes[0,i],classes[0,i],scores[0,i],dpsm, config)
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
            cv2.putText(destImg, "FPS Cap: %.1f    FPS Proc: %.1f  TensorFlow: %.1f    Area: %.1f" % (stream.fps, fpsProcess, percentTensorFlow, percentArea), (0,20), cv2.FONT_HERSHEY_PLAIN, fontScale=config.fontScale, color=(255, 255, 0),
                       thickness=1)

            roi_ul = (int(config.regionOfInterest[0] * destImg.shape[1]), int(config.regionOfInterest[1] * destImg.shape[0]))
            roi_lr = (int(config.regionOfInterest[2] * destImg.shape[1]), int(config.regionOfInterest[3] * destImg.shape[0]))
            fov.regionOfInterestPixels = (roi_ul, roi_lr)
            rom_ul = (int(config.regionOfMeasurement[0] * destImg.shape[1]), int(config.regionOfMeasurement[1] * destImg.shape[0]))
            rom_lr = (int(config.regionOfMeasurement[2] * destImg.shape[1]), int(config.regionOfMeasurement[3] * destImg.shape[0]))
            fov.regionOfMeasurementPixels = (rom_ul, rom_lr)

            cv2.rectangle(destImg,fov.regionOfInterestPixels[0],fov.regionOfInterestPixels[1],
                          color=(16,16,16),thickness=config.boxThickness)
            cv2.rectangle(destImg, fov.regionOfMeasurementPixels[0], fov.regionOfMeasurementPixels[1],
                          color=(16, 64, 64), thickness=config.boxThickness, )

            w1=destImg.shape[1]
            h1=destImg.shape[0]
            w2=config.windowWidth
            h2=h1*w2/w1
            cv2.imshow('object detection', cv2.resize(destImg, (int(w2),int(h2) )))
            if plc and plc.targetsRequested and len(targets)>0:
                print("%s: Sending %d targets" %(time.time(),len(targets)))
                plc.sendTargets(targets)

            if not waitForKey(stream,config):
                break



