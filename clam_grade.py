import cv2 as cv
import numpy as np
import PIL



class ClamTarget:
    id=0
    center=(0,0)
    box=[0,0,0,0]
    classification=0
    areaPixel=0
    areaSquareMm=0.0
    isOfInterest=False
    isOfMeasurement=False
    percentRed=0.0,
    sizeGrade="unknown"
    minRange=0.0,
    maxRange=10000.0

def preprocess(origImage, config):

    roi=config.regionOfInterest
    roip=((int)(roi[0] * origImage.shape[1]), (int)(roi[1] * origImage.shape[0]), (int)(roi[2] * origImage.shape[1]), (int)(roi[3] * origImage.shape[0]))
    blkImage = np.zeros(shape=origImage.shape, dtype=np.uint8)
    safeImage= origImage[roip[1]:roip[3], roip[0]:roip[2]]
    blkImage[roip[1]:roip[3],roip[0]:roip[2]]=safeImage
    hueImage = cv.cvtColor(blkImage, cv.COLOR_BGR2HSV)
    enhancedBw = cv.inRange(hueImage, (config.hue_L, config.saturation_L, config.value_L),
                            (config.hue_H, config.saturation_H, config.value_H))

    _, enhancedThreshold = cv.threshold(enhancedBw, config.minThreshold, config.maxThreshold,
                                        cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    enhancedBlur = cv.GaussianBlur(enhancedThreshold, (config.blur, config.blur), 0)

    return (origImage, blkImage, hueImage, enhancedBw, enhancedThreshold,enhancedBlur,safeImage)

def grade(isOfInterest, isOfMeasurement, boxCenter, srcImg, destImg, box, dpsm, config):
    im_width = srcImg.shape[1]
    im_height = srcImg.shape[0]
    tile_x1 = max(int(box[0])-2,0)
    tile_y1 = max(int(box[1])-2,0)
    tile_x2 = min(int(box[2]+box[0])+2,im_width)
    tile_y2 = min(int(box[3]+box[1])+2,im_height)
    safe_w=(config.regionOfInterest[0]-config.regionOfInterest[2])*im_width
    safe_h=(config.regionOfInterest[1]-config.regionOfInterest[3])*im_height
    safeArea=(int)(safe_w*safe_h)
    objImg = srcImg[tile_y1:tile_y2, tile_x1:tile_x2].copy()
    objImageArea= objImg.shape[0] * objImg.shape[1]
    max_acceptable_area=0.75*objImageArea
    imgSteps = preprocess(objImg, config)

    cnt, _ = cv.findContours(imgSteps[3],cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

    max_c=-1
    max_area=0

    if(safeArea*0.75>objImageArea):
        for i in range(len(cnt)):
            area = cv.contourArea(cnt[i])
            if(area>max_area and area<=max_acceptable_area):
                max_area=area
                max_c=i
    displayImg=objImg
    if config.showEnhanced== "threshold":
        displayImg= cv.cvtColor(imgSteps[0], cv.COLOR_GRAY2RGB)
    elif config.showEnhanced== "bw":
        displayImg = cv.cvtColor(imgSteps[1], cv.COLOR_GRAY2RGB)
    elif config.showEnhanced== "hue":
        displayImg = cv.cvtColor(imgSteps[2], cv.COLOR_GRAY2RGB)
    elif config.showEnhanced== "blur":
        displayImg = cv.cvtColor(imgSteps[3], cv.COLOR_GRAY2RGB)

    if(max_c>-1):
        clamTarget=ClamTarget()
        M = cv.moments(cnt[max_c])
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        percentRed=0
        if(config.surf_hue_L<0):
            surfBw1 = cv.inRange(objImg, (0, config.surf_saturation_L, config.surf_value_L),
                                 (config.surf_hue_H, config.surf_saturation_H, config.surf_value_H))
            surfBw2 = cv.inRange(objImg, (180 + config.surf_hue_L, config.surf_saturation_L, config.surf_value_L),
                                 (180, config.surf_saturation_H, config.surf_value_H))
            surfBw=surfBw1|surfBw2

        else:
            surfBw = cv.inRange(objImg, (config.surf_hue_L, config.surf_saturation_L, config.surf_value_L),
                                (config.surf_hue_H, config.surf_saturation_H, config.surf_value_H))




            redCount = cv.countNonZero(surfBw)
            boxPixels=objImg.shape[0]*objImg.shape[1]
            percentRed=redCount/boxPixels
            if config.showEnhanced == "isSurf":
                displayImg = cv.cvtColor(surfBw, cv.COLOR_GRAY2RGB)

            if(percentRed>config.surf_red_percent):
                category=2.0
            else:
                category=1.0

        boxColor = (32,32,32) if not isOfInterest else (255, 255, 0) if category == 2.0 else (0, 255, 255)

        obj_area=float(max_area) / float(dpsm)

        cv.circle(destImg,boxCenter,3,boxColor,cv.FILLED)

        clamTarget.classification=int(category)
        clamTarget.center=boxCenter
        clamTarget.areaSquareMm=obj_area
        clamTarget.areaPixel=max_area
        clamTarget.isOfInterest=isOfInterest
        clamTarget.isOfMeasurement=isOfMeasurement
        clamTarget.box=box
        clamTarget.percentRed=percentRed
        if clamTarget.classification==2.0:
            maxRange=1000000.0
            for size in config.surfSizes:
                if size.min<clamTarget.areaSquareMm:
                    clamTarget.minRange=size.min
                    clamTarget.maxRange=maxRange
                    clamTarget.sizeGrade=size.name
                    break
                else:
                    maxRange=size.min

        return clamTarget






