import requests
import datetime

def write_clam(config, target):
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
    requests.post("http://192.168.2.92:9200/clamsize/_doc",json=saveTarget)



