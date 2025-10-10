import sys
import os
import time

if sys.platform.startswith('win'):
    import msvcrt
elif sys.platform.startswith('linux'):
    import tty
    import termios
    import select


class KeyboardHandling:
    @staticmethod
    def windows():
        if not msvcrt.kbhit():
            return -1  # no key pressed

        key = -1
        first_char = msvcrt.getch()

        if first_char == b'\xe0':  # special key (arrow keys)
            second_char = msvcrt.getch()
            if second_char == b'H':
                key = 0  # up
            elif second_char == b'P':
                key = 2  # down
            elif second_char == b'M':
                key = 3  # right
            elif second_char == b'K':
                key = 1  # left

        elif first_char in [b'w', b'8']:
            key = 0
        elif first_char in [b's', b'2']:
            key = 2
        elif first_char in [b'd', b'6']:
            key = 3
        elif first_char in [b'a', b'4']:
            key = 1
        elif first_char == b' ':
            key = 4
        elif first_char == b'\x03':  # Ctrl+C
            key = 5

        return key

    @staticmethod
    def linux():
        key = -1
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            if select.select([sys.stdin], [], [], 0.0)[0]:
                ch1 = sys.stdin.read(1)
                if ch1 == '\x1b':
                    if select.select([sys.stdin], [], [], 0.0)[0]:
                        ch2 = sys.stdin.read(1)
                        if ch2 == '[':
                            if select.select([sys.stdin], [], [], 0.0)[0]:
                                ch3 = sys.stdin.read(1)
                                if ch3 == 'A':
                                    key = 0  # up
                                elif ch3 == 'B':
                                    key = 2  # down
                                elif ch3 == 'C':
                                    key = 3  # right
                                elif ch3 == 'D':
                                    key = 1  # left
                elif ch1 == 'w':
                    key = 0
                elif ch1 == 's':
                    key = 2
                elif ch1 == 'd':
                    key = 3
                elif ch1 == 'a':
                    key = 1
                elif ch1 == ' ':
                    key = 4
                elif ch1 == '\x03':  # Ctrl+C
                    key = 5
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return key


def handle_keyboard():
    if sys.platform.startswith('win'):
        return KeyboardHandling.windows()
    elif sys.platform.startswith('linux'):
        return KeyboardHandling.linux()
    else:
        raise RuntimeError("This game is made for Windows and Linux only.")



# DEV UTILITIES 
# # FOR LOGING
def custom_print (*args):
    print(*args,sep="     ",file=open("output.txt","a",encoding="utf-8"))