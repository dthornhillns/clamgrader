import requests
import datetime

def write_clam(config, target):
    if(config.writeToElastic):
        saveTarget= {
            "@timestamp": datetime.datetime.now().isoformat(),
            "species": "surf" if target.classification == 2.0 else "cockle",
            "areaMm": target.areaSquareMm,
            "areaPx": target.areaPixel,
            "redPct": target.percentRed,
            "sizeGrade": target.sizeGrade,
            "minRange": target.minRange,
            "maxRange": target.maxRange
        }
        requests.post(config.elasticsearch,json=saveTarget)



