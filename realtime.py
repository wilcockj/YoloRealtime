import cv2
import numpy as np
from time import time
from mss import mss
net = cv2.dnn.readNet('models/yolov3.weights','models/yolov3.cfg')
classes = []
loop_time = time()
with open("models/coco.names", "r") as f:
    classes = f.read().splitlines()

#cap = cv2.VideoCapture(0)
#bounding_box = {'top': 165, 'left': 0, 'width': 1366, 'height': 766}
bounding_box = {'top': 0, 'left': 1366, 'width': 1920, 'height': 1080}
font = cv2.FONT_HERSHEY_PLAIN
colors = np.random.uniform(0, 255, size=(100, 3))

while True:
    cap = np.array(mss().grab(bounding_box))
    cap = np.flip(cap[:, :, :3], 2)
    cap = cv2.cvtColor(cap,cv2.COLOR_BGR2RGB)

    img = cap
    #_, img = cap.read()
    height, width, _ = img.shape

    blob = cv2.dnn.blobFromImage(img, 1/255, (416, 416), (0,0,0), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_names)

    boxes = []
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.2:
                center_x = int(detection[0]*width)
                center_y = int(detection[1]*height)
                w = int(detection[2]*width)
                h = int(detection[3]*height)

                x = int(center_x - w/2)
                y = int(center_y - h/2)

                boxes.append([x, y, w, h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.4)

    if len(indexes)>0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i],2))
            color = colors[i]
            cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
            cv2.putText(img, label + " " + confidence, (x, y+20), font, 2, (255,255,255), 2)
    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    cv2.imshow('Image', img)
    key = cv2.waitKey(1)
    if key==27:
        break

    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()
cap.release()
cv2.destroyAllWindows()
