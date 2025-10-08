from .download_selenium_driver import DriverType, download_driver
from typing import Optional
import os
import tempfile
import pathlib


def selenium_driver(driver_type: DriverType, version: Optional[str] = None) -> pathlib.Path:
    """
    Returns the selenium driver. 
    Args:
        driver_type (DriverType): The type of driver to download ('chrome' or 'firefox').
        version (str, optional): The version of the driver to download. 
                                 If None, downloads the latest stable version. Defaults to None.
    
    Returns:
        str: The full path to the downloaded driver executable.
    """
    selenium_download_path_str = os.environ.get('DATALOG_SELENIUM_DRIVER_PATH', None)
    if selenium_download_path_str is None:
        # use temp directory
        selenium_download_path_str = tempfile.gettempdir()
    selenium_download_path = pathlib.Path(selenium_download_path_str)
    
    download_file = download_driver(driver_type, selenium_download_path, version)
    if driver_type == 'chrome' and not os.access(download_file, os.X_OK):
        # make executable
        download_file.chmod(download_file.stat().st_mode | 0o111)
        
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        service = ChromeService(executable_path=str(download_file))
        options = webdriver.ChromeOptions()
        headless = os.environ.get('DATALOG_GUI', '0') == '0'
        if headless:
            options.add_argument('--headless=new')
        return webdriver.Chrome(service=service, options=options)
    elif driver_type == 'gecko' and not os.access(download_file, os.X_OK):
        # make executable
        download_file.chmod(download_file.stat().st_mode | 0o111)
        
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service as GeckoService
        service = GeckoService(executable_path=str(download_file))
        options = webdriver.FirefoxOptions()
        headless = os.environ.get('DATALOG_GUI', '0') == '0'
        if headless:
            options.add_argument('--headless')
        return webdriver.Firefox(service=service, options=options)
    