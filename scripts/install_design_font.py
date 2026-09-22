"""Install the project's OFL font for the current Windows user via the standard font APIs."""
import ctypes,json,os,shutil,winreg
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'assets/fonts/prata/Prata-Regular.ttf'
font_root=(Path(os.environ['LOCALAPPDATA'])/'Microsoft/Windows/Fonts').resolve()
destination=(font_root/'Prata-Regular.ttf').resolve()
assert destination.parent==font_root and source.is_file()
font_root.mkdir(parents=True,exist_ok=True)
if not destination.exists():shutil.copy2(source,destination)
elif source.read_bytes()!=destination.read_bytes():raise RuntimeError('A different Prata font is already installed; inspect before replacing')
with winreg.CreateKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows NT\CurrentVersion\Fonts') as key:
    winreg.SetValueEx(key,'Prata (TrueType)',0,winreg.REG_SZ,str(destination))
gdi=ctypes.WinDLL('gdi32');gdi.AddFontResourceExW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint,ctypes.c_void_p]
registered=gdi.AddFontResourceExW(str(destination),0,None)
result=ctypes.c_size_t()
ctypes.windll.user32.SendMessageTimeoutW(0xffff,0x001D,0,0,2,1000,ctypes.byref(result))
print(json.dumps({'font':'Prata','path':str(destination),'registered':registered}))
