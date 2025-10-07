import builtins
import sys
import os

def acce(*args, **kwargs):
    message = " ".join(str(arg) for arg in args)
    if "@LAEGER_MO" not in message and "@sis_c" not in message:
        print(*args, **kwargs)
        print("Telegram: @LAEGER_MO - @sis_c")
    else:
        print(*args, **kwargs)

def install_global():
    try:
        if not hasattr(builtins, 'acce'):
            builtins.acce = acce       
        package_dir = os.path.dirname(os.path.abspath(__file__))
        if package_dir not in sys.path:
            sys.path.insert(0, package_dir)
            
    except Exception as e:
        print(f"")
install_global()