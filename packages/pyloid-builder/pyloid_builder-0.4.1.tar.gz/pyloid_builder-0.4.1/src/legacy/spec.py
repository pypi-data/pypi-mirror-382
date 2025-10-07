import json
from pathlib import Path
import platform


def get_platform() -> str:
	"""
	Returns the name of the current system's platform.

	This function uses `platform.system()` to return the name of the current operating system.

	Returns
	-------
	"windows" | "macos" | "linux"
	    - "windows" for Windows systems
	    - "macos" for macOS systems
	    - "linux" for Linux systems

	Examples
	--------
	>>> from pyloid.utils import get_platform
	>>> platform_name = get_platform()
	>>> print(platform_name)
	windows
	"""
	os_name = platform.system().lower()
	os_type = {'darwin': 'macos', 'linux': 'linux', 'windows': 'windows'}.get(os_name)
	if os_type is None:
		raise ValueError(f'Unsupported platform: {os_name}')

	return os_type


def create_spec_from_json(json_path):
	with open(json_path, 'r', encoding='utf-8') as f:
		config = json.load(f)

	os_type = get_platform()

	if os_type == 'macos':
		spec_content = _create_macos_spec(config)
	elif os_type == 'linux':
		spec_content = _create_linux_spec(config)
	else:  # windows
		spec_content = _create_windows_spec(config)

	spec_path = Path(f'build-{os_type}.spec')
	spec_path.write_text(spec_content, encoding='utf-8')

	return str(spec_path)


def _create_windows_spec(config):
	bundle_type = config.get('bundle', {}).get('windows', 'directory')
	console = config.get('console', False)

	base_spec = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{config['main_script']}'],
    pathex={config.get('pathex', [])},
    binaries={config.get('binaries', [])},
    datas={config.get('datas', [])},
    hiddenimports={config.get('hiddenimports', [])},
    hookspath={config.get('hookspath', [])},
    hooksconfig={config.get('hooksconfig', {})},
    runtime_hooks={config.get('runtime_hooks', [])},
    excludes={config.get('excludes', [])},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
"""

	if bundle_type == 'onefile':
		return (
			base_spec
			+ f"""
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{config.get('name', 'pyloid-app')}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{config.get('icon', 'src-pyloid/icons/icon.ico')}'
)
"""
		)
	else:
		return (
			base_spec
			+ f"""
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{config.get('name', 'pyloid-app')}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console={console},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{config.get('icon', 'src-pyloid/icons/icon.ico')}'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{config.get('name', 'pyloid-app')}'
)
"""
		)


def _create_macos_spec(config):
	console = config.get('console', False)
	return f"""# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['{config['main_script']}'],
    pathex={config.get('pathex', [])},
    binaries={config.get('binaries', [])},
    datas={config.get('datas', [])},
    hiddenimports={config.get('hiddenimports', [])},
    hookspath={config.get('hookspath', [])},
    hooksconfig={config.get('hooksconfig', {})},
    runtime_hooks={config.get('runtime_hooks', [])},
    excludes={config.get('excludes', [])},
    noarchive=False,
    optimize=0
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{config.get('name', 'pyloid-app')}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console={console},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{config.get('icon', 'src-pyloid/icons/icon.ico')}'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{config.get('name', 'pyloid-app')}'
)

app = BUNDLE(
    coll,
    name='{config.get('name', 'pyloid-app')}.app',
    icon='{config.get('icon', 'src-pyloid/icons/icon.icns')}',
    bundle_identifier=None
)
"""


def _create_linux_spec(config):
	bundle_type = config.get('bundle', {}).get('linux', 'directory')
	console = config.get('console', False)

	base_spec = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{config['main_script']}'],
    pathex={config.get('pathex', [])},
    binaries={config.get('binaries', [])},
    datas={config.get('datas', [])},
    hiddenimports={config.get('hiddenimports', [])},
    hookspath={config.get('hookspath', [])},
    hooksconfig={config.get('hooksconfig', {})},
    runtime_hooks={config.get('runtime_hooks', [])},
    excludes={config.get('excludes', [])},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
"""

	if bundle_type == 'onefile':
		return (
			base_spec
			+ f"""
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{config.get('name', 'pyloid-app')}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{config.get('icon', 'src-pyloid/icons/icon.png')}'
)
"""
		)
	else:
		return (
			base_spec
			+ f"""
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{config.get('name', 'pyloid-app')}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console={console},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{config.get('icon', 'src-pyloid/icons/icon.png')}'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{config.get('name', 'pyloid-app')}'
)
"""
		)
