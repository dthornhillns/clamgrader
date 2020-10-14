import numpy as np
import math
from flask import Response, request
from flask import Flask
from flask import render_template
import cv2
import clam_grade
import clam_log
import argparse
import time
import plc_integration
import threading
import configuration as cfg
from video_get import VideoGet

outputFrame = None
lock = threading.Lock()

# Helper code
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


def waitForKey(stream, config, plc):
    waitKey = cv2.waitKey(1) & 0xFF
    if waitKey == ord('*'):
        stream.stop()
        if plc:
            plc.stop()
        cv2.destroyAllWindows()
        return False
    elif waitKey == ord('x'):
        config.contrast += 10
    elif waitKey == ord('z'):
        config.contrast -= 10
    elif waitKey == ord('s'):
        config.brightness += 10
    elif waitKey == ord('a'):
        config.brightness -= 10
    elif waitKey == ord('w'):
        config.minThreshold += 10
    elif waitKey == ord('q'):
        config.minThreshold -= 10
    elif waitKey == ord('2'):
        config.maxThreshold += 10
    elif waitKey == ord('1'):
        config.maxThreshold -= 10
    elif waitKey == ord('f'):
        config.surf_hue_H += 10
    elif waitKey == ord('g'):
        config.surf_saturation_H += 10
    elif waitKey == ord('h'):
        config.surf_value_H += 10
    elif waitKey == ord('v'):
        config.surf_hue_H -= 10
    elif waitKey == ord('b'):
        config.surf_saturation_H -= 10
    elif waitKey == ord('n'):
        config.surf_value_H -= 10
    elif waitKey == ord('j'):
        config.surf_hue_L += 10
    elif waitKey == ord('k'):
        config.surf_saturation_L += 10
    elif waitKey == ord('l'):
        config.surf_value_L += 10
    elif waitKey == ord('m'):
        config.surf_hue_L -= 10
    elif waitKey == ord(','):
        config.surf_saturation_L -= 10
    elif waitKey == ord('.'):
        config.surf_value_L -= 10
    elif waitKey == ord('3'):
        config.blur -= 1
    elif waitKey == ord('4'):
        config.blur += 1
    elif waitKey == ord('u'):
        config.showEnhanced = 0
    elif waitKey == ord('i'):
        config.showEnhanced = 1
    elif waitKey == ord('o'):
        config.showEnhanced = 2
    elif waitKey == ord('p'):
        config.showEnhanced = 3
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

def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--config", help="Config file for detection environment in JSON format", required=True)
parser.add_argument("-n", "--nodisplay", help="Operate in headless mode", action="store_true")
args = vars(parser.parse_args())

configFile = args["config"]
noDisplay = args["nodisplay"]
config = cfg.loadConfig(configFile)
app=Flask(__name__)

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html", hue_L=config.hue_L, hue_H=config.hue_H, saturation_L=config.saturation_L, saturation_H=config.saturation_H, value_L=config.value_L, value_H=config.value_H)

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/config", methods=['PUT'])
def set_config():
    configJson = request.get_json(force=True)
    config.hue_L = configJson["hue_L"]
    config.hue_H = configJson["hue_H"]
    config.saturation_L = configJson["saturation_L"]
    config.saturation_H = configJson["saturation_H"]
    config.value_L = configJson["value_L"]
    config.value_H = configJson["value_H"]
    config.showEnhanced = configJson["showEnhanced"]
    return Response(status=200)

@app.route("/config", methods=['POST'])
def save_config():
    config.save(configFile)
    return Response(status=200)

class FieldOfView:
    regionOfInterestPixels = ((0, 0), (100, 100))
    regionOfMeasurementPixels = ((0, 0), (100, 100))

def startFlask(config):
    app.run(host="0.0.0.0", port=config.diagnosticsPort, debug=False,
            threaded=True, use_reloader=False)

def calculateDistance(p1,p2):
    dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    return dist

def detect():
    print("Initializing detection")

    global outputFrame, lock, config

    dpsm = 72
    cap = None
    plc = None

    real_area = config.real_height * config.real_width

    fov = FieldOfView()

    if config.videoFile:
        cap = cv2.VideoCapture(config.videoFile)
    elif config.cameraID >= 0:
        cap = cv2.VideoCapture(config.cameraID)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    stream = VideoGet(cap, config.capRate)


    if config.plcEnabled:
        plc = plc_integration.PlcIntegration(0.001, config.plcIp, config.plcDestNode, config.plcSrcNode)

    isImage = not config.videoFile is None and (config.videoFile.endswith(".png") or config.videoFile.endswith(".jpg"))

    if config.plcEnabled:
        plc.start()

    # Detection

    stream.start()
    startTime = time.time()
    fpsProcess = 0
    frameCount = 0
    tensorFlowTime = 0.000001
    areaTime = 0.000001

    blobParams = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    blobParams.minThreshold = 30;
    blobParams.maxThreshold = 60;

    # Filter by Area.
    blobParams.filterByArea = False
    blobParams.minArea = 1500

    # Filter by Circularity
    blobParams.filterByCircularity = False
    blobParams.minCircularity = 0.1

    # Filter by Convexity
    blobParams.filterByConvexity = False
    blobParams.minConvexity = 0.87

    # Filter by Inertia
    blobParams.filterByInertia = False
    blobParams.minInertiaRatio = 0.01

    # Create a detector with the parameters
    ver = (cv2.__version__).split('.')
    if int(ver[0]) < 3:
        detector = cv2.SimpleBlobDetector(blobParams)
    else:
        detector = cv2.SimpleBlobDetector_create(blobParams)

    lastSampleTime=time.time()
    while True:
        # Read frame from camera
        image_np = stream.frame
        # print("Got Frame: %s" % (time.time()))
        currentSampleTime=time.time()
        writeTargets=False
        if (currentSampleTime - lastSampleTime) >= 2.0:
            writeTargets=True
            lastSampleTime = currentSampleTime
        if image_np is not None:
            targets = []
            tensorFlowStartTime = time.time()
            imgSteps=clam_grade.preprocess(image_np,config)
            contours, _ = cv2.findContours(imgSteps[3], cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

            destImg = imgSteps[config.showEnhanced].copy()
            cv2.rectangle(destImg, fov.regionOfInterestPixels[0], fov.regionOfInterestPixels[1],
                          color=(16, 16, 16), thickness=config.boxThickness)
            cv2.rectangle(destImg, fov.regionOfMeasurementPixels[0], fov.regionOfMeasurementPixels[1],
                          color=(16, 64, 64), thickness=config.boxThickness)
            radius = int(destImg.shape[1] * config.doubleTargetThreshold)
            areaStartTime = time.time()
            imageArea = image_np.shape[0]*image_np.shape[1]
            for i in range(len(contours)):
                contour=contours[i]
                box=cv2.boundingRect(contour)
                width = box[2]
                height = box[3]
                boxArea = width * height
                percentArea = boxArea / imageArea
                if percentArea >= 0.01 and percentArea <=0.5:
                    boxNormalCenter = ((box[0] + (width / 2))/image_np.shape[0], (box[1] + (height / 2))/image_np.shape[1])
                    isOfInterest = (boxNormalCenter[0] > config.regionOfInterest[1] and
                                    boxNormalCenter[0] < config.regionOfInterest[3] and
                                    boxNormalCenter[1] > config.regionOfInterest[0] and
                                    boxNormalCenter[1] < config.regionOfInterest[2])
                    isOfMeasurement = (boxNormalCenter[0] > config.regionOfMeasurement[1] and
                                       boxNormalCenter[0] < config.regionOfMeasurement[3] and
                                       boxNormalCenter[1] > config.regionOfMeasurement[0] and
                                       boxNormalCenter[1] < config.regionOfMeasurement[2])
                    target = clam_grade.grade(isOfInterest, isOfMeasurement, (box[0]+int(box[2]/2),box[1]+int(box[3]/2)), image_np, destImg, box,
                                              dpsm, config)
                    if not target is None:
                        targetColor = (32,32,32) if not target.isOfInterest else (255, 255, 0) if target.classification == 2 else (0, 255, 255)
                        cv2.drawContours(destImg,contours,i,targetColor,thickness=1)
                        cv2.rectangle(destImg,(target.box[0],target.box[1]),(target.box[0]+target.box[2],target.box[1]+target.box[3]),targetColor)
                        cv2.circle(destImg, target.center, radius, (0, 255, 0), thickness=1)
                        cv2.putText(destImg, "RED: %.1f    AREA: %.1f" % (
                            target.percentRed*100, target.areaSquareMm), (target.box[0], target.box[1]), cv2.FONT_HERSHEY_PLAIN,
                                    fontScale=config.fontScale, color=targetColor,
                                    thickness=1)
                        if writeTargets:
                            clam_log.write_clam(config,target)

            frameCount += 1
            stopTime = time.time()
            tensorFlowTime += areaStartTime - tensorFlowStartTime
            areaTime += stopTime - areaStartTime

            if (stopTime >= 0.250):
                stop = time.time()
                elapsed = stopTime - startTime
                fpsProcess = frameCount / elapsed
                frameCount = 0
                startTime = time.time()
                totalTime = areaTime + tensorFlowTime
                percentTensorFlow = (tensorFlowTime / totalTime) * 100
                percentArea = (areaTime / totalTime) * 100
                tensorFlowTime = 0
                areaTime = 0
                # Display output
                cv2.putText(destImg, "FPS Cap: %.1f    FPS Proc: %.1f  TensorFlow: %.1f    Area: %.1f" % (
                stream.fps, fpsProcess, percentTensorFlow, percentArea), (0, destImg.shape[1]-200), cv2.FONT_HERSHEY_PLAIN,
                            fontScale=config.fontScale, color=(255, 255, 0),
                            thickness=1)

                roi_ul = (
                int(config.regionOfInterest[0] * destImg.shape[1]), int(config.regionOfInterest[1] * destImg.shape[0]))
                roi_lr = (
                int(config.regionOfInterest[2] * destImg.shape[1]), int(config.regionOfInterest[3] * destImg.shape[0]))
                fov.regionOfInterestPixels = (roi_ul, roi_lr)
                rom_ul = (int(config.regionOfMeasurement[0] * destImg.shape[1]),
                          int(config.regionOfMeasurement[1] * destImg.shape[0]))
                rom_lr = (int(config.regionOfMeasurement[2] * destImg.shape[1]),
                          int(config.regionOfMeasurement[3] * destImg.shape[0]))
                fov.regionOfMeasurementPixels = (rom_ul, rom_lr)

                w1 = destImg.shape[1]
                h1 = destImg.shape[0]
                w2 = config.windowWidth
                h2 = h1 * w2 / w1
                cvImg = cv2.resize(destImg, (int(w2), int(h2)))
                if noDisplay:
                    with lock:
                        outputFrame=cvImg.copy()
                else:
                    cv2.imshow('object detection', cvImg)
                if plc and plc.targetsRequested and len(targets) > 0:
                    print("%s: Sending %d targets" % (time.time(), len(targets)))
                    plc.sendTargets(targets)

                if not waitForKey(stream, config, plc):
                    break

if (noDisplay):
    print("noDisplay is on")
    threading.Thread(target=detect).start()
    startFlask(config)
else:
    print("noDisplay is off")
    detect()
