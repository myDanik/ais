"""Register the OFL Carlito fonts used by the Figma lecture for faithful local exports."""
import ctypes,os,shutil,winreg
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
font_dir=(Path(os.environ['LOCALAPPDATA'])/'Microsoft/Windows/Fonts').resolve()
font_dir.mkdir(parents=True,exist_ok=True)
gdi=ctypes.WinDLL('gdi32');gdi.AddFontResourceExW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint,ctypes.c_void_p]
for style in ['Regular','Bold']:
    src=ROOT/'assets/fonts/carlito'/f'Carlito-{style}.ttf';dst=(font_dir/src.name).resolve()
    assert dst.parent==font_dir and src.is_file()
    if not dst.exists():shutil.copy2(src,dst)
    elif dst.read_bytes()!=src.read_bytes():raise RuntimeError('Existing font differs; inspect before replacing')
    label='Carlito' if style=='Regular' else 'Carlito Bold'
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows NT\CurrentVersion\Fonts') as key:winreg.SetValueEx(key,label+' (TrueType)',0,winreg.REG_SZ,str(dst))
    print(label,gdi.AddFontResourceExW(str(dst),0,None))
result=ctypes.c_size_t();ctypes.windll.user32.SendMessageTimeoutW(0xffff,0x001D,0,0,2,1000,ctypes.byref(result))
