import sys
import cv2
import numpy as np
from ultralytics import YOLO
import psycopg2

fluxo = str(sys.argv[1]) #entrada | saida | duplo

def connect():
    con = psycopg2.connect(host='database10772.integrator.host',port=5432, database='analitics',
    user='postgres', password='McVde#BklLpB')
    return con        

def contarEntrada():
    try:
        con = connect()
        cur = con.cursor()
        sql = "insert into contador(tipo) values ('E')"
        cur.execute(sql)
        con.commit()
        con.close()
    except ValueError:
        print("Não foi possivel conectar ao servidor", ValueError)

def contarSaida():    
    try:
        con = connect()
        cur = con.cursor()
        sql = "insert into contador(tipo) values ('S')"
        cur.execute(sql)
        con.commit()
        con.close()
    except ValueError:
        print("Não foi possivel conectar ao servidor", ValueError)


#arena
linhax1 = 270
linhay1 = 90
linhax2 = 600
linhay2 = 350

# linhax1 = 10
# linhay1 = 350
# linhax2 = 600
# linhay2 = 350

model = YOLO('yolov8n.pt')
classnames = model.model.names
class_IDS = [0,2, 3, 5, 7]
labels = [classnames[i] for i in class_IDS]
contador_in = 0
contador_out = 0
#cam arena
cap = cv2.VideoCapture('rtsp://aps:aps2024aps@186.208.10.166:554/cam/realmonitor?channel=1&subtype=0')
#cam lidere
# cap = cv2.VideoCapture('rtsp://aps:aps2024aps@186.208.3.38:554/cam/realmonitor?channel=8&subtype=1')

if not cap.isOpened():
    print("Cannot open camera")
    exit()

pontoXCentral = 398;
pontoYCentral = 192;

pontoXEsquerdo = 269;
pontoYEsquerdo = 90;

pontoXDireito = 598;
pontoYDireito = 350;

while True:
    ret, frame = cap.read()
    if (frame is None): continue
    frame = cv2.resize(frame, (800,600))
    results = model.predict(frame, conf = 0.5, classes = class_IDS)
    current_detections = np.empty([0,5])

    # cv2.line(frame,(270,90),(600,350),color=(0, 0, 255), thickness=8) arena
    cv2.line(frame,(linhax1,linhay1),(linhax2,linhay2),color=(0, 0, 255), thickness=8)
    #ponto central
    cv2.circle(frame,(pontoXCentral, pontoYCentral), 5, (0, 222, 255), 2)
    #ponto esquerdo
    cv2.circle(frame,(pontoXEsquerdo, pontoYEsquerdo), 5, (0, 222, 255), 2)    
    #ponto direito
    cv2.circle(frame,(pontoXDireito, pontoYDireito), 5, (0, 222, 255), 2)    
    

    for info in results:
        parameters = info.boxes
        for box in parameters:
            xmin, ymin, xmax, ymax = box.xyxy[0]
            xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
            confidence = box.conf[0]
            category = int(box.cls[0])
            
            # Calculating the center of the bounding-box
            center_x, center_y = int(((xmax+xmin))/2), int((ymax+ ymin)/2)
            
            # drawing center and bounding-box of vehicle in the given frame 
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (255,0,0), 5) # box
            cv2.circle(frame, (center_x,center_y), 5,(255,0,0),-1) # center of box
            
            #Drawing above the bounding-box the name of class recognized.
            cv2.putText(img=frame, text=f"{classnames[category]} ({str(np.round(confidence,2))})",
                        org= (xmin,ymin-10), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(255, 0, 0),thickness=2)            
            
            if (center_y < (linhay1 + 20)) and (center_y > (linhay1 - 20)):
                if (fluxo == 'entrada') and (center_x >= 0) and (center_x <= pontoXDireito): 
                    contarEntrada()
                elif (fluxo == 'saida') and (center_x >= 0) and (center_x >= pontoXEsquerdo): 
                    contarSaida()
                else:
                    if  (center_x >= 0) and (center_x <= pontoXCentral):
                        contarEntrada()
                    else:
                        contarSaida()

    #cv2.imshow('frame', frame)
    #if cv2.waitKey(1) == ord('q') or cv2.waitKey(1) == ord('Q'):
    #    break

cap.release()
cv2.destroyAllWindows()
