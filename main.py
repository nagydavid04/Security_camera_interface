
import cv2
import tkinter as tk
import numpy as np
from PIL import ImageTk, Image
import datetime


class Cam:
    def __init__(self, source, num):
        self.source = cv2.VideoCapture(source)
        self.number = num

    def get_frame(self):
        ret, frame = self.source.read()

        if ret:
            frame = place_frame(cv2.cvtColor(cv2.resize(frame, (universal_width, universal_height)),
                                             cv2.cv2.COLOR_RGB2BGR))
        else:
            frame = no_signal_image.copy()

        frame = cv2.putText(frame, f"Cam{self.number}", (5, 43),
                            cv2.FONT_ITALIC, 1.5,
                            (255, 255, 255), 3, cv2.LINE_AA)

        frame = cv2.putText(frame, str(datetime.datetime.now()).split(".")[0],
                            (620, 740),
                            cv2.FONT_ITALIC, 1, (255, 255, 255), 3, cv2.LINE_AA)

        return frame


def update_screen():
    if current_cam != -1:
        # show current cam
        screen = cv2.resize(cams[current_cam].get_frame(), (cam_screen_width, cam_screen_height))

    else:
        # show all cam
        screen = np.zeros((cam_screen_height, cam_screen_width, 3), dtype=np.uint8)

        frames = [cam.get_frame() for cam in cams]

        if len(frames) % 2 != 0 and len(frames) != 1:
            frames.append(no_camera_image)

        len_frames = len(frames)

        if len_frames == 1:
            screen = cv2.resize(frames[0], (cam_screen_width, cam_screen_height))

        elif len_frames == 2:
            frame_width, frame_height = cam_screen_width // 2, cam_screen_height
            frames = [cv2.resize(frame, (frame_width, frame_height)) for frame in frames]
            screen[0:frame_height, 0:frame_width] = frames[0]
            screen[0:frame_height, frame_width:cam_screen_width] = frames[1]

        else:
            frame_width, frame_height = cam_screen_width // (len_frames // 2), cam_screen_height // 2
            frames = [cv2.resize(frame, (frame_width, frame_height)) for frame in frames]
            index = 0
            for x in range(0, cam_screen_width, frame_width):
                for y in range(0, cam_screen_height, frame_height):
                    screen[y:y + frame_height, x:x + frame_width] = frames[index]
                    index += 1

    screen = ImageTk.PhotoImage(Image.fromarray(screen))

    label.configure(image=screen, borderwidth=0)
    label.image = screen
    win.after(1, update_screen)


def left():
    global current_cam
    if current_cam > -1:
        current_cam -= 1
    else:
        current_cam = len(cams)-1


def right():
    global current_cam
    if current_cam < len(cams)-1:
        current_cam += 1
    else:
        current_cam = -1


def place_frame(image):
    image[0:universal_height, 0:1] = vertical_line
    image[0:universal_height, universal_width-1:universal_width] = vertical_line
    image[0:1, 0:universal_width] = horizontal_line
    image[universal_height-1:universal_height, 0:universal_width] = horizontal_line
    return image


current_cam = -1    # show all cam, if value >= 0 --> show specific cam

no_signal_image = np.array(cv2.imread("no_signal_image.png"))
no_camera_image = np.array(cv2.imread("no_camera_image.png"))

# defining the tkinter window
win = tk.Tk()
win.attributes("-fullscreen", True)
win.resizable(False, False)
win.title("Camera system")
win.configure(background="gray")

display_width, display_height = win.winfo_screenwidth(), win.winfo_screenheight()
cam_screen_width, cam_screen_height = display_width, int(display_height * 5/6)
universal_width, universal_height = 1000, 750

vertical_line = [[(0, 0, 0)] for _ in range(universal_height)]
horizontal_line = [[(0, 0, 0) for _ in range(universal_width)]]

no_signal_image = place_frame(cv2.resize(no_signal_image, (universal_width, universal_height)))
no_camera_image = place_frame(cv2.resize(no_camera_image, (universal_width, universal_height)))

cams = [Cam(f"videos/video{num}.mp4", num) for num in range(1, 6)]      # defining the sources

label = tk.Label(win)
label.pack()

exit_button = tk.Button(win, text="Exit", command=win.destroy, font='Helvetica 30 bold', bg='gray')
exit_button.place(x=display_width-display_width//8, y=display_height-display_height//8)

left_button = tk.Button(win, text="<---", command=left, font='Helvetica 30 bold', bg='gray')
left_button.place(x=display_width//2 - display_width//7, y=display_height-display_height//8, width=100)

right_button = tk.Button(win, text="--->", command=right, font='Helvetica 30 bold', bg='gray')
right_button.place(x=display_width//2 + display_width//7 - 100, y=display_height-display_height//8, width=100)

update_screen()

win.mainloop()
