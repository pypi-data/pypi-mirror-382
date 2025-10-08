import requests
import os
import sys
import platform
import zipfile
import tarfile
import stat
from pathlib import Path
from typing import Optional, Literal

from .errors import UnsupportedSeleniumDriverError, UnableToDownloadSeleniumDriverError
DriverType = Literal['chrome', 'firefox']

def _driver_name(driver_type: str, platform_str: str, arch: str, version: str) -> str:
    return f"{driver_type}_{version}_{platform_str}_{arch}"

def download_driver(driver_type: DriverType, download_path: Path, version: Optional[str] = None) -> Path:
    """
    Downloads the specified Selenium WebDriver to a given path.

    Args:
        driver_type (DriverType): The type of driver to download ('chrome' or 'firefox').
        download_path (Path): The directory path to save the driver executable.
        version (str, optional): The version of the driver to download. 
                                 If None, downloads the latest stable version. Defaults to None.
    
    Returns:
        str: The full path to the downloaded driver executable.
    """
    driver_type_str = driver_type.lower()
    if driver_type_str not in ['chrome', 'firefox']:
        raise UnsupportedSeleniumDriverError(driver_type)

    # --- 1. Determine OS and Architecture ---
    os_name = sys.platform
    arch = platform.machine()
    
    # --- 2. Create destination path if it doesn't exist ---
    os.makedirs(download_path, exist_ok=True)


    # --- 3. Handle Driver-Specific Logic ---
    if driver_type_str == 'firefox':
        executable_path = _download_geckodriver(download_path, version, os_name, arch)
    elif driver_type_str == 'chrome':
        executable_path = _download_chromedriver(download_path, version, os_name, arch)
    else:
        raise UnsupportedSeleniumDriverError(driver_type)
    return executable_path




def _download_geckodriver(download_path: Path, version: Optional[str], os_name: str, arch: str) -> Path:
    """Handles the download and extraction of geckodriver."""
    base_url = "https://api.github.com/repos/mozilla/geckodriver/releases"
    
    if version:
        # Add 'v' prefix if missing, e.g., 0.34.0 -> v0.34.0
        if not version.startswith('v'):
            version = f"v{version}"
        url = f"{base_url}/tags/{version}"
    else:
        url = f"{base_url}/latest"

    response = requests.get(url)
    response.raise_for_status()
    release_data = response.json()
    
    if not version:
        version = release_data['tag_name']
        print(f"Found latest geckodriver version: {version}")
    if not version:
        raise UnableToDownloadSeleniumDriverError('geckodriver', 'Could not determine geckodriver version.')
    filename = _driver_name('geckodriver', os_name, arch, version)
    # Determine asset name based on platform
    asset_fragment = ""
    if 'linux' in os_name:
        asset_fragment = 'linux64.tar.gz' if '64' in arch else 'linux32.tar.gz'
        if 'aarch64' in arch or 'arm64' in arch:
            asset_fragment = 'linux-aarch64.tar.gz'
    elif 'darwin' in os_name: # macOS
        # Modern geckodriver releases for macOS are universal binaries
        asset_fragment = 'macos.tar.gz'
        if 'aarch64' in arch or 'arm64' in arch: # Check for aarch64 specific if universal isn't there
             if not any(asset['name'].endswith(asset_fragment) for asset in release_data['assets']):
                  asset_fragment = 'macos-aarch64.tar.gz'
    elif 'win' in os_name or 'cygwin' in os_name:
        asset_fragment = 'win64.zip' if '64' in arch else 'win32.zip'
        if 'aarch64' in arch or 'arm64' in arch:
            asset_fragment = 'win-aarch64.zip'

    download_url = None
    for asset in release_data['assets']:
        if asset['name'].endswith(asset_fragment):
            download_url = asset['browser_download_url']
            break
    
    if not download_url:
        raise UnableToDownloadSeleniumDriverError('geckodriver', 'No suitable download URL found.')

    return _download_and_extract(download_url, download_path, 'geckodriver', filename)


def _download_chromedriver(download_path: Path, version: Optional[str], os_name: str, arch: str):
    """Handles the download and extraction of chromedriver."""
    base_url = "https://googlechromelabs.github.io/chrome-for-testing/"
    
    # Determine platform string for the JSON endpoint
    platform_str = ""
    if 'linux' in os_name:
        platform_str = 'linux-x64'
    elif 'darwin' in os_name: # macOS
        platform_str = 'mac-arm64' if 'aarch64' in arch or 'arm64' in arch else 'mac-x64'
    elif 'win' in os_name or 'cygwin' in os_name:
        platform_str = 'win64' if '64' in arch else 'win32'

    if not platform_str:
        raise UnsupportedSeleniumDriverError('chrome')

    latest_version = None
    if version:
        print(f"Fetching chromedriver version: {version}")
        # For a specific version, we need to search the full list
        versions_url = f"{base_url}known-good-versions-with-downloads.json"
        response = requests.get(versions_url)
        response.raise_for_status()
        all_versions_data = response.json()
        
        target_version_info = None
        for v_info in all_versions_data['versions']:
            if v_info['version'] == version:
                target_version_info = v_info
                break
        
        if not target_version_info:
             raise UnableToDownloadSeleniumDriverError('chromedriver', f"Version {version} not found.")
        
        downloads = target_version_info['downloads']['chromedriver']

    else:
        print("Fetching latest stable chromedriver version...")
        # For the latest version, we can use a simpler endpoint
        latest_url = f"{base_url}last-known-good-versions-with-downloads.json"
        response = requests.get(latest_url)
        response.raise_for_status()
        latest_data = response.json()
        
        latest_version = latest_data['channels']['Stable']['version']
        print(f"Found latest stable chromedriver version: {latest_version}")
        downloads = latest_data['channels']['Stable']['downloads']['chromedriver']

    version = version or latest_version
    if not version:
        raise UnableToDownloadSeleniumDriverError('chromedriver', 'Could not determine chromedriver version.')
    filename = _driver_name('chromedriver', os_name, arch, version)
    download_url = None
    for download in downloads:
        if download['platform'] == platform_str:
            download_url = download['url']
            break
    
    if not download_url:
        raise UnableToDownloadSeleniumDriverError('chromedriver', 'No suitable download URL found.')

    return _download_and_extract(download_url, download_path, 'chromedriver', filename)

def _download_and_extract(url: str, download_path: Path, driver_name: str, filename: str) -> Path:
    """Generic helper to download and extract a driver archive."""
    
    if not download_path.exists():
        download_path.mkdir(parents=True, exist_ok=True)
    # if file already exists, return it
    existing_file = download_path / filename
    if existing_file.exists():
        print(f"Driver already exists at: {existing_file}")
        return existing_file
    
    print(f"Downloading from: {url}")
    archive_name = os.path.basename(url)
    archive_path = download_path / archive_name
    # Download the file
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(archive_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    print(f"Extracting '{archive_name}'...")
    executable_name = f"{driver_name}.exe" if sys.platform.startswith('win') else driver_name
    final_path = None
    
    if archive_name.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            # Find the executable member in the zip
            for member_info in zip_ref.infolist():
                if member_info.filename.endswith(executable_name) and not member_info.is_dir():
                    # Extract the file directly into the target path, not a sub-folder
                    member_info.filename = os.path.basename(member_info.filename)
                    zip_ref.extract(member_info, download_path)
                    final_path = download_path / member_info.filename
                    break
            else:
                 raise UnableToDownloadSeleniumDriverError(driver_name, "Executable not found in the zip archive.")

    elif archive_name.endswith('.tar.gz'):
        with tarfile.open(archive_path, 'r:gz') as tar_ref:
            # geckodriver is typically at the root of the tarball
            tar_ref.extract(executable_name, download_path)
            final_path = download_path / executable_name

    # Make executable on Unix-like systems
    if not sys.platform.startswith('win') and final_path:
        current_permissions = os.stat(final_path).st_mode
        os.chmod(final_path, current_permissions | stat.S_IEXEC)

    # Clean up the downloaded archive
    os.remove(archive_path)
    if not final_path or not final_path.exists():
        raise UnableToDownloadSeleniumDriverError(driver_name, "Extraction failed or executable not found.")
    # move file to desired filename
    if final_path.name != filename:
        new_path = download_path / filename
        final_path.rename(new_path)
        final_path = new_path
    return final_path
