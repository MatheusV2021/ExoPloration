import cv2
import mediapipe as mp
import pyautogui

# Configuração do Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

dedao_fechado = False  # Variável para rastrear o estado do polegar

# Função para calcular a distância entre dois pontos
def calcular_distancia(ponto1, ponto2):
    return ((ponto1.x - ponto2.x) ** 2 + (ponto1.y - ponto2.y) ** 2) ** 0.5

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # Espelhar a imagem horizontalmente
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    result = hands.process(img_rgb)

    if result.multi_hand_landmarks and result.multi_handedness:
        for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Identificar se a mão é a direita ou a esquerda
            hand_label = result.multi_handedness[idx].classification[0].label

            if hand_label == 'Right':  # Apenas a mão direita controla o mouse
                # Obter as coordenadas do polegar e da base do dedo indicador
                polegar = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                base_indicador = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]

                # Calcular a distância entre o polegar e a base do dedo indicador
                distancia_thumb_indicador = calcular_distancia(polegar, base_indicador)

                # Condição para detectar quando o polegar se aproxima da base do indicador
                if distancia_thumb_indicador < 0.05:  # Ajuste o valor conforme necessário
                    if not dedao_fechado:
                        pyautogui.mouseDown()  # Clique do mouse quando o polegar se aproxima
                        dedao_fechado = True
                else:
                    # Solta o clique quando o polegar não estiver próximo da base do indicador
                    if dedao_fechado:
                        pyautogui.mouseUp()
                        dedao_fechado = False

                # Mover o mouse baseado na posição do indicador
                x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y

                screen_width, screen_height = pyautogui.size()
                mouse_x = int(x * screen_width)
                mouse_y = int(y * screen_height)

                pyautogui.moveTo(mouse_x, mouse_y)

            else:
                # Mão esquerda é detectada, mas não controla o mouse
                pass

    cv2.imshow("Hand Tracking", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
