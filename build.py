import os
import sys
import shutil
import logging
from pathlib import Path
import PyInstaller.__main__
import argparse
from concurrent.futures import ThreadPoolExecutor

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_assets():
    assets_dir = Path("assets")
    if not assets_dir.exists():
        logging.warning("Assets directory not found, creating...")
        assets_dir.mkdir()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=1, 
                       help='Number of parallel workers')
    return parser.parse_args()

def get_platform_config():
    configs = {
        "darwin": {
            "icon_path": os.path.join("assets", "icon.icns"),
            "data_files": [
                ('assets/icon.icns', 'assets'),
            ],
            "hidden_imports": [
                'uvloop',
                'asyncio',
                'playwright.async_api'
            ],
            "platform_options": [
                '--collect-submodules=asyncio',
                '--collect-submodules=playwright',
                '--collect-data=certifi'
            ]
        },
        "win32": {
            "icon_path": os.path.join("assets", "icon.ico"),
            "data_files": [
                ('assets\\icon.ico', 'assets'),
                ('binaries\\windows\\*', 'binaries\\windows')
            ],
            "hidden_imports": [
                'win32timezone',
                'asyncio'
            ],
            "platform_options": [
                '--collect-submodules=win32timezone',
                '--collect-submodules=asyncio',
                '--collect-data=certifi',
                '--collect-data=playwright',
            ]
        },
        "linux": {
            "icon_path": os.path.join("assets", "icon.png"),
            "data_files": [
                ('assets/icon.png', 'assets'),
                ('binaries/linux/*', 'binaries/linux')
            ],
            "hidden_imports": [
                'uvloop',
                'asyncio'
            ],
            "platform_options": []
        }
    }
    return configs.get(sys.platform, configs["linux"])

def create_spec_file():
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules

datas = [('assets/icon.icns', 'assets')]
hiddenimports = ['uvloop', 'asyncio', 'playwright.async_api']
datas += collect_data_files('certifi')
hiddenimports += collect_submodules('asyncio')
hiddenimports += collect_submodules('playwright')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets'
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='url-markdown',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,  # Enable argv emulation for macOS
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon.icns'],
)

app = BUNDLE(
    exe,
    name='url-markdown.app',
    icon='assets/icon.icns',
    bundle_identifier=None,
)
"""
    with open("url-markdown.spec", "w") as spec_file:
        spec_file.write(spec_content)

def build_app():
    args = parse_args()
    setup_logging()
    ensure_assets()
    
    spec_file = "url-markdown.spec"
    
    if not os.path.exists(spec_file):
        logging.info(f"{spec_file} not found, creating...")
        create_spec_file()
    
    logging.info(f"Building using spec file: {spec_file}")
    
    try:
        PyInstaller.__main__.run([spec_file])
        logging.info("Build completed successfully")
    except Exception as e:
        logging.error(f"Build failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    build_app()