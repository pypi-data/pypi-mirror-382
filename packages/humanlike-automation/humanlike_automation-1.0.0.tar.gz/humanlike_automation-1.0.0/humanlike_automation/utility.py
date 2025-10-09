import os
import logging
import linecache
import sys
import requests
import subprocess
import pyperclip


class CustomLogger:
    @staticmethod
    def get_logger(name: str):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        if not logger.hasHandlers():
            log_dir = os.path.join(os.getcwd(), 'logs', name)
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f"{name}.log")
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
            file_handler.setFormatter(file_formatter)
            
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
            console_handler.setFormatter(console_formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger

class Utility:
    def __init__(self):
        self.logger = CustomLogger.get_logger('Utility')
        
    def print_exception(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        self.logger.error(f'EXCEPTION IN ({filename}, LINE {lineno} "{line.strip()}"): {exc_obj}')
    
    def run_script(self, script_path):
        lock_file = script_path + ".lock"
        if os.path.isfile(lock_file):
            self.logger.warning(f"Script {script_path} is already running.")
            return True
        open(lock_file, 'w').close()
        try:
            subprocess.run(["python", script_path])
        finally:
            os.remove(lock_file)
        

    def save_data(self, data, file_name, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, file_name)
        with open(file_path, "w") as f:
            f.write(data)
        self.logger.info(f"Data saved to {file_path}")

    def read_data(self, file_name, directory):
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read()
        else:
            self.logger.warning(f"{file_path} does not exist.")
            return None

    def copy_to_clipboard(self, text):
        try:
            pyperclip.copy(text)
            self.logger.info("Text copied to clipboard.")
        except Exception as e:
            self.logger.error(f"An error occurred while copying text to clipboard: {e}")

    def paste_from_clipboard(self):
        try:
            return pyperclip.paste()
        except Exception as e:
            self.logger.error(f"An error occurred while pasting text from clipboard: {e}")
            return None
