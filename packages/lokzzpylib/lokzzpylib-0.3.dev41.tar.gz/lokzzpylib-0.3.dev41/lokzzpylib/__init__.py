from clint.textui import puts, colored, indent
import threading, colorama, keyboard, random, queue, time, io, re

import atexit, sys
from blessed import Terminal

try: import msvcrt, win32con, win32console
except ImportError: windows = False
else: windows = True

from .misc import *
# misc = [
#   class = [Choice, RepeatedTimer],
#   func = [isdebug, ask_bool, ask_int, wind_getonekey, clearsc, clearinp]
# ]

colorama.init()

## TAG::<AI> (AI generated code)
class FrameBuffer:
    def __init__(self, term: Terminal = Terminal()):
        self.term = term
        self.current_frame = ""  # Current frame being built
        self.last_frame = ""    # Last frame that was displayed
        self.cursor_x = 0       # Track cursor x position
        self.cursor_y = 0       # Track cursor y position
        self._valid = True      # Track if buffer is still valid
        self._setup_cleanup()
        self._clear_initial()
    
    def _validate(self):
        """Check if buffer is still valid"""
        if not self._valid:
            raise RuntimeError("FrameBuffer has been destroyed and cannot be used")
    
    def destroy(self):
        """Cleanup and invalidate the buffer"""
        if self._valid:
            self._cleanup()
            # Unregister from atexit to prevent double cleanup
            atexit.unregister(self._cleanup)
            # Clear references
            self.term = None
            self.current_frame = None
            self.last_frame = None
            self._valid = False
    
    def _setup_cleanup(self):
        """Set up cleanup handlers"""
        atexit.register(self._cleanup)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """Restore terminal state"""
        try:
            # Reset all colors and attributes
            print(self.term.normal + self.term.normal_cursor, end='')
            # Move to bottom and add newline
            print(self.term.move_xy(0, self.term.height-1) + '\n', end='')
            sys.stdout.flush()
        except:
            # If anything fails during cleanup, make a last-ditch effort
            try:
                print('\033[0m\033[?25h\n', end='')
                sys.stdout.flush()
            except:
                pass
    
    def _clear_initial(self):
        """Clear any existing text on screen during initialization"""
        # First push everything up
        print('\n' * self.term.height, end='')
        # Then clear everything
        for y in range(self.term.height):
            print(self.term.move_xy(0, y) + ' ' * self.term.width, end='')
        # Move back to top
        print(self.term.move_xy(0, 0), end='')
        sys.stdout.flush()
    
    def add(self, string):
        """Add string to current frame buffer"""
        self._validate()
        self.current_frame += str(string)
        return self
    
    def write(self, text: str = ''):
        """Support for print(text, file=buffer)"""
        self._validate()
        if isinstance(text, str):
            self.add(text)
        else:
            self.add(str(text))
        return self
    
    # def flush(self):
    #     """Support for print(text, file=buffer), removed because this literally clears the frame before it"""
    #     self.push()
    #     return self
    
    def _move_to(self, x, y):
        """Move cursor to position"""
        self._validate()
        self.cursor_x = x
        self.cursor_y = y
        return self.term.move_xy(x, y)
    
    def push(self):
        """Calculate difference between frames and update display"""
        self._validate()
        if not self.current_frame and not self.last_frame:
            return self
        
        # Split frames into lines
        current_lines = self.current_frame.split('\n')
        last_lines = self.last_frame.split('\n')
        
        # Calculate the maximum number of lines in both frames
        max_lines = max(len(current_lines), len(last_lines))
        
        # Extend both line lists to the same length
        current_lines.extend([''] * (max_lines - len(current_lines)))
        last_lines.extend([''] * (max_lines - len(last_lines)))
        
        # Process each line
        for y, (current, last) in enumerate(zip(current_lines, last_lines)):
            if current != last:
                # Clear the old line
                if last:
                    print(self.term.move_xy(0, y) + ' ' * self.term.width, end='')
                # Write the new line
                if current:
                    print(self.term.move_xy(0, y) + current, end='')
        
        # Clear any remaining lines to the bottom of terminal
        for y in range(max_lines, self.term.height):
            print(self.term.move_xy(0, y) + ' ' * self.term.width, end='')
        
        # Store current frame as last frame
        self.last_frame = self.current_frame
        # Clear current frame
        self.current_frame = ""
        
        # Reset colors after each frame
        print(self.term.normal, end='')
        
        # Move cursor to bottom
        print(self.term.move_xy(0, self.term.height-1), end='')
        
        sys.stdout.flush()
        return self
## TAG::</AI>

class win_buffer():
    def __init__(self):
        if not windows: OSError('Not Windows')
        self.buffer = [win32console.CreateConsoleScreenBuffer(DesiredAccess = win32con.GENERIC_READ | win32con.GENERIC_WRITE, ShareMode=0, SecurityAttributes=None, Flags=1), win32console.CreateConsoleScreenBuffer(DesiredAccess = win32con.GENERIC_READ | win32con.GENERIC_WRITE, ShareMode=0, SecurityAttributes=None, Flags=1)]
        self.writeto = self.buffer[0]

    def push(self):
        self.buffer[1] = self.buffer[0]
        self.buffer[0] = win32console.CreateConsoleScreenBuffer(DesiredAccess = win32con.GENERIC_READ | win32con.GENERIC_WRITE, ShareMode=0, SecurityAttributes=None, Flags=1)
        self.writeto = self.buffer[0]
        self.pushing = self.buffer[1]
        self.pushing.SetConsoleActiveScreenBuffer()

    def write(self, text: str):
        self.writeto.WriteConsole(text)

class slowprint(io.StringIO):
    def __init__(self, delay: int = 0.1):
        self.queue = queue.Queue()
        #self.queue = []
        self.delay = delay
        self.doshit, self.stopdo = True, False
        
        self.timerctl = threading.Thread(target=self._do)
        self.timerctl.daemon = True
        self.timerctl.start()
    
    def write(self, text: str):
        self.queue.put(text)

    def _do(self):
        while self.doshit:
            if self.queue.qsize() > 0: 
                puts(self.queue.get(), newline=False)
                time.sleep(self.delay)
        else:
            if self.stopdo: return

    def _stop(self):
        if self.queue.qsize() == 0: 
            self.doshit = False
            self.stopdo = True
            self.stoptimer.stop()
    
    def getreadytostop(self):
        self.stoptimer = RepeatedTimer(0.1, function=self._stop)
        self.stoptimer.start()

class time_clc:
    def __init__(self, name = "", speak_on_start: bool = False, 
                start_fmt: str = '[{name}]\n',
                result_fmt: str = '[{name}] took {time_elapsed}s\n',
                checkpoint_fmt: str | None = '[{name} > {point_name} ({point_num})] took {time_point_elapsed}s since last checkpoint\n'
                ):
        self.startt = time.time()
        self.ckptimes = [self.startt]
        self.ckp_num = 0
        self.name = name
        self.start_fmt = start_fmt
        self.result_fmt = result_fmt
        self.checkpoint_fmt = checkpoint_fmt or self.result_fmt
        if speak_on_start: print(self.start_fmt.format(name=self.name), end='', flush=self.start_fmt.endswith('\n'))
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.endt = time.time()
        self.time_elapsed = self.endt - self.startt
        data = {"name": self.name, "time_elapsed": round(self.time_elapsed, 2)}
        print(self.result_fmt.format(**data), end='', flush=self.result_fmt.endswith('\n'))

    def wrapper(func, speak_on_start: bool = False, start_fmt: str = '[%s]\n', result_fmt: str = '[%s] took %.2fs\n'):
        def wrapper(*args, **kwargs):
            if speak_on_start: print(start_fmt % func.__name__, end='', flush=start_fmt.endswith('\n'))
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            time_elapsed = end - start
            data = {"name": func.__name__, "time_elapsed": round(time_elapsed, 2)}
            print(result_fmt.format(**data), end='', flush=result_fmt.endswith('\n'))
            return result
        return wrapper
    w = wrapper

    def checkpoint(self, name: str, checkpoint_fmt: str | None = None):
        true_checkpoint = checkpoint_fmt or self.checkpoint_fmt
        current_time = time.time()
        time_elapsed = current_time - self.ckptimes[self.ckp_num]
        self.ckp_num += 1
        self.ckptimes.append(current_time)
        data = {"name": self.name, "point_name": name, "point_num": self.ckp_num, "time_point_elapsed": round(time_elapsed, 2), "time_elapsed": round(current_time - self.startt, 2)}
        print(true_checkpoint.format(**data), end='', flush=true_checkpoint.endswith('\n'))

    def end(self):
        self.endt = time.time()
        data = {"name": self.name, "time_elapsed": round(self.endt - self.startt, 2)}
        print(self.result_fmt.format(**data), end='', flush=self.result_fmt.endswith('\n'))

class thread_sep:
    def __init__(self, name_map: dict[str: str] = {}):
        """
        name_map: dict[str: str]
            key: thread name | use * in string for wildcards
            value: new thread name
        """
    
        self.stdout = sys.__stdout__
        sys.stdout = self
        
        self.has_star = False
        for i in name_map.keys(): 
            if '*' in i: self.has_star = True
        
        if self.has_star:
            name_mp = {}
            for i, v in name_map.items():
                stars = [v + n for v, n in enumerate([i for i, w in enumerate(i) if '*' in w])] # keep track of stars
                gi = re.escape(i.replace('*', '')) # escape everything
                stri = list(gi)
                for y in stars: stri.insert(y, r'.*')
                name_mp[v] = re.compile(''.join(stri))
            self.name_map = name_mp
        else: self.name_map = name_map
    
    def write(self, text):
        thread = threading.current_thread().name
        if self.has_star:
            for k, v in self.name_map.items():
                if re.match(v, thread): thread = k
        else:
            try: thread = self.name_map[thread]
            except: pass
        if text != '\n': self.stdout.write(f'{thread}: {text}\n')
    
    def flush(self): self.stdout.flush()


def progress_bar(current: int, total: int, name: str = "Progress", bar_length: int = 50, juststring: bool = False, arrow: str = '>', dash: str = '-', pad: str = ' '):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * dash + arrow
    padding = int(bar_length - len(arrow)) * pad
    endst = f'{name}: [{arrow}{padding}] {int(fraction*100)}%'.removeprefix(': ' if name.__len__() == 0 else '')
    if juststring: return endst
    else: 
        ending = '\n' if current >= total else '\r'
        print(endst, end=ending)

def progress_bar2(start_time: float, current_time: float = time.time(), timetotal: int = 30, size: int = 1, ljust: int = 4):
    remains = timetotal - (current_time - start_time)
    progbarsize = timetotal * size
    timepassed = (round(remains * size) - progbarsize) * -1
    progbarstring = '█' * timepassed + '░' * int(progbarsize - timepassed) + ' ' + str(round(remains, 2)).ljust(ljust, '0') + 's'
    return progbarstring

def printc(n: str, *d, f: bool = False, nc = False, firstclr: object = colored.blue, sepL: int = 0, sepC: str = ' ', Beg: str = colored.green('//|'), BegL: int = 4, end: str = '\n', returnstring: bool = False, stream: None = None) -> str | None:
    sep = sepC * sepL; w = ''.join(map(str, d))
    if not f: 
        if nc: outstr = (n + sep + w + end)
        else: outstr = (firstclr(n) + sep + w + end)
    else: 
        if nc: outstr = (w + sep + n + end)
        else: outstr = (firstclr(w) + sep + n + end)
    if returnstring: return outstr
    else: 
        with indent(BegL, quote=Beg): 
            if stream == None: puts(outstr, newline=False)
            else: puts(outstr, stream=stream, newline=False)

def formatdict(thing: dict | list , item_color: object = colored.red, key_color: object = colored.green) -> str:
    if type(thing) == dict:
        retirm = '{ '
        for k, v in thing.items(): retirm += f"{key_color(k)}: {item_color(v)}, "
        retirmo = retirm.removesuffix(', ') + ' }'
    elif type(thing) == list:
        retirm = '[ '
        for i in thing: retirm += f"{item_color(i)}, "
        retirmo = retirm.removesuffix(', ') + ' ]'
    else: raise ValueError(f"{type(thing)} is not a dict or list >> '{thing}'")
    return retirmo

if __name__ == '__main__': exit()
