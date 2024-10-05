import cv2
import mediapipe as mp
import pyautogui

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

mao_fechada = False

def calcular_distancia(ponto1, ponto2):
    return ((ponto1.x - ponto2.x) ** 2 + (ponto1.y - ponto2.y) ** 2) ** 0.5

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    result = hands.process(img_rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)


            x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
            y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y


            screen_width, screen_height = pyautogui.size()
            mouse_x = int(x * screen_width)
            mouse_y = int(y * screen_height)


            pyautogui.moveTo(mouse_x, mouse_y)


            polegar = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            indicador = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            medio = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

            distancia_thumb_indicador = calcular_distancia(polegar, indicador)
            distancia_indicador_medio = calcular_distancia(indicador, medio)

            if distancia_thumb_indicador < 0.05 and distancia_indicador_medio < 0.05:
                if not mao_fechada:
                    pyautogui.mouseDown()
                    mao_fechada = True
            else:
                if mao_fechada:
                    pyautogui.mouseUp()
                    mao_fechada = False

    cv2.imshow("Hand Tracking", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
