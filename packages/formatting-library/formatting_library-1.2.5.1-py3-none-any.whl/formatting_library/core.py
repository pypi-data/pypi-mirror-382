# ======= #
# Imports #
# ======= #

import time
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from PIL import Image # type: ignore
import ctypes
import os
import platform
import subprocess

# ========= #
# Variables # 
# ========= #

IMAGE_CHARACTER = "▄"
RESET = "\033[0m"

RAINBOW_COLORS = [
    (255, 179, 179),
    (255, 217, 179),
    (255, 255, 179),
    (179, 255, 179),
    (179, 179, 255),
    (217, 179, 255)
]

# ================ #
# Color Converters #
# ================ #

@dataclass
class RGB:

    r: int
    g: int
    b: int

    def __post_init__(self):
        if not all(0 <= val <= 255 for val in (self.r, self.g, self.b)):
            raise ValueError("RGB values must be between 0 and 255")

    @classmethod
    def from_sequence(cls, rgb: Union[List[int], Tuple[int, ...]]) -> 'RGB':
        if len(rgb) != 3:
            raise ValueError("RGB must contain exactly 3 values")
        return cls(*rgb)
    
    def to_foreground(self) -> str:
        return f"\033[38;2;{self.r};{self.g};{self.b}m"
    
    def to_background(self) -> str:
        return f"\033[48;2;{self.r};{self.g};{self.b}m"
    
    def to_dual(self, bottom: 'RGB') -> str:
        return f"\033[48;2;{self.r};{self.g};{self.b};38;2;{bottom.r};{bottom.g};{bottom.b}m"
    
class ColorFuncs:

    @staticmethod
    def rgb_fore(rgb: Union[RGB, List[int], Tuple[int, ...]]) -> str:
        if not isinstance(rgb, RGB):
            rgb = RGB.from_sequence(rgb)
        return rgb.to_foreground()

    @staticmethod
    def rgb_back(rgb: Union[RGB, List[int], Tuple[int, ...]]) -> str:
        if not isinstance(rgb, RGB):
            rgb = RGB.from_sequence(rgb)
        return rgb.to_background()

# ================== #
# Terminal Modifiers #
# ================== #

class Terminal:
    
    @staticmethod
    def clear_screen():
        print("\033c\033[H", end="")
    
    @staticmethod
    def set_cursor_position(x: int, y: int):
        print(f"\033[{x};{y}H", end="")
    
    @staticmethod
    def scroll_cursor(lines: int):
        direction = "A" if lines <= 0 else "B"
        print(f"\033[{abs(lines)}{direction}", end="")
    
    @staticmethod
    def replace_current_line(text: str):
        print(f"\33[2K\r{text}", end="")
    
    @staticmethod
    def replace_line(y: int, text: str):
        print(f"\33[s\33[{y};0H\33[2K\r{text}\33[u", end="")


# =============== #
# Cool Formatting #
# =============== #

class TextFormatter:
    
    @staticmethod
    def rainbow_text(text: str, *, background: bool = False) -> str:
        color_func = ColorFuncs.rgb_back if background else ColorFuncs.rgb_fore
        non_spaces = [(i, c) for i, c in enumerate(text) if c != ' ']
        
        if not non_spaces:
            return text
        
        result = list(text)
        
        for i, (pos, char) in enumerate(non_spaces):
            color_index = min(
                int(i * len(RAINBOW_COLORS) / len(non_spaces)),
                len(RAINBOW_COLORS) - 1
            )
            rgb_color = RAINBOW_COLORS[color_index]
            result[pos] = f"{color_func(rgb_color)}{char}{RESET}"
        
        return ''.join(result)
    
    @staticmethod
    def align_text(text: str, width: int, alignment: str = "right") -> str:
        if width < len(text):
            raise ValueError(f"Width ({width}) cannot be less than text length ({len(text)})")
        
        mappings = {
            "left": f"{text:<{width}}",
            "right": f"{text:>{width}}",
            "center": f"{text:^{width}}"
        }
        
        try:
            return mappings[alignment.lower()]
        except KeyError:
            raise ValueError("Invalid alignment. Choose: 'left', 'right', 'center'")
    
    @staticmethod
    def substitute_text(text: str, replacement: str, start: int = 0, end: Optional[int] = None) -> str:
        if end is None:
            return text[:start] + replacement
        return text[:start] + replacement + text[end:]
    
@dataclass
class PrintOptions:
    speed: float = 10.0
    text_color: Optional[Union[RGB, List[int], Tuple[int, ...]]] = None
    background_color: Optional[Union[RGB, List[int], Tuple[int, ...]]] = None
    end: str = "\n"
    newline_delay: float = 0.5


class Printer:
    
    @staticmethod
    def slow_print(text: str, options: Optional[PrintOptions] = None):
        if options is None:
            options = PrintOptions()
        
        delay = 1 / options.speed
        
        if options.text_color:
            print(ColorFuncs.rgb_fore(options.text_color), end="")
        if options.background_color:
            print(ColorFuncs.rgb_back(options.background_color), end="")
        
        for char in text:
            print(char, end="", flush=True)
            time.sleep(delay)
            if char == "\n":
                time.sleep(options.newline_delay)
        
        print(RESET, end=options.end)
    
    @staticmethod
    def print_box(text: str):
        """
        You can use this function to create the cool looking boxes that I've been using to group the code!
        """
        border = f"# {'=' * len(text)} #"
        print(f"{border}\n# {text} #\n{border}")

# ===================== #
# Custom Text Formatter #
# ===================== #

@dataclass
class ImprovedColors:
    
    COLOR_MAP: Dict[str, str] = field(default_factory=lambda: {
        '0': "\33[38;2;0;0;0m",
        '1': "\33[38;2;0;0;170m",
        '2': "\33[38;2;0;170;0m",
        '3': "\33[38;2;0;170;170m",
        '4': "\33[38;2;170;0;0m",
        '5': "\33[38;2;170;0;170m",
        '6': "\33[38;2;255;170;0m",
        '7': "\33[38;2;170;170;170m",
        '8': "\33[38;2;85;85;85m",
        '9': "\33[38;2;85;85;255m",
        'a': "\33[38;2;85;255;85m",
        'b': "\33[38;2;85;255;255m",
        'c': "\33[38;2;255;85;85m",
        'd': "\33[38;2;255;85;255m",
        'e': "\33[38;2;255;255;85m",
        'f': "\33[38;2;255;255;255m",
        'l': '\33[1m',
        'n': '\33[4m',
        'o': '\33[3m',
        'r': "\33[0m"
    })
    
    def format_text(self, text: str) -> str:
        def replace_color_code(match):
            code = match.group(1).lower()
            return self.COLOR_MAP.get(code, '')
        
        result = re.sub(r'&(.)', replace_color_code, text)
        return result + RESET

# ============== #
# Image Renderer #
# ============== #

class ImageRenderer:
    
    @staticmethod
    def image_to_ascii(image_path: Union[str, Path]) -> str:
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        lines = []
        
        with Image.open(image_path) as image:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            width, height = image.size
            
            for y in range(0, height - 1, 2):
                line_parts = []
                for x in range(width):
                    top_pixel = RGB(*image.getpixel((x, y))) # type: ignore
                    bottom_pixel = RGB(*image.getpixel((x, y + 1))) # type: ignore
                    
                    color_code = top_pixel.to_dual(bottom_pixel)
                    line_parts.append(f"{color_code}{IMAGE_CHARACTER}")
                
                lines.append(''.join(line_parts) + RESET)
            
            if height % 2 == 1:
                line_parts = []
                for x in range(width):
                    top_pixel = RGB(*image.getpixel((x, height - 1))) # type: ignore
                    bottom_pixel = RGB(255, 255, 255)
                    
                    color_code = top_pixel.to_dual(bottom_pixel)
                    line_parts.append(f"{color_code}{IMAGE_CHARACTER}")
                
                lines.append(''.join(line_parts) + RESET)
        
        return '\n'.join(lines)

class CBuilder:
    """
    WARNING: This class uses os.system() to compile C code and creates 
    directories. Only use with trusted source files in secure environments.
    
    Builds and loads C shared libraries for Python integration.
    Supports Windows (.dll), macOS (.dylib), and Linux (.so).
    """
    
    def __init__(self, directory=".", filename="main", build_command=None):
        self.directory = directory
        self.filename = filename
        self.build_command = build_command
        self.lib = None
        self.platform = platform.system().lower()
        self._build()
    
    def _get_library_extension(self):
        extensions = {
            'windows': '.dll',
            'darwin': '.dylib',
            'linux': '.so'
        }
        return extensions.get(self.platform, '.so')
    
    def _get_default_compiler_command(self, output_path, input_path):
        if self.platform == 'windows':
            return f"gcc -Ofast -shared -o {output_path} {input_path}"
        elif self.platform == 'darwin':
            return f"gcc -Ofast -march=native -mtune=native -funroll-loops -fomit-frame-pointer -DNDEBUG -shared -fPIC -undefined dynamic_lookup -o {output_path} {input_path}"
        else:
            return f"gcc -Ofast -march=native -mtune=native -funroll-loops -fomit-frame-pointer -DNDEBUG -shared -fPIC -o {output_path} {input_path} -lrt"
    
    def _build(self):
        lib_extension = self._get_library_extension()
        
        if self.directory == ".":
            output_path = f"build/{self.filename}{lib_extension}"
            lib_path = f"./build/{self.filename}{lib_extension}"
        else:
            output_path = f"{self.directory}/build/{self.filename}{lib_extension}"
            lib_path = f"./{self.directory}/build/{self.filename}{lib_extension}"
        
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        input_path = f"{self.directory}/{self.filename}.c"
        
        if self.build_command is None:
            compile_command = self._get_default_compiler_command(output_path, input_path)
        else:
            compile_command = self.build_command.format(
                output=output_path,
                input=input_path
            )
        
        result = os.system(compile_command)
        
        if result == 0:
            self.lib = ctypes.CDLL(lib_path)
        else:
            platform_info = {
                'windows': 'Ensure MinGW, MSYS2, or Visual Studio Build Tools are installed',
                'darwin': 'Ensure Xcode Command Line Tools are installed (xcode-select --install)',
                'linux': 'Ensure GCC and build-essential are installed'
            }
            suggestion = platform_info.get(self.platform, 'Ensure GCC compiler is available')
            raise RuntimeError(
                f"Compilation failed with code {result} on {self.platform.title()}. "
                f"{suggestion}"
            )
    
    def define_function(self, func_name, args=None, rtype=None):
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        if args is None:
            args = []
        
        func_obj = getattr(self.lib, func_name)
        
        if isinstance(args, list):
            func_obj.argtypes = args
        else:
            func_obj.argtypes = []
        
        func_obj.restype = rtype
        return func_obj
    
    def get_platform_info(self):
        return {
            'platform': self.platform,
            'library_extension': self._get_library_extension(),
            'python_architecture': platform.architecture(),
            'machine': platform.machine()
        }

class Esoteric:
    @staticmethod
    def _get_bin_path():
        module_dir = Path(__file__).parent
        return module_dir / "_bin"
    
    EXECUTABLES = {
        "befunge": {
            "linux": "linux/bef98",
            "darwin": "darwin/bef98",
        },
        "lolcode": {
            "darwin": "darwin/lci",
            "linux": "linux/lci",
            "windows": "windows/lci.exe",
        }
    }

    @staticmethod
    def _run_language(language, filename=''):
        if not filename:
            raise ValueError("Filename cannot be empty")
        
        platform_name = platform.system().lower()
        executables = Esoteric.EXECUTABLES.get(language)
        
        if executables is None:
            raise ValueError(f"Unknown language: {language}")
        
        executable_rel_path = executables.get(platform_name)
        
        if executable_rel_path is None:
            raise RuntimeError(
                f"{platform_name} is currently not supported for {language}."
            )
        
        bin_path = Esoteric._get_bin_path()
        executable_path = bin_path / executable_rel_path
        
        if not executable_path.is_file():
            raise FileNotFoundError(
                f"Executable not found: {executable_path}\n"
                f"Bin directory: {bin_path}\n"
                f"Bin exists: {bin_path.exists()}\n"
                f"Contents: {list(bin_path.rglob('*')) if bin_path.exists() else 'N/A'}"
            )
        
        if platform_name in ['linux', 'darwin']:
            try:
                os.chmod(executable_path, 0o755)
            except Exception as e:
                print(f"Warning: Could not set executable permissions: {e}")
        
        try:
            result = subprocess.run(
                [str(executable_path), filename],
                check=True,
                capture_output=False
            )
            return result.returncode
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Execution failed with code {e.returncode}")

    @staticmethod
    def runBefunge(filename=''):
        return Esoteric._run_language("befunge", filename)

    @staticmethod
    def runLOLCODE(filename=''):
        return Esoteric._run_language("lolcode", filename)

    
    
# ======= #
# Aliases #
# ======= #

clear_screen = Terminal.clear_screen
set_cursor_position = Terminal.set_cursor_position
scroll_cursor = Terminal.scroll_cursor
replace_current_line = Terminal.replace_current_line
replace_line = Terminal.replace_line

rainbow_text = TextFormatter.rainbow_text
align = TextFormatter.align_text
substitute = TextFormatter.substitute_text

slow_print = Printer.slow_print
ccb_gen = Printer.print_box

rgb_fore = ColorFuncs.rgb_fore
rgb_back = ColorFuncs.rgb_back

COLORS = ImprovedColors()
formatted = COLORS.format_text

img_to_ascii = ImageRenderer.image_to_ascii

runBefunge = Esoteric.runBefunge
runLOLCODE = Esoteric.runLOLCODE