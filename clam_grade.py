import cv2 as cv
from PIL import ImageFont


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

try:
    font = ImageFont.truetype('arial.ttf', 24)
except IOError:
    font = ImageFont.load_default()

def grade(srcImg, box, category, score,  dpsm, imgAdjust):
    im_width = srcImg.shape[1]
    im_height = srcImg.shape[0]
    box_x1=int(box[0]*im_width)
    box_y1=int(box[1]*im_height)
    box_x2 = int(box[2] * im_width)
    box_y2 = int(box[3] * im_height)
    tile_x1 = int(box[1]*im_width)
    tile_y1 = int(box[0]*im_height)
    tile_x2 = int(box[3]*im_width)
    tile_y2 = int(box[2]*im_height)
    #objImg=srcImg[box_y1i:box_y2i, box_x1i:box_x2i]
    objImg = srcImg[tile_y1:tile_y2, tile_x1:tile_x2]
    imgArea= objImg.shape[0] * objImg.shape[1]
    max_acceptable_area=0.75*imgArea

    convert=objImg
    #if imgAdjust.channel>-1:
    #    channels = cv.split(convert)
    #    hue=channels[imgAdjust.channel]
    #    hue=cv.merge((hue,hue,hue))
    #else:
    #    hue=convert

    hue=cv.cvtColor(convert,cv.COLOR_BGR2HSV)
    enhancedBw=cv.inRange(hue, (imgAdjust.hue_L, imgAdjust.saturation_L, imgAdjust.value_L),
                   (imgAdjust.hue_H, imgAdjust.saturation_H, imgAdjust.value_H))

    #plt.imshow(hue)
    #plt.show()

    #enhanced = cv.convertScaleAbs(enhanced, alpha=imgAdjust.contrast, beta= imgAdjust.brightness)
    #enhancedThreshold = cv.Canny(enhancedBw,threshold1=imgAdjust.minThreshold, threshold2=imgAdjust.maxThreshold)
    _, enhancedThreshold = cv.threshold(enhancedBw, imgAdjust.minThreshold, imgAdjust.maxThreshold, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    #plt.imshow(bw)
    #plt.show()

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


    obj_area=float(max_area) / float(dpsm)
    areaStr="Area (mm): %.2f" % (obj_area)
    areaLabel_LL=(10,int(displayImg.shape[0]-10))
    #cv.rectangle(displayImg, areaLabel_UL, areaLabel_LR, (0,255,0), -1)
    displayImg = cv.putText(displayImg, areaStr,areaLabel_LL, cv.FONT_HERSHEY_PLAIN, fontScale=2, color=(255,255,0), thickness=2)

    if imgAdjust.withContours==True:
        displayImg = cv.drawContours(displayImg, cnt, max_c, (255, 0, 0), 2)
    srcImg[tile_y1:tile_y2, tile_x1:tile_x2]=displayImg

    cv.rectangle(srcImg,(tile_x1,tile_y1),(tile_x2,tile_y2),(0,255,255),2)
    #cv.rectangle(srcImg, (0, 0), (100, 200), (0, 0, 255), 1)
    print("%d, %d, %d | %d, %d, %d | %d, %d, %d, %d, %d" % (imgAdjust.hue_L, imgAdjust.saturation_L, imgAdjust.value_L,
                                               imgAdjust.hue_H, imgAdjust.saturation_H, imgAdjust.value_H,
                                               imgAdjust.brightness, imgAdjust.contrast,
                                               imgAdjust.minThreshold, imgAdjust.maxThreshold,
                                               imgAdjust.blur))




