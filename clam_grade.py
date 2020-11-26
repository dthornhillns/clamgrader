import cv2 as cv
import numpy as np
import PIL



class ClamTarget:
    id = 0
    center = (0,0)
    box = [0,0,0,0]
    classification = 0
    pixelAreaPx = 0
    contourAreaPx = 0
    pixelAreaMm = 0.0
    contourAreaMm = 0.0
    isOfInterest = False
    isOfMeasurement = False
    percentRed = 0.0
    redAreaPx = 0
    sizeGrade = "unknown"
    minRange = 0.0
    maxRange = 10000.0
    annotation = "auto"
    dpsm = 0.0

def preprocess(origImage, config):

    roi=config.regionOfInterest
    roip=((int)(roi[0] * origImage.shape[1]), (int)(roi[1] * origImage.shape[0]), (int)(roi[2] * origImage.shape[1]), (int)(roi[3] * origImage.shape[0]))
    blkImage = np.zeros(shape=origImage.shape, dtype=np.uint8)
    safeImage= origImage[roip[1]:roip[3], roip[0]:roip[2]]
    blkImage[roip[1]:roip[3],roip[0]:roip[2]]=safeImage
    hueImage = cv.cvtColor(blkImage, cv.COLOR_BGR2HSV)
    enhancedBw = cv.inRange(hueImage, (config.hue_L, config.saturation_L, config.value_L),
                            (config.hue_H, config.saturation_H, config.value_H))

    _, enhancedThreshold = cv.threshold(enhancedBw, config.threshold_L, config.threshold_H,
                                        cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    enhancedBlur = cv.GaussianBlur(enhancedThreshold, (config.blur, config.blur), 0)

    if (config.surf_hue_L < 0):
        surfBw1 = cv.inRange(origImage, (0, config.surf_saturation_L, config.surf_value_L),
                             (config.surf_hue_H, config.surf_saturation_H, config.surf_value_H))
        surfBw2 = cv.inRange(origImage, (180 + config.surf_hue_L, config.surf_saturation_L, config.surf_value_L),
                             (180, config.surf_saturation_H, config.surf_value_H))
        surfBw = surfBw1 | surfBw2

    else:
        surfBw = cv.inRange(origImage, (config.surf_hue_L, config.surf_saturation_L, config.surf_value_L),
                            (config.surf_hue_H, config.surf_saturation_H, config.surf_value_H))

    return (origImage, blkImage, hueImage, enhancedBw, enhancedThreshold,enhancedBlur,surfBw)

def grade(isOfInterest, isOfMeasurement, boxCenter, srcImg, imgSteps, box, contours,contourIndex, dpsm, config):
    im_width = srcImg.shape[1]
    im_height = srcImg.shape[0]
    tile_x1 = max(int(box[0])-2,0)
    tile_y1 = max(int(box[1])-2,0)
    tile_x2 = min(int(box[2]+box[0])+2,im_width)
    tile_y2 = min(int(box[3]+box[1])+2,im_height)
    blkImage = np.zeros(shape=(tile_y2-tile_y1,tile_x2-tile_x1), dtype=np.uint8)
    cv.drawContours(blkImage,contours,contourIndex,color=(255),thickness=-1,offset=(-tile_x1,-tile_y1))
    pixelCount = np.sum(blkImage == 255).item()
    contourArea = cv.contourArea(contours[contourIndex])
    clamTarget = ClamTarget()
    redImage = imgSteps[6][tile_y1:tile_y2, tile_x1:tile_x2].copy()
    redImageMasked = cv.bitwise_and(redImage,blkImage)
    redCount = cv.countNonZero(redImageMasked)
    percentRed = redCount/pixelCount

    if percentRed > (config.surf_red_percent / 100.0):
        category = 2.0
    else:
        category = 1.0

    contourAreaMm = float(contourArea) / float(dpsm)
    pixelAreaMm = float(pixelCount) / float(dpsm)

    clamTarget.classification=int(category)
    clamTarget.center=boxCenter
    clamTarget.contourAreaPx=contourArea
    clamTarget.pixelAreaPx=pixelCount
    clamTarget.contourAreaMm=contourAreaMm
    clamTarget.pixelAreaMm=pixelAreaMm
    clamTarget.isOfInterest=isOfInterest
    clamTarget.isOfMeasurement=isOfMeasurement
    clamTarget.box=box
    clamTarget.percentRed=percentRed
    clamTarget.redAreaPx=redCount
    clamTarget.dpsm=dpsm
    if clamTarget.classification==2.0:
        maxRange=1000000.0
        for size in config.surfSizes:
            if size.min<clamTarget.pixelAreaMm:
                clamTarget.minRange=size.min
                clamTarget.maxRange=maxRange
                clamTarget.sizeGrade=size.name
                break
            else:
                maxRange=size.min

    return clamTarget






