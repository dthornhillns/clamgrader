import json

class SizeClass:
    def __init__(self, name, min):
        self.name = name
        self.min = min

class DetectionConfig:
    def __init__(self):
        self.elasticsearch = ""
        self.diagnosticsPort = 5000
        self.contrast = 0
        self.brightness = 0
        self.threshold_L = 30
        self.threshold_H = 60
        self.showEnhanced = "original"
        self.channel = 2
        self.blur = 5
        self.hue_L = -16
        self.saturation_L = -7
        self.value_L = 2
        self.hue_H = 185
        self.saturation_H = 165
        self.value_H = 245
        self.withContours = True
        self.boxThickness = 1
        self.fontScale = 1
        self.surf_red_percent = 7.0
        self.surf_hue_L = 5
        self.surf_saturation_L = 5
        self.surf_value_L = 69
        self.surf_hue_H = 80
        self.surf_saturation_H = 255
        self.surf_value_H = 255
        self.modelPath = None

        # List of the strings that is used to add correct label for each box.
        self.labelsPath = None

        # Number of classes to detect
        self.num_classes = 2
        self.min_score = 0.7
        self.real_width = 1000.0
        self.real_height = 1000.0
        self.videoFile = None
        self.cameraID = None
        self.capRate = 0.02
        self.plcPollTime = 0.01
        self.plcIp = "192.168.0.121"
        self.plcDestNode = 121
        self.plcSrcNode = 25
        self.plcEnabled = False
        self.windowWidth = 1600
        self.regionOfInterest = None
        self.regionOfMeasurement = None
        self.doubleTargetThreshold=0.01
        self.surfSizesFile = None
        self.surfSizes = []
        self.calibrationBox = None
        self.calibrationBoxThickness=3
        self.writeToElastic = False

    def getJson(self):
        data = {
            "elasticsearch": self.elasticsearch,
            "diagnosticsPort": self.diagnosticsPort,
            "contrast": self.contrast,
            "brightness": self.brightness,
            "threshold_L": self.threshold_L,
            "threshold_H": self.threshold_H,
            "showEnhanced": self.showEnhanced,
            "channel": self.channel,
            "blur": self.blur,
            "value_L": self.hue_L,
            "hue_L": self.hue_L,
            "saturation_L": self.saturation_L,
            "hue_H": self.hue_H,
            "saturation_H": self.saturation_H,
            "value_H": self.value_H,
            "surf_red_percent": self.surf_red_percent,
            "surf_hue_L": self.surf_hue_L,
            "surf_saturation_L": self.surf_saturation_L,
            "surf_value_L": self.surf_value_L,
            "surf_hue_H": self.surf_hue_H,
            "surf_saturation_H": self.surf_saturation_H,
            "surf_value_H": self.surf_value_H,
            "modelPath": self.modelPath,
            "labelsPath": self.labelsPath,
            "min_score": self.min_score,
            "num_classes": self.num_classes,
            "real_width": self.real_width,
            "real_height": self.real_height,
            "capRate": self.capRate,
            "plcPollTime": self.plcPollTime,
            "plcIp": self.plcIp,
            "plcDestNode": self.plcDestNode,
            "plcSrcNode": self.plcSrcNode,
            "plcEnabled": self.plcEnabled,
            "windowWidth": self.windowWidth,
            "regionOfInterest": self.regionOfInterest,
            "regionOfMeasurement": self.regionOfMeasurement,
            "doubleTargetThreshold": self.doubleTargetThreshold,
            "surfSizesFile": self.surfSizesFile,
            "calibrationBox": self.calibrationBox,
            "calibrationBoxThickness": self.calibrationBoxThickness,
            "writeToElastic": self.writeToElastic

        }
        if self.videoFile:
            data["videoFile"] = self.videoFile
        if self.cameraID:
            data["cameraID"] = self.cameraID
        return data

    def save(self, path):
        jsonFile = open(path, "w")
        data=self.getJson()
        json.dump(data, jsonFile,indent=4, sort_keys=True)

def loadConfig(path):
    config = DetectionConfig()
    jsonFile = open(path,"r")
    jsonDict = json.load(jsonFile)
    config.elasticsearch = jsonDict["elasticsearch"]
    config.diagnosticsPort = jsonDict["diagnosticsPort"]
    config.contrast = jsonDict["contrast"]
    config.brightness = jsonDict["brightness"]
    config.threshold_L = jsonDict["threshold_L"]
    config.threshold_H = jsonDict["threshold_H"]
    config.showEnhanced = jsonDict["showEnhanced"]
    config.channel = jsonDict["channel"]
    config.blur = jsonDict["blur"]
    config.hue_L = jsonDict["hue_L"]
    config.saturation_L = jsonDict["saturation_L"]
    config.value_L = jsonDict["value_L"]
    config.hue_H = jsonDict["hue_H"]
    config.saturation_H = jsonDict["saturation_H"]
    config.value_H = jsonDict["value_H"]
    config.surf_red_percent = jsonDict["surf_red_percent"]
    config.surf_hue_L = jsonDict["surf_hue_L"]
    config.surf_saturation_L = jsonDict["surf_saturation_L"]
    config.surf_value_L = jsonDict["surf_value_L"]
    config.surf_hue_H = jsonDict["surf_hue_H"]
    config.surf_saturation_H = jsonDict["surf_saturation_H"]
    config.surf_value_H = jsonDict["surf_value_H"]
    config.modelPath = jsonDict["modelPath"]
    config.labelsPath = jsonDict["labelsPath"]
    config.min_score = jsonDict["min_score"]
    config.num_classes = jsonDict["num_classes"]
    config.real_width = jsonDict["real_width"]
    config.real_height = jsonDict["real_height"]
    if "videoFile" in jsonDict:
        config.videoFile = jsonDict["videoFile"]
    if "cameraID" in jsonDict:
        config.cameraID = jsonDict["cameraID"]
    config.capRate = jsonDict["capRate"]
    config.plcPollTime = jsonDict["plcPollTime"]
    config.plcIp = jsonDict["plcIp"]
    config.plcDestNode = jsonDict["plcDestNode"]
    config.plcSrcNode = jsonDict["plcSrcNode"]
    config.plcEnabled = jsonDict["plcEnabled"]
    config.windowWidth = jsonDict["windowWidth"]
    config.regionOfInterest = jsonDict["regionOfInterest"]
    config.regionOfMeasurement = jsonDict["regionOfMeasurement"]
    config.doubleTargetThreshold = jsonDict["doubleTargetThreshold"]
    config.surfSizesFile = jsonDict["surfSizesFile"]
    config.calibrationBox = jsonDict["calibrationBox"]
    config.calibrationBoxThickness = jsonDict["calibrationBoxThickness"]
    config.writeToElastic = jsonDict["writeToElastic"]

    sizesJsonFile = open(config.surfSizesFile,"r")
    sizesJson = json.load(sizesJsonFile)
    for sizeName in sizesJson:
        config.surfSizes.append(SizeClass(sizeName, sizesJson[sizeName]))
    config.surfSizes.sort(key=lambda x: x.min, reverse=True)
    return config


