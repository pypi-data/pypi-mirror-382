import curses
import sys

class StdOutWrapper:
    text = ''
    def write(self,txt):
        self.text += txt
        self.text = '\n'.join(self.text.split('\n')[-30:])
    def get_text(self,beg,end):
        return '\n'.join(self.text.split('\n')[beg:end])

class Curses_Wrapper:
    def __init__(self, scr, displays_shape=(1,1), command_callback=None):
        curses.noecho()
        curses.cbreak()
        scr.keypad(True)
        self.scr = scr

        self.scr.timeout(1)

        self.displays = []
        self.boxes = []
        self.displays_shape = displays_shape
        self.written_text = ''
        self.command_callback = command_callback

        self.display_width = (curses.COLS-1)//(displays_shape[0])
        self.display_height = (curses.LINES-1)//(displays_shape[1])

        for x in range(self.displays_shape[0]):
            x_coord = x * self.display_width
            d = []
            for y in range(self.displays_shape[1]):
                y_coord = y * self.display_height
                self.boxes += [self.scr.subwin(self.display_height, self.display_width, y_coord, x_coord)]
                d += [self.scr.subwin(self.display_height-2, self.display_width-2, y_coord+1, x_coord+1)]
            self.displays += [d]

    def __del__(self):
        curses.nocbreak()
        self.scr.keypad(False)
        curses.echo()
        curses.endwin()

    def refresh(self):
        for i in self.boxes:
            i.box('|', '-')
            i.refresh()
        for i in [ item for sublist in self.displays for item in sublist ]:
            i.refresh()

    def clear(self):
        for i in self.boxes:
            i.erase()
        for i in [ item for sublist in self.displays for item in sublist ]:
            i.erase()

    def print(self, text, window_coords):
        '''Adds text to a window at (window_coords) (2-tuple)'''
        try:
            self.displays[window_coords[0]][window_coords[1]].addstr(text)
        except curses.error:
            pass

    def set_text(self, text, window_coords):
        try:
            self.displays[window_coords[0]][window_coords[1]].erase()
            self.displays[window_coords[0]][window_coords[1]].addstr(text)
        except curses.error:
            pass

    def getkey(self):
        while(True):
            try:
                char = self.scr.getkey()
                if(ord(char) == 8):
                    # delete
                    self.written_text = self.written_text[:-1]
                elif(char == '\n' and command_callback):
                    self.command_callback(self.written_text)
                    self.written_text = ''
                else:
                    self.written_text += char
            except:
                break

    def input(self, window_coords=(0,0)):
        ex=False
        written = ''
        self.scr.nodelay(False)
        while(not(ex)):
            try:
                char = self.scr.getkey()
                if(char == 'KEY_BACKSPACE'):
                    # delete
                    if(self.written_text != ''):
                        self.written_text = self.written_text[:-1]
                        cursor_pos = curses.getsyx()
                        self.displays[window_coords[0]][window_coords[1]].delch(cursor_pos[0]-1, cursor_pos[1]-2)
                        self.refresh()
                elif(char == '\n'):
                    written = self.written_text
                    ex=True
                    self.written_text = ''
                    self.displays[window_coords[0]][window_coords[1]].echochar(char)
                else:
                    self.displays[window_coords[0]][window_coords[1]].echochar(char)
                    self.written_text += char
            except Exception as e:
                break
        return written

global wrapper
global daviscurses_args

daviscurses_args = { 'autoflush': True }

def set_screensize(dims):
    global wrapper
    wrapper = Curses_Wrapper(curses.initscr(), dims)

def print(s, *args, **kwargs):
    global daviscurses_args
    try:
        if('window_coords' in kwargs):
            coords = kwargs['window_coords']
            if(coords[0] < 0 or coords[0] > wrapper.displays_shape[0]-1):
                coords[0] = 0
            if(coords[1] < 0 or coords[1] > wrapper.displays_shape[1]-1):
                coords[1] = 0
        else:
            coords = (0,0)
        flush=daviscurses_args['autoflush']
        if('flush' in kwargs):
            flush=False if (not(kwargs['flush'])) else True
        wrapper.print(str(s), coords)
        for si in args:
            wrapper.print(' ' + str(si), coords)
        wrapper.print('\n', coords)
        if(flush):
            wrapper.refresh()
    except Exception as e:
        with open('curses_errors.txt', 'a') as file:
            file.write(str(e))
            file.close()

def input(*args, **kwargs):
    if(len(args) == 1):
        print(args[0])
    if(len(args) > 1):
        print(args[0], args[1:])
    wcoords = (0,0) if not('window_coords' in kwargs) else kwargs['window_coords']
    return wrapper.input()

set_screensize((1,1))

daviscurses_args = { 'autoflush': True }

def set_autoflush(b):
    global daviscurses_args
    daviscurses_args['autoflush'] = b
