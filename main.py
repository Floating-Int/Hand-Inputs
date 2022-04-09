import win32con
import cv2
import mediapipe as mpipe
import math
import keyboard
import win32api
import time


IP = input("Enter IP: ")
PORT = input("Enter PORT: ")
IP = IP if IP else "192.168.10.125"
PORT = PORT if PORT else 8080
URL = f"https://{IP}:{PORT}/video"

print("Connecting to", URL)
capture = cv2.VideoCapture(URL)
print("Connection established...")
print("[INFO] Press 'q' to quit")

hands = mpipe.solutions.hands.Hands()
THUMB = 4
INDEX = 8
MIDDLE = 12

UP = "w"
LEFT = "a"
DOWN = "s"
RIGHT = "d"


info = {
    UP: False,
    LEFT: False,
    DOWN: False,
    RIGHT: False
}


def _on_up() -> None:
    keyboard.press(UP)
    keyboard.release(DOWN)
    keyboard.release(LEFT)
    keyboard.release(RIGHT)
    ...
    print("UP")
    # for key in info.keys():
    #     if info[key]:
    #         keyboard.release(key)
    # keyboard.press(UP)


def _on_down() -> None:
    keyboard.release(UP)
    keyboard.press(DOWN)
    keyboard.release(LEFT)
    keyboard.release(RIGHT)
    ...
    print("DOWN")
    # for key in info.keys():
    #     if info[key]:
    #         keyboard.release(key)
    # keyboard.press(DOWN)


def _on_left() -> None:
    keyboard.release(UP)
    keyboard.release(DOWN)
    keyboard.press(LEFT)
    keyboard.release(RIGHT)
    ...
    print("LEFT")
    # for key in info.keys():
    #     if info[key]:
    #         keyboard.release(key)
    # keyboard.press(LEFT)


def _on_right() -> None:
    keyboard.release(UP)
    keyboard.release(DOWN)
    keyboard.release(LEFT)
    keyboard.press(RIGHT)
    ...
    print("RIGHT")
    # for key in info.keys():
    #     if info[key]:
    #         keyboard.release(key)
    # keyboard.press(RIGHT)


def _on_all() -> None:
    ...
    print("ALL")
    click()


def _on_none() -> None:
    ...
    print("NONE")
    for key in info.keys():
        info[key] = False
        keyboard.release(key)


def distance(p1x: int, p1y: int, p2x: int, p2y: int) -> float:
    """Returns the distance between point1 and point2

    Args:
        p1x (int): point1.x
        p1y (int): point1.y
        p2x (int): point2.x
        p2y (int): point2.y

    Returns:
        float: distance
    """
    a, b = p2x - p1x, p2y - p1y
    # pytagoras
    c = math.sqrt(a * a + b * b)
    return c


def distance_vec(p1: tuple, p2: tuple) -> float:
    return distance(*p1, *p2)


def rotate_vec(point: tuple, origin: tuple, angle: float) -> tuple:
    """Rotate a point counterclockwise by the given angle (in radians) around an origin

    Args:
        point (tuple): Vector2 point
        origin (tuple): Vector2 origin
        angle (float): radians

    Returns:
        tuple: Vector2
    """
    px, py = point
    ox, oy = origin
    dx, dy = px - ox, py - oy
    x = ox + math.cos(angle) * dx - math.sin(angle) * dy
    y = oy + math.sin(angle) * dx + math.cos(angle) * dy
    return (x, y)


def click() -> None:
    """Simulates a Left Mouse Button click
    """
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def main() -> None:
    while capture.isOpened():
        _, _ = capture.read()  # increase fps
        _, frame = capture.read()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            # for landmark in results.multi_hand_landmarks:
            #     mpipe.solutions.drawing_utils.draw_landmarks(
            #         frame, landmark, mpipe.solutions.hands.HAND_CONNECTIONS)

            hand_landmarks = results.multi_hand_landmarks[0]
            image_height, image_width, _ = frame.shape
            # index finger
            a, b = map(int, (hand_landmarks.landmark[INDEX].x * image_width,
                             hand_landmarks.landmark[INDEX].y * image_height))
            # thumb
            x1, y1 = map(int, (hand_landmarks.landmark[THUMB].x * image_width,
                               hand_landmarks.landmark[THUMB].y * image_height))
            # middle
            x2, y2 = map(int, (hand_landmarks.landmark[MIDDLE].x * image_width,
                               hand_landmarks.landmark[MIDDLE].y * image_height))
            # frame = cv2.line(frame, (x1, y1), (a, b), (0, 0, 255), 5)
            # frame = cv2.line(frame, (x2, y2), (a, b), (0, 0, 255), 5)

            l1 = distance(x1, y1, a, b) < 100
            l2 = distance(x2, y2, a, b) < 150
            origin = ((x2 - x1) // 2 + x1, (y2 - y1) // 2 + y1)
            ox, oy = origin

            # frame = cv2.line(frame, (ox-100, oy-100),
            #                  (ox+100, oy+100), (0, 255, 255), 5)
            # frame = cv2.line(frame, (ox+100, oy-100),
            #                  (ox-100, oy+100), (0, 255, 255), 5)
            # frame = cv2.line(frame, (ox, oy-200),
            #                  (ox, oy+200), (255, 255, 255), 5)
            # frame = cv2.line(frame, (ox+200, oy),
            #                  (ox-200, oy), (255, 255, 255), 5)

            if l1 and l2:
                _on_all()  # all together

            elif l1:  # left or down
                px, py = map(int, rotate_vec(
                    (x1, y1), origin, math.radians(-45)))
                #frame = cv2.circle(frame, (px, py), 5, (0, 255, 0), 5)
                if px < ox:  # left
                    _on_left()
                else:  # down
                    _on_down()

            elif l2:  # right or up
                px, py = map(int, rotate_vec(
                    (x2, y2), origin, math.radians(-45)))
                #frame = cv2.circle(frame, (px, py), 5, (0, 255, 0), 5)
                if px < ox:  # right
                    _on_up()
                else:  # up
                    _on_right()
            else:  # release
                _on_none()

        #cv2.imshow("Livestream", frame)
        # cv2.waitKey(1)

        if keyboard.is_pressed("q"):  # quit
            break
    # on exit
    capture.release()


if __name__ == "__main__":
    main()
