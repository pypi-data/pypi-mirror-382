#!/usr/bin/env python3

import sys
import os
from evileye.core.logging_config import setup_evileye_logging
from evileye.core.logger import get_module_logger
sys.path.append('.')

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    pyqt_version = 6
except ImportError:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    pyqt_version = 5

from evileye.visualization_modules.events_journal_json import EventsJournalJson

# Инициализация логирования для тестов
logger = setup_evileye_logging(log_level="INFO", log_to_console=True, log_to_file=True)
test_logger = get_module_logger("test")

def test_json_journal():
    app = QApplication(sys.argv)
    
    # Test with existing data
    journal = EventsJournalJson('EvilEyeData')
    journal.show()
    
    test_logger.info("JSON Journal test window opened. Close it to continue.")
    
    # Run the application
    app.exec()

if __name__ == "__main__":
    test_json_journal()



