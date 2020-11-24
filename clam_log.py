import requests
import datetime

def write_clam(config, target, img):
    if(config.writeToElastic):
        saveTarget = {
            "@timestamp": datetime.datetime.now().isoformat(),
            "species": "surf" if target.classification == 2.0 else "cockle",
            "areaMm": target.areaSquareMm,
            "areaPx": target.areaPixel,
            "redPct": target.percentRed,
            "sizeGrade": target.sizeGrade,
            "minRange": target.minRange,
            "maxRange": target.maxRange,
            "imageWidth": img.shape[0],
            "imageHeight": img.shape[1],
            "boxX1": target.box[0],
            "boxY1": target.box[1],
            "boxX2": target.box[2],
            "boxY2": target.box[3],
            "centerX": target.center[0],
            "centerY": target.center[1],
            "redPctThreshold": config.surf_red_percent/100.0,
            "annotation":target.annotation
        }
        requests.post(config.elasticsearch,json=saveTarget)



