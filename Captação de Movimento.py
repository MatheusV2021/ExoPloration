import cv2
import mediapipe as mp
import pyautogui

# Configuração do Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

dedao_fechado = False  # Variável para rastrear o estado do polegar (mão direita)
scroll_atual = 0  # Variável para rastrear o estado de scroll (mão esquerda)
clique_unico_executado = False  # Variável para evitar múltiplos cliques únicos

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
                # Obter as coordenadas do polegar, dedo indicador e dedo médio
                polegar = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                base_indicador = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                meio_dedo = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

                # Calcular a distância entre o polegar e a base do dedo indicador
                distancia_thumb_indicador = calcular_distancia(polegar, base_indicador)

                # Calcular a distância entre o polegar e o dedo médio (para o clique único)
                distancia_thumb_meio = calcular_distancia(polegar, meio_dedo)

                # Condição para o clique único (quando o polegar e o dedo médio se tocam)
                if distancia_thumb_meio < 0.075 and not clique_unico_executado:
                    pyautogui.click()  # Executa o clique único
                    clique_unico_executado = True  # Marca o clique como executado

                # Quando os dedos se afastarem, reseta o clique único
                if distancia_thumb_meio > 0.1:
                    clique_unico_executado = False  # Permite outro clique único quando os dedos se afastarem

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

            elif hand_label == 'Left':  # A mão esquerda realiza o scroll
                # Obter as coordenadas do polegar e da ponta do dedo indicador
                polegar_esquerdo = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                indicador_esquerdo = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Calcular a distância entre o polegar e o indicador da mão esquerda
                distancia_esquerda = calcular_distancia(polegar_esquerdo, indicador_esquerdo)

                # Lógica de rolagem: quanto menor a distância, maior a rolagem
                if distancia_esquerda < 0.05:
                    if scroll_atual != 1:
                        pyautogui.scroll(-100)  # Scroll up
                        scroll_atual = 1
                elif distancia_esquerda > 0.1:
                    if scroll_atual != -1:
                        pyautogui.scroll(100)  # Scroll down
                        scroll_atual = -1
                else:
                    scroll_atual = 0  # Reset do estado de scroll

    cv2.imshow("Hand Tracking", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
