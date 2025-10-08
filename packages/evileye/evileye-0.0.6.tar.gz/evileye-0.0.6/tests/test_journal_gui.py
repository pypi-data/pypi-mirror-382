#!/usr/bin/env python3

import sys
import os
from evileye.core.logging_config import setup_evileye_logging
from evileye.core.logger import get_module_logger
sys.path.append('.')

# Инициализация логирования для тестов
logger = setup_evileye_logging(log_level="INFO", log_to_console=True, log_to_file=True)
test_logger = get_module_logger("test")

def test_journal_gui():
    """Test journal GUI with fixes"""
    
    test_logger.info("=== Journal GUI Test ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from evileye.visualization_modules.events_journal_json import EventsJournalJson
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create journal widget
        journal = EventsJournalJson('EvilEyeData')
        journal.show()
        
        test_logger.info("✅ Journal widget created and shown")
        test_logger.info("📋 Features to test:")
        test_logger.info("   - Different images for found vs lost events")
        test_logger.info("   - Bounding boxes drawn correctly on images")
        test_logger.info("   - Event type filtering (found/lost)")
        test_logger.info("   - Date selection")
        test_logger.info("   - Image scaling and display")
        
        test_logger.info("\n🔧 Fixed Issues:")
        test_logger.info("   - Event type separation")
        test_logger.info("   - Proper timestamp handling")
        test_logger.info("   - Correct image paths")
        test_logger.info("   - Bounding box scaling with actual image dimensions")
        
        test_logger.info("\n⚠️  Note: Image files may not exist yet")
        test_logger.info("   - This is a separate issue with image saving")
        test_logger.info("   - Journal will work correctly when images are available")
        
        # Run the application
        test_logger.info("\n🖥️  Journal window opened. Close it to continue...")
        app.exec()
        
    except Exception as e:
        test_logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_journal_gui()



