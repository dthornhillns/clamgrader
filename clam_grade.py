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


def grade(srcImg,destImg, box, category, score,  dpsm, imgAdjust):
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

    hue=cv.cvtColor(convert,cv.COLOR_BGR2HSV)
    enhancedBw=cv.inRange(hue, (imgAdjust.hue_L, imgAdjust.saturation_L, imgAdjust.value_L),
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
        displayImg = cv.cvtColor(hue, cv.COLOR_GRAY2RGB)
    elif imgAdjust.showEnhanced=="blur":
        displayImg = cv.cvtColor(enhancedBlur, cv.COLOR_GRAY2RGB)

    if(max_c>-1):
        M = cv.moments(cnt[max_c])
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])


        obj_area=float(max_area) / float(dpsm)
        areaStr="A: %.2f" % (obj_area)
        areaLabel_LL=(10,int(displayImg.shape[0]-10))
        displayImg = cv.putText(displayImg, areaStr,areaLabel_LL, cv.FONT_HERSHEY_PLAIN, fontScale=1, color=(255,255,0), thickness=1)

        if imgAdjust.withContours==True:
            displayImg = cv.drawContours(displayImg, cnt, max_c, (255, 0, 0), 1)
        #copy enhanced over original
        destImg[tile_y1:tile_y2, tile_x1:tile_x2]=displayImg
        #draw bounding box on original
        cv.rectangle(destImg,(tile_x1,tile_y1),(tile_x2,tile_y2),(0,255,255),1)
        #draw countour center target on original
        cv.circle(destImg,(tile_x1+cY, tile_y1+cY),5,(255,0,255),cv.FILLED)





