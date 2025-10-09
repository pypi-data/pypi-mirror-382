from .__init__ import printc
from .__init__ import windows
from .__init__ import msvcrt, keyboard
# how the fuck was this even allowed? circular import
from threading import Timer
from pick import pick


## <misc.class>
class Choice:
    def __init__(self, index: int, option: str):
        self.index = index
        self.option = option

class RepeatedTimer:
    def __init__(self, interval: float, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
## </misc.class>

## <misc.func>
def isdebug(args: list) -> bool: s = args.copy(); s.pop(0); return '-d' in args or '--debug' in s

def choose_from_list(title: str, options: list, indi: str = "*", minselcont: int = 1) -> Choice:
    option, index = pick(options, title, indi, min_selection_count=minselcont); index += 1
    return Choice(index, option)

def ask_bool(prompt: str) -> bool:
    try: return {"true": True, "yes": True, "y": True, "false": False, "no": False, "n": False}[input(prompt).lower()]
    except KeyError: print("invalid input")

def ask_int(prompt: str) -> int:
    while True:
        try: return int(input(prompt))
        except ValueError: print("not a number")

def wind_getonekey(f: bool = True) -> str:
    if not windows: return ''
    if f: return str(msvcrt.getch(), 'utf-8')
    else: return msvcrt.getch()

def clearsc(type: int = 1):
    if type == 1: print('\033[2J')
    elif type == 2: print('\n' * 25)

def clearinp(t: int = 25, v: bool = False):
    for i in range(t):
        keyboard.press_and_release("\b")
        if v: printc(f"on the {i + 1} backspace")
## </misc.func>