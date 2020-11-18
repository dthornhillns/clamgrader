import numpy as np
import math
from flask import Response, request
from flask import Flask
from flask import render_template
from flask import jsonify
import flask_cors
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
app = Flask(__name__)


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html", hue_L=config.hue_L, hue_H=config.hue_H, saturation_L=config.saturation_L,
                           saturation_H=config.saturation_H, value_L=config.value_L, value_H=config.value_H,
                           threshold_L=config.minThreshold, threshold_H=config.maxThreshold,
                           roi_X1=config.regionOfInterest[0] * 100, roi_Y1=config.regionOfInterest[1] * 100,
                           roi_X2=config.regionOfInterest[2] * 100, roi_Y2=config.regionOfInterest[3] * 100)


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/config", methods=['PUT'])
def set_config():
    configJson = request.get_json(force=True)
    for configName in configJson:
        if (hasattr(config, configName)):
            setattr(config, configName, configJson[configName])

    return Response(status=200)


@app.route("/config", methods=['POST'])
def save_config():
    config.save(configFile)
    return Response(status=200)

@app.route("/config", methods=['GET'])
def get_config():
    data=config.getJson()
    return jsonify(data)


class FieldOfView:
    regionOfInterestPixels = ((0, 0), (100, 100))


def startFlask(config):
    app.run(host="0.0.0.0", port=config.diagnosticsPort, debug=False,
            threaded=True, use_reloader=False)


def calculateDistance(p1, p2):
    dist = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
    return dist


def calculateDpsmm(widthPx, heightPx, config):
    calWidthPx = (config.calibrationBox[2] - config.calibrationBox[0]) * widthPx
    calhHeightPx = (config.calibrationBox[3] - config.calibrationBox[1]) * heightPx
    areaPx = calWidthPx * calhHeightPx
    areaMm = config.real_width * config.real_height
    return areaPx / areaMm


def detect():
    print("Initializing detection")

    global outputFrame, lock, config

    cap = None
    plc = None

    fov = FieldOfView()

    if config.videoFile:
        cap = cv2.VideoCapture(config.videoFile)
    elif config.cameraID:
        cap = cv2.VideoCapture(config.cameraID)

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

    lastSampleTime = time.time()
    while True:
        # Read frame from camera
        image_np = stream.frame
        # print("Got Frame: %s" % (time.time()))
        currentSampleTime = time.time()
        writeTargets = False
        if (currentSampleTime - lastSampleTime) >= 2.0:
            writeTargets = True
            lastSampleTime = currentSampleTime
        if image_np is not None:
            targets = []
            tensorFlowStartTime = time.time()
            imgSteps = clam_grade.preprocess(image_np, config)
            contours, _ = cv2.findContours(imgSteps[4], cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

            if config.showEnhanced==100:
                destImg = imgSteps[0].copy()
                calibrationUL = (
                    int(destImg.shape[1] * config.calibrationBox[0]), int(destImg.shape[0] * config.calibrationBox[1]))
                calibrationLR = (
                    int(destImg.shape[1] * config.calibrationBox[2]), int(destImg.shape[0] * config.calibrationBox[3]))
                cv2.rectangle(destImg,
                              calibrationUL,
                              calibrationLR,
                              color=(16, 200, 200), thickness=config.calibrationBoxThickness)
            else:
                destImg = imgSteps[config.showEnhanced].copy()


            dpsmm = calculateDpsmm(destImg.shape[0], destImg.shape[0], config)
            cv2.rectangle(destImg, fov.regionOfInterestPixels[0], fov.regionOfInterestPixels[1],
                          color=(16, 16, 16), thickness=config.boxThickness)

            radius = int(destImg.shape[1] * config.doubleTargetThreshold)
            areaStartTime = time.time()
            imageArea = image_np.shape[0] * image_np.shape[1]
            for i in range(len(contours)):
                contour = contours[i]
                box = cv2.boundingRect(contour)
                width = box[2]
                height = box[3]
                boxArea = width * height
                percentArea = boxArea / imageArea
                if percentArea >= 0.01 and percentArea <= 0.5:

                    isOfInterest = True
                    isOfMeasurement = True

                    target = clam_grade.grade(isOfInterest, isOfMeasurement,
                                              (box[0] + int(box[2] / 2), box[1] + int(box[3] / 2)), image_np, destImg,
                                              box,
                                              dpsmm, config)
                    if not target is None:
                        targetColor = (0, 255, 0) if not target.isOfInterest else (
                        255, 255, 0) if target.classification == 2 else (0, 255, 255)
                        cv2.drawContours(destImg, contours, i, targetColor, thickness=1)
                        cv2.rectangle(destImg, (target.box[0], target.box[1]),
                                      (target.box[0] + target.box[2], target.box[1] + target.box[3]), targetColor)
                        cv2.circle(destImg, target.center, radius, (0, 255, 0), thickness=1)
                        cv2.putText(destImg, "RED: %.1f    AREA: %.1f" % (
                            target.percentRed * 100, target.areaSquareMm), (target.box[0], target.box[1]),
                                    cv2.FONT_HERSHEY_PLAIN,
                                    fontScale=config.fontScale, color=targetColor,
                                    thickness=1)
                        if writeTargets:
                            clam_log.write_clam(config, target)

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
                    stream.fps, fpsProcess, percentTensorFlow, percentArea), (0, destImg.shape[1] - 200),
                            cv2.FONT_HERSHEY_PLAIN,
                            fontScale=config.fontScale, color=(255, 255, 0),
                            thickness=1)

                roi_ul = (
                    int(config.regionOfInterest[0] * destImg.shape[1]),
                    int(config.regionOfInterest[1] * destImg.shape[0]))
                roi_lr = (
                    int(config.regionOfInterest[2] * destImg.shape[1]),
                    int(config.regionOfInterest[3] * destImg.shape[0]))
                fov.regionOfInterestPixels = (roi_ul, roi_lr)

                w1 = destImg.shape[1]
                h1 = destImg.shape[0]
                w2 = config.windowWidth
                h2 = h1 * w2 / w1
                cvImg = cv2.resize(destImg, (int(w2), int(h2)))
                if noDisplay:
                    with lock:
                        outputFrame = cvImg.copy()
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
