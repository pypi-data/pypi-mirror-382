import os
import sys
import site
import builtins
import glob
import subprocess
import shutil
from .core import acce

def find_all_python_versions():
    python_versions = []
    home_dir = os.path.expanduser("~")
    search_paths = [
        "/usr/bin/python*",
        "/usr/local/bin/python*", 
        f"{home_dir}/.local/bin/python*",
        "/opt/python*/bin/python*",
        "/usr/lib/python*",
        "/usr/local/lib/python*"
    ]
    
    for path_pattern in search_paths:
        for python_path in glob.glob(path_pattern):
            if os.path.isfile(python_path) and os.access(python_path, os.X_OK):
                try:
                    if "python" in os.path.basename(python_path):
                        if not any(x in python_path for x in ["config", "m", "env"]):
                            python_versions.append(python_path)
                except:
                    continue
    
    return list(set(python_versions))

def install_for_python_version(python_executable):
    try:
        get_site_packages_cmd = [
            python_executable, 
            "-c", 
            "import site; print('\\n'.join(site.getsitepackages() + [site.getusersitepackages()]))"
        ]
        
        result = subprocess.run(get_site_packages_cmd, capture_output=True, text=True)
        site_packages_paths = result.stdout.strip().split('\n')
        acce_code = '''\
def acce(*args, **kwargs):
    print(*args, **kwargs)
try:
    import builtins
    builtins.acce = acce
    acce("Programmer Seo Hook : @LAEGER_MO : @sis_c")
    
except:
    try:
        import __builtin__ as builtins
        builtins.acce = acce
    except:
        pass

__all__ = ['acce']
'''
        
        usercustomize_code = '''\
try:
    try:
        from acce import acce
    except:
        def acce(*args, **kwargs):
            print(*args, **kwargs)           
    try:
        import builtins
        if not hasattr(builtins, 'acce'):
            builtins.acce = acce
    except:
        try:
            import __builtin__ as builtins
            if not hasattr(builtins, 'acce'):
                builtins.acce = acce
        except:
            pass
except Exception as e:
    pass
'''
        
        for site_dir in site_packages_paths:
            try:
                if os.path.exists(site_dir):
                    os.makedirs(site_dir, exist_ok=True)                    
                    acce_path = os.path.join(site_dir, "acce.py")
                    with open(acce_path, "w", encoding="utf-8") as f:
                        f.write(acce_code)                    
                    usercustomize_path = os.path.join(site_dir, "usercustomize.py")
                    with open(usercustomize_path, "w", encoding="utf-8") as f:
                        f.write(usercustomize_code)                    
                    print(f"")
                    return True                    
            except Exception as e:
                print(f"")
                continue        
        return False        
    except Exception as e:
        print(f"")
        return False

def install_all_versions():
    python_versions = find_all_python_versions()
    
    if not python_versions:
        print("")
        return
    for i, version in enumerate(python_versions, 1):
        print(f"")
    
    success_count = 0
    for python_version in python_versions:
        if install_for_python_version(python_version):
            success_count += 1
        else:
            print(f"")
    install_current_session()

def install_current_session():
    try:
        if not hasattr(builtins, 'acce'):
            builtins.acce = acce
            print("")        
    except Exception as e:
        print()

def manual_install_specific_versions():
    python_versions = [
        'python2', 'python2.7', 'python3', 'python3.6', 'python3.7', 'python3.8',
        'python3.9', 'python3.10', 'python3.11', 'python3.12', 'python3.13'
    ]
    
    for version in python_versions:
        for path in ['/usr/bin/', '/usr/local/bin/', '/opt/local/bin/']:
            python_path = os.path.join(path, version)
            if os.path.exists(python_path):
                install_for_python_version(python_path)

def main():
    install_all_versions()
    manual_install_specific_versions()
if __name__ == "__main__":
    main()