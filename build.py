import os
import sys
import logging
from pathlib import Path
import PyInstaller.__main__
import argparse

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
            "icon_path": "'assets/icon.icns'",  
            "data_files": [
                ('assets/icon.icns', 'assets'),
                ('logs/*', 'logs')
            ],
            "hidden_imports": [
                'uvloop',
                'asyncio',
                'playwright.async_api',
                'charset_normalizer',
                'charset_normalizer.md',
            ],
            "excludes": [
                'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
                'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
                'scipy', 'numpy', 'pandas', 'matplotlib', 'IPython', 'jupyter'
            ]
        },
        "win32": {
            "icon_path": "'assets/icon.ico'",  
            "data_files": [
                ('assets\\icon.ico', 'assets'),
                ('logs/*', 'logs')
            ],
            "hidden_imports": [
                'win32timezone',
                'asyncio',
                'charset_normalizer',
                'charset_normalizer.md',
            ],
            "excludes": [
                'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
                'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
                'scipy', 'numpy', 'pandas', 'matplotlib', 'IPython', 'jupyter'
            ]
        },
        "linux": {
            "icon_path": "'assets/icon.png'",  
            "data_files": [
                ('assets/icon.png', 'assets'),
                ('logs/*', 'logs')
            ],
            "hidden_imports": [
                'uvloop',
                'asyncio',
                'charset_normalizer',
                'charset_normalizer.md',
            ],
            "excludes": [
                'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
                'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
                'scipy', 'numpy', 'pandas', 'matplotlib', 'IPython', 'jupyter'
            ]
        }
    }
    return configs.get(sys.platform, configs["linux"])

def create_spec_file():
    config = get_platform_config()
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None
datas = {config['data_files']} + collect_data_files('certifi')
hiddenimports = {config['hidden_imports']} + collect_submodules('asyncio') + collect_submodules('playwright')
excludes = {config['excludes']}

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=2,  # Enable optimization
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='URL Markdown',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,  # Enable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={config['icon_path']},
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='URL Markdown.app',
        icon={config['icon_path']},
        bundle_identifier='com.urlmarkdown.app',
        info_plist={{
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'CFBundleShortVersionString': '1.0.0',
        }},
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
        PyInstaller.__main__.run([
            spec_file,
            '--noconfirm',
            '--clean',
            '--log-level=WARN',
            '--distpath=dist',
            '--workpath=build'
        ])
        logging.info("Build completed successfully")
    except Exception as e:
        logging.error(f"Build failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    build_app()