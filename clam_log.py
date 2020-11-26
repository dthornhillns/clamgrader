import sys

import requests
import datetime

def write_clam(config, target, img):
    if(config.writeToElastic):
        saveTarget = {
            "@timestamp": datetime.datetime.now().isoformat(),
            "species": "surf" if target.classification == 2.0 else "cockle",
            "pixelAreaMm": target.pixelAreaMm,
            "contourAreaMm": target.contourAreaMm,
            "pixelAreaPx": target.pixelAreaPx,
            "contourAreaPx": target.contourAreaPx,
            "dpsm": target.dpsm,
            "redPct": target.percentRed,
            "redAreaPx": target.redAreaPx,
            "sizeGrade": target.sizeGrade,
            "minRange": target.minRange,
            "maxRange": target.maxRange,
            "imageWidth": img.shape[0],
            "imageHeight": img.shape[1],
            "boxX1": target.box[0],
            "boxY1": target.box[1],
            "boxX2": target.box[2],
            "boxY2": target.box[3],
            "boxWidth": target.box[0]-target.box[2],
            "boxHeight": target.box[1] - target.box[3],
            "centerX": target.center[0],
            "centerY": target.center[1],
            "redPctThreshold": config.surf_red_percent/100.0,
            "annotation":target.annotation
        }
        try:
            requests.post(config.elasticsearch,json=saveTarget)
        except:
            e = sys.exc_info()[0]
            print(e)



