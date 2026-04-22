"""
Centralized logging configuration untuk BeasiswaKu

Modul ini menghandle semua setup logging di aplikasi.
Semua modul lain hanya perlu: logger = logging.getLogger(__name__)

Penggunaan:
    from src.core.logging_config import setup_logging
    setup_logging()  # Call sekali di startup (misal di main.py)
"""

import logging
import os
from datetime import datetime


# Folder untuk log files
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Format untuk logging
LOG_FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_level=logging.INFO, log_file=True):
    """
    Centralized logging setup untuk seluruh aplikasi
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Apakah output ke file (default: True)
    
    Behavior:
        - Console handler: log ke terminal
        - File handler (optional): log ke file dengan timestamp
        - Format: [YYYY-MM-DD HH:MM:SS] [module_name] [LEVEL] message
        - Level: DEBUG untuk file, INFO untuk console (default)
    
    Usage:
        # Di main.py atau startup module:
        from src.core.logging_config import setup_logging
        setup_logging()  # Call sekali di awal
        
        # Di semua modul lain:
        import logging
        logger = logging.getLogger(__name__)
    
    Notes:
        - Function ini idempotent - aman dipanggil berkali-kali
        - Setelah dijalankan, semua logger akan menggunakan configuration ini
        - Hindari logging.basicConfig() di modul lain (conflict dengan setup ini)
    """
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Jika sudah punya handlers, clear dulu (prevent duplicate)
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    # Set root level
    root_logger.setLevel(logging.DEBUG)  # Capture all, filter di handler
    
    # ===== Console Handler =====
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)  # Default: INFO
    console_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # ===== File Handler (optional) =====
    if log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(LOG_DIR, f"beasiswaku_{timestamp}.log")
        
        try:
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)  # File captures DEBUG dan lebih
            file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
            
            console_logger = logging.getLogger(__name__)
            console_logger.info(f"📁 Logging to file: {log_file_path}")
        
        except IOError as e:
            console_logger = logging.getLogger(__name__)
            console_logger.warning(f"⚠️ Could not create log file: {str(e)}")
    
    return root_logger


def get_logger(name):
    """
    Convenience function untuk get logger dengan nama module
    
    Usage:
        logger = get_logger(__name__)
    
    Return:
        logging.Logger instance
    """
    return logging.getLogger(name)
