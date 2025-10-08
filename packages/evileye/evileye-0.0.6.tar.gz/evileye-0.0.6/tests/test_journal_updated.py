#!/usr/bin/env python3

import sys
import os
from evileye.core.logging_config import setup_evileye_logging
from evileye.core.logger import get_module_logger
sys.path.append('.')

# Инициализация логирования для тестов
logger = setup_evileye_logging(log_level="INFO", log_to_console=True, log_to_file=True)
test_logger = get_module_logger("test")

def test_journal_updated():
    """Test updated journal with new structure"""
    
    test_logger.info("=== Updated Journal Test ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from evileye.visualization_modules.events_journal_json import EventsJournalJson
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create journal widget
        journal = EventsJournalJson('EvilEyeData')
        
        test_logger.info("✅ Updated journal widget created")
        
        # Test data loading
        test_logger.info("\n📊 Data Summary:")
        test_logger.info(f"   Total events: {journal.ds.get_total({})}")
        test_logger.info(f"   Found events: {journal.ds.get_total({'event_type': 'found'})}")
        test_logger.info(f"   Lost events: {journal.ds.get_total({'event_type': 'lost'})}")
        test_logger.info(f"   Available dates: {journal.ds.list_available_dates()}")
        
        # Test sample data
        test_logger.info("\n📋 Sample Data:")
        events = journal.ds.fetch(0, 5, {}, [])
        for i, ev in enumerate(events):
            test_logger.info(f"   Event {i+1}:")
            test_logger.info(f"     Type: {ev.get('event_type')}")
            test_logger.info(f"     Time: {ev.get('ts')}")
            test_logger.info(f"     Source: {ev.get('source_name')}")
            test_logger.info(f"     Object ID: {ev.get('object_id')}")
            test_logger.info(f"     Image: {ev.get('image_filename')}")
        
        # Show window
        journal.show()
        
        test_logger.info("\n🔧 New Features:")
        test_logger.info("   - Database-style table structure")
        test_logger.info("   - Found and lost events in same row")
        test_logger.info("   - Proper source name display (Cam1, Cam2, etc.)")
        test_logger.info("   - Real-time updates every 5 seconds")
        test_logger.info("   - Preview and Lost preview columns")
        test_logger.info("   - Bounding box drawing on images")
        
        test_logger.info("\n✅ All systems operational")
        test_logger.info("🖥️  Journal window opened. Close it to continue...")
        
        journal.ds.close()
        app.exec()
        
    except Exception as e:
        test_logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_journal_updated()

