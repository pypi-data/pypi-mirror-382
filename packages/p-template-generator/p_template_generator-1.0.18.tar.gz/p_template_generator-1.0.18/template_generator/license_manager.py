import os
import platform

def _get_license_file_path():
    if platform.system() == "Windows":
        appdata = os.environ.get('APPDATA', '')
        config_dir = os.path.join(appdata, 'template_generator')
    else:
        home = os.path.expanduser('~')
        config_dir = os.path.join(home, '.config', 'template_generator')
    
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, 'license.txt')

def read_license():
    try:
        file_path = _get_license_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
    except Exception:
        pass
    
    return None

def write_license(license_key):
    if not license_key:
        return False
    
    try:
        file_path = _get_license_file_path()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(license_key)
        return True
    except Exception:
        return False