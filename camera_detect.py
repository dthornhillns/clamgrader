import numpy as np
import tensorflow as tf
import cv2
import clam_grade
import argparse
from video_stream import VideoStream


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
    cap=cv2.VideoCapture(videoFile)
elif cameraID:
    cap = cv2.VideoCapture(cameraID)

stream=VideoStream(cap)

# Loading label map
# Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine
#label_map = label_map_util.load_labelmap(labelsPath)
#categories = label_map_util.convert_label_map_to_categories(
#    label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
#category_index = label_map_util.create_category_index(categories)
with open(labelsPath,"r") as labelFile:
    category_index=eval(labelFile.read())

# Helper code
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

isImage= not videoFile is None and videoFile.endswith(".png") or videoFile.endswith(".jpg")
# Detection
with tf.Session(graph=tf.Graph()) as sess:
    tf.saved_model.loader.load(sess, ['serve'], modelPath)
    detection_graph=tf.get_default_graph()
    lastImg = None
    stream.start()
    while True:
        # Read frame from camera
        image_np = stream.read()

        if image_np is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            image_np=lastImg.copy()
        else:
            lastImg=image_np.copy()


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


        for i in range(len(boxes[0])):
            if(scores[0,i]>MIN_SCORE):
                clam_grade.grade(image_np,boxes[0,i],classes[0,i],scores[0,i],dpsm, imgAdjust)



        # Display output
        cv2.imshow('object detection', cv2.resize(image_np, (800, 600)))

        waitKey=  cv2.waitKey(25) & 0xFF
        if  waitKey == ord('*'):
            stream.stop()
            cv2.destroyAllWindows()
            break
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


