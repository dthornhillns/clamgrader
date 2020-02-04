import cv2 as cv
import PIL


class ImageAdjustment:
    contrast=0
    brightness=0
    minThreshold=30
    maxThreshold=60
    showEnhanced="original"
    channel=2
    blur=5
    hue_L=-16
    saturation_L=-7
    value_L=2
    hue_H=185
    saturation_H=165
    value_H=245
    withContours=True
    boxThickness=1
    fontScale=1
    surf_hue_L = 5
    surf_saturation_L = 5
    surf_value_L = 69
    surf_hue_H = 80
    surf_saturation_H = 255
    surf_value_H = 255


def grade(isOfInterest,isOfMeasurement, boxCenter, srcImg, destImg, box, category, score, dpsm, imgAdjust):
    im_width = srcImg.shape[1]
    im_height = srcImg.shape[0]
    tile_x1 = max(int(box[1]*im_width)-2,0)
    tile_y1 = max(int(box[0]*im_height)-2,0)
    tile_x2 = min(int(box[3]*im_width)+2,im_width)
    tile_y2 = min(int(box[2]*im_height)+2,im_height)

    objImg = srcImg[tile_y1:tile_y2, tile_x1:tile_x2].copy()
    imgArea= objImg.shape[0] * objImg.shape[1]
    max_acceptable_area=0.75*imgArea

    convert=objImg

    hueImage=cv.cvtColor(convert,cv.COLOR_BGR2HSV)
    enhancedBw=cv.inRange(hueImage, (imgAdjust.hue_L, imgAdjust.saturation_L, imgAdjust.value_L),
                   (imgAdjust.hue_H, imgAdjust.saturation_H, imgAdjust.value_H))



    _, enhancedThreshold = cv.threshold(enhancedBw, imgAdjust.minThreshold, imgAdjust.maxThreshold, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    enhancedBlur=cv.GaussianBlur(enhancedThreshold, (imgAdjust.blur, imgAdjust.blur), 0)

    cnt, _ = cv.findContours(enhancedBlur,cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

    max_c=-1
    max_area=0
    for i in range(len(cnt)):
        area = cv.contourArea(cnt[i])
        if(area>max_area and area<=max_acceptable_area):
            max_area=area
            max_c=i
    displayImg=objImg
    if imgAdjust.showEnhanced=="threshold":
        displayImg= cv.cvtColor(enhancedThreshold, cv.COLOR_GRAY2RGB)
    elif imgAdjust.showEnhanced=="bw":
        displayImg = cv.cvtColor(enhancedBw, cv.COLOR_GRAY2RGB)
    elif imgAdjust.showEnhanced=="hue":
        displayImg = cv.cvtColor(hueImage, cv.COLOR_GRAY2RGB)
    elif imgAdjust.showEnhanced=="blur":
        displayImg = cv.cvtColor(enhancedBlur, cv.COLOR_GRAY2RGB)

    surfRanges=0
    if(max_c>-1):
        M = cv.moments(cnt[max_c])
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        percentRed=0
        if category==2.0 and score<0.99999:
            if(imgAdjust.surf_hue_L<0):
                surfBw1 = cv.inRange(objImg, (0, imgAdjust.surf_saturation_L, imgAdjust.surf_value_L),
                                    (imgAdjust.surf_hue_H, imgAdjust.surf_saturation_H, imgAdjust.surf_value_H))
                surfBw2 = cv.inRange(objImg, (180+imgAdjust.surf_hue_L, imgAdjust.surf_saturation_L, imgAdjust.surf_value_L),
                                     (180, imgAdjust.surf_saturation_H, imgAdjust.surf_value_H))
                surfBw=surfBw1|surfBw2
                surfRanges=2
                #print("(%d) (%d %d %d) (%d %d %d) | (%d %d %d) (%d %d %d)" % (
                #surfRanges, 0, imgAdjust.surf_saturation_L, imgAdjust.surf_value_L,
                #imgAdjust.surf_hue_H, imgAdjust.surf_saturation_H, imgAdjust.surf_value_H,
                #180+imgAdjust.surf_hue_L, imgAdjust.surf_saturation_L, imgAdjust.surf_value_L,
                #180, imgAdjust.surf_saturation_H, imgAdjust.surf_value_H))

            else:
                surfBw = cv.inRange(objImg, (imgAdjust.surf_saturation_L, imgAdjust.surf_saturation_L, imgAdjust.surf_value_L),
                                     (imgAdjust.surf_hue_H, imgAdjust.surf_saturation_H, imgAdjust.surf_value_H))
                surfRanges = 1
                #print("(%d) (%d %d %d) (%d %d %d)" % (surfRanges, imgAdjust.surf_saturation_L, imgAdjust.surf_saturation_L, imgAdjust.surf_value_L,
                #                                      imgAdjust.surf_hue_H, imgAdjust.surf_saturation_H, imgAdjust.surf_value_H))



            # surfBlur = cv.GaussianBlur(surfThreshold, (imgAdjust.blur, imgAdjust.blur), 0)
            # surfCnts, _ = cv.findContours(surfBlur, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
            redCount = cv.countNonZero(surfBw)
            boxPixels=objImg.shape[0]*objImg.shape[1]
            percentRed=redCount/boxPixels
            #displayImg = cv.cvtColor(surfBw, cv.COLOR_GRAY2RGB)

            if(percentRed>0.10):
                category=2.0
            else:
                category=1.0


        boxColor = (32,32,32) if not isOfInterest else (255, 255, 0) if category == 2.0 else (0, 255, 255)

        obj_area=float(max_area) / float(dpsm)
        areaStr="A: %.2f R: %.2f" % (obj_area, percentRed)
        areaLabel_LL=(10,int(displayImg.shape[0]-10))
        displayImg = cv.putText(displayImg, areaStr,areaLabel_LL, cv.FONT_HERSHEY_PLAIN, fontScale=imgAdjust.fontScale, color=(255,255,0), thickness=2)

        if imgAdjust.withContours==True and isOfMeasurement:
            displayImg = cv.drawContours(displayImg, cnt, max_c, (255, 0, 0), imgAdjust.boxThickness)
        #copy enhanced over original
        destImg[tile_y1:tile_y2, tile_x1:tile_x2]=displayImg
        #draw bounding box on original
        cv.rectangle(destImg,(tile_x1,tile_y1),(tile_x2,tile_y2),boxColor,imgAdjust.boxThickness)
        #draw countour center target on original
        cv.circle(destImg,(tile_x1+cY, tile_y1+cY),5,(255,0,255),cv.FILLED)

        center=(int(boxCenter[1] * im_width),int(boxCenter[0]*im_height))
        cv.circle(destImg,center,3,boxColor,cv.FILLED)






