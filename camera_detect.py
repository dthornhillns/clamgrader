import numpy as np
import tensorflow as tf
from flask import Response
from flask import Flask
from flask import render_template
import cv2
import clam_grade
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
        config.showEnhanced = "hue"
    elif waitKey == ord('i'):
        config.showEnhanced = "threshold"
    elif waitKey == ord('o'):
        config.showEnhanced = "blur"
    elif waitKey == ord('p'):
        config.showEnhanced = "original"
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
app=Flask(__name__, template_folder="/home/mark/projects/Clam_Grader/templates")

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

class FieldOfView:
    regionOfInterestPixels = ((0, 0), (100, 100))
    regionOfMeasurementPixels = ((0, 0), (100, 100))

def startFlask():
    app.run(host="0.0.0.0", port=5000, debug=True,
            threaded=True, use_reloader=False)

def detect():
    print("Initializing detection")

    global outputFrame, lock

    config = cfg.loadConfig(configFile)
    dpsm = 0
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

    with open(config.labelsPath, "r") as labelFile:
        category_index = eval(labelFile.read())

    if config.plcEnabled:
        plc = plc_integration.PlcIntegration(0.001, config.plcIp, config.plcDestNode, config.plcSrcNode)

    isImage = not config.videoFile is None and (config.videoFile.endswith(".png") or config.videoFile.endswith(".jpg"))

    if config.plcEnabled:
        plc.start()

    # Detection
    with tf.Session(graph=tf.Graph()) as sess:
        tf.saved_model.loader.load(sess, ['serve'], config.modelPath)
        detection_graph = tf.get_default_graph()
        stream.start()
        startTime = time.time()
        fpsProcess = 0
        frameCount = 0
        tensorFlowTime = 0.000001
        areaTime = 0.000001
        while True:
            # Read frame from camera
            image_np = stream.frame
            # print("Got Frame: %s" % (time.time()))
            if image_np is not None:
                targets = []
                tensorFlowStartTime = time.time()
                if dpsm == 0:
                    dpsm = image_np.shape[0] * image_np.shape[1] / real_area

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
                    if (scores[0, i] > config.min_score):
                        box = boxes[0, i]
                        width = box[2] - box[0]
                        height = box[3] - box[1]
                        boxCenter = (box[0] + (width / 2), box[1] + (height / 2))
                        isOfInterest = (boxCenter[0] > config.regionOfInterest[1] and
                                        boxCenter[0] < config.regionOfInterest[3] and
                                        boxCenter[1] > config.regionOfInterest[0] and
                                        boxCenter[1] < config.regionOfInterest[2])
                        isOfMeasurement = (boxCenter[0] > config.regionOfMeasurement[1] and
                                           boxCenter[0] < config.regionOfMeasurement[3] and
                                           boxCenter[1] > config.regionOfMeasurement[0] and
                                           boxCenter[1] < config.regionOfMeasurement[2])
                        target = clam_grade.grade(isOfInterest, isOfMeasurement, boxCenter, image_np, destImg, boxes[0, i],
                                                  classes[0, i], scores[0, i], dpsm, config)
                        if not target is None:
                            if target.isOfInterest:
                                targets.append(target)

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
                stream.fps, fpsProcess, percentTensorFlow, percentArea), (0, 20), cv2.FONT_HERSHEY_PLAIN,
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

                cv2.rectangle(destImg, fov.regionOfInterestPixels[0], fov.regionOfInterestPixels[1],
                              color=(16, 16, 16), thickness=config.boxThickness)
                cv2.rectangle(destImg, fov.regionOfMeasurementPixels[0], fov.regionOfMeasurementPixels[1],
                              color=(16, 64, 64), thickness=config.boxThickness, )

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
    startFlask()
else:
    print("noDisplay is off")
    detect()
