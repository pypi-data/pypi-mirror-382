"""
Portable Browser Manager for Chrome Portable and Stealth Mode
Handles portable Chrome installations and anti-detection features
"""

import os
import sys
import logging
import zipfile
import requests
import platform
from pathlib import Path
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

logger = logging.getLogger(__name__)


class PortableBrowserManager:
    """
    Manages portable Chrome installations and stealth configurations
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the portable browser manager
        
        Args:
            base_dir: Base directory for portable browser files
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "portable_browser"
        self.chrome_dir = self.base_dir / "chrome"
        self.profiles_dir = self.base_dir / "profiles"
        self.drivers_dir = self.base_dir / "drivers"
        
        # Create directories if they don't exist
        for directory in [self.base_dir, self.chrome_dir, self.profiles_dir, self.drivers_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_chrome_portable_path(self) -> Optional[Path]:
        """
        Get the path to portable Chrome executable
        
        Returns:
            Path to Chrome executable or None if not found
        """
        possible_paths = [
            self.chrome_dir / "chrome.exe",
            self.chrome_dir / "GoogleChromePortable.exe",
            self.chrome_dir / "chrome" / "chrome.exe",
            self.chrome_dir / "Application" / "chrome.exe"
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found portable Chrome at: {path}")
                return path
        
        # Try to find system Chrome as fallback
        system_paths = [
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
            Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe"
        ]
        
        for path in system_paths:
            if path.exists():
                logger.info(f"Using system Chrome at: {path}")
                return path
        
        logger.warning("Chrome executable not found")
        return None
    
    def get_chromedriver_path(self) -> str:
        """
        Get the path to ChromeDriver
        
        Returns:
            Path to ChromeDriver executable
        """
        # Look for portable ChromeDriver first
        portable_driver = self.drivers_dir / "chromedriver.exe"
        if portable_driver.exists():
            logger.info(f"Using portable ChromeDriver at: {portable_driver}")
            return str(portable_driver)
        
        # Use webdriver-manager to download if not found
        try:
            driver_path = ChromeDriverManager().install()
            logger.info(f"Using managed ChromeDriver at: {driver_path}")
            return driver_path
        except Exception as e:
            logger.error(f"Failed to get ChromeDriver: {e}")
            raise
    
    def create_stealth_profile(self, profile_name: str = "stealth_default") -> Path:
        """
        Create a stealth profile directory with anti-detection settings
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Path to the profile directory
        """
        if profile_name is None:
            profile_name = "stealth_default"
        profile_path = self.profiles_dir / profile_name
        profile_path.mkdir(parents=True, exist_ok=True)
        
        # Create preferences file with stealth settings
        preferences = {
            "profile": {
                "default_content_setting_values": {
                    "notifications": 2,
                    "media_stream": 2,
                    "geolocation": 2
                },
                "default_content_settings": {
                    "popups": 0
                },
                "managed_default_content_settings": {
                    "images": 1
                }
            },
            "safebrowsing": {
                "enabled": False
            },
            "autofill": {
                "enabled": False
            },
            "password_manager_enabled": False,
            "credentials_enable_service": False,
            "extensions": {
                "ui": {
                    "developer_mode": True
                }
            }
        }
        
        import json
        prefs_file = profile_path / "Preferences"
        with open(prefs_file, 'w') as f:
            json.dump(preferences, f, indent=2)
        
        logger.info(f"Created stealth profile at: {profile_path}")
        return profile_path
    
    def get_stealth_options(self, profile_name: str = "stealth_default", 
                           headless: bool = False) -> Options:
        """
        Get Chrome options configured for stealth mode
        
        Args:
            profile_name: Name of the profile to use
            headless: Whether to run in headless mode
            
        Returns:
            Configured Chrome options
        """
        options = Options()
        
        # Basic stealth arguments
        stealth_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions-except",
            "--disable-extensions",
            "--disable-plugins-discovery",
            "--disable-plugins",
            "--disable-preconnect",
            "--disable-print-preview",
            "--disable-setuid-sandbox",
            "--disable-sync",
            "--hide-scrollbars",
            "--mute-audio",
            "--no-default-browser-check",
            "--no-first-run",
            "--disable-logging",
            "--disable-gpu-logging",
            "--disable-software-rasterizer",
            "--log-level=3",
            "--silent",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-infobars",
            "--disable-breakpad",
            "--disable-canvas-aa",
            "--disable-2d-canvas-clip-aa",
            "--disable-gl-drawing-for-tests",
            "--disable-dev-tools",
            "--disable-default-apps",
            "--disable-desktop-notifications",
            "--disable-file-system",
            "--disable-notifications",
            "--disable-prompt-on-repost",
            "--disable-domain-reliability",
            "--disable-ipc-flooding-protection",
            "--disable-hang-monitor",
            "--disable-client-side-phishing-detection",
            "--disable-popup-blocking",
            "--disable-background-networking",
            "--disable-background-media-suspend",
            "--disable-background-occluded-window-throttling",
            "--disable-background-tab-rendering",
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)
        
        # User agent
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Profile settings
        profile_path = self.create_stealth_profile(profile_name)
        options.add_argument(f"--user-data-dir={profile_path}")
        
        # Headless mode
        if headless:
            options.add_argument("--headless=new")
        
        # Prefs for additional stealth
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1,
            "profile.password_manager_enabled": False,
            "credentials_enable_service": False,
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.media_stream_camera": 2,
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_setting_values.desktop_notifications": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        # Exclude automation switches
        # options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        # options.add_experimental_option('useAutomationExtension', False)
        
        return options
    
    def create_stealth_driver(self, profile_name: str = "stealth_default", 
                             headless: bool = False, 
                             use_undetected: bool = True) -> webdriver.Chrome:
        """
        Create a Chrome driver configured for stealth mode
        
        Args:
            profile_name: Name of the profile to use
            headless: Whether to run in headless mode
            use_undetected: Whether to use undetected-chromedriver
            
        Returns:
            Configured Chrome WebDriver
        """
        try:
            if use_undetected:
                # Use undetected-chromedriver for maximum stealth
                options = self.get_stealth_options(profile_name, headless)

                # Set binary location if portable Chrome is available
                chrome_path = self.get_chrome_portable_path()
                if chrome_path:
                    options.binary_location = str(chrome_path)

                # Create undetected Chrome driver
                driver = uc.Chrome(options=options, version_main=None)

                # Apply additional stealth JavaScript
                self.apply_stealth_javascript(driver)

            else:
                # Use regular selenium with stealth options
                options = self.get_stealth_options(profile_name, headless)

                # Set binary location if portable Chrome is available
                chrome_path = self.get_chrome_portable_path()
                if chrome_path:
                    options.binary_location = str(chrome_path)

                # Get ChromeDriver
                driver_path = self.get_chromedriver_path()
                service = Service(driver_path)
                
                driver = webdriver.Chrome(service=service, options=options)
            
            # Apply additional stealth JavaScript
            try:
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as e:
                logger.warning(f"Could not redefine webdriver property: {e}")
            
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                "source": """
                    try {
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                    } catch (e) {}
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    window.chrome = {
                        runtime: {}
                    };
                """
            })
            
            logger.info("Stealth Chrome driver created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create stealth driver: {e}")
            raise
    
    def apply_stealth_javascript(self, driver):
        """
        Apply additional JavaScript for stealth mode
        
        Args:
            driver: WebDriver instance
        """
        try:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            logger.warning(f"Could not redefine webdriver property: {e}")
        
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": """
                try {
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                } catch (e) {}
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                window.chrome = {
                    runtime: {}
                };
            """
        })
    
    def download_chrome_portable(self, force_download: bool = False) -> bool:
        """
        Download Chrome Portable (placeholder - manual download recommended)
        
        Args:
            force_download: Force download even if already exists
            
        Returns:
            True if successful, False otherwise
        """
        chrome_path = self.get_chrome_portable_path()
        if chrome_path and not force_download:
            logger.info("Chrome Portable already available")
            return True
        
        logger.info("Chrome Portable download not implemented - please download manually")
        logger.info(f"Please download Chrome Portable and extract to: {self.chrome_dir}")
        logger.info("Download from: https://portableapps.com/apps/internet/google_chrome_portable")
        
        return False
    
    def download_chromedriver(self, force_download: bool = False) -> bool:
        """
        Download ChromeDriver to portable directory
        
        Args:
            force_download: Force download even if already exists
            
        Returns:
            True if successful, False otherwise
        """
        driver_path = self.drivers_dir / "chromedriver.exe"
        if driver_path.exists() and not force_download:
            logger.info("ChromeDriver already available")
            return True
        
        try:
            # Use webdriver-manager to download and copy to portable directory
            managed_driver = ChromeDriverManager().install()
            
            import shutil
            shutil.copy2(managed_driver, driver_path)
            
            logger.info(f"ChromeDriver downloaded to: {driver_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download ChromeDriver: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status of portable browser setup
        
        Returns:
            Dictionary with setup status information
        """
        chrome_path = self.get_chrome_portable_path()
        
        status = {
            "base_dir": str(self.base_dir),
            "chrome_available": chrome_path is not None,
            "chrome_path": str(chrome_path) if chrome_path else None,
            "profiles_dir": str(self.profiles_dir),
            "drivers_dir": str(self.drivers_dir),
            "chromedriver_available": (self.drivers_dir / "chromedriver.exe").exists(),
            "profiles": [p.name for p in self.profiles_dir.iterdir() if p.is_dir()]
        }
        
        return status

    def apply_stealth_javascript(self, driver):
        """
        Apply stealth JavaScript to make browser less detectable
        
        Args:
            driver: Chrome WebDriver instance
        """
        try:
            # Remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Mock languages and plugins
            driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            # Mock permissions
            driver.execute_script("""
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
            """)
            
            logger.info("Stealth JavaScript applied successfully")
            
        except Exception as e:
            logger.warning(f"Failed to apply stealth JavaScript: {e}")
