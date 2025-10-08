#!/usr/bin/env python3

import sys
import os
from evileye.core.logging_config import setup_evileye_logging
from evileye.core.logger import get_module_logger
sys.path.append('.')

# Инициализация логирования для тестов
logger = setup_evileye_logging(log_level="INFO", log_to_console=True, log_to_file=True)
test_logger = get_module_logger("test")

def test_data_source():
    """Test data source functionality"""
    
    test_logger.info("=== Test Data Source ===")
    
    try:
        from evileye.visualization_modules.journal_data_source_json import JsonLabelJournalDataSource
        
        # Create data source
        base_dir = "EvilEyeData"
        ds = JsonLabelJournalDataSource(base_dir)
        
        test_logger.info(f"✅ Data source created with base_dir: {base_dir}")
        
        # Test available dates
        dates = ds.list_available_dates()
        test_logger.info(f"📅 Available dates: {dates}")
        
        # Test fetching data
        if dates:
            # Use first available date
            test_date = dates[0]
            test_logger.info(f"📊 Testing with date: {test_date}")
            
            ds.set_date(test_date)
            data = ds.fetch(0, 10, {}, [])
            test_logger.info(f"📈 Fetched {len(data)} records")
            
            if data:
                test_logger.info("📋 Sample data:")
                for i, record in enumerate(data[:3]):
                    test_logger.info(f"  Record {i+1}: {record}")
            else:
                test_logger.info("❌ No data found")
        else:
            test_logger.info("❌ No dates available")
            
        # Test without date filter
        test_logger.info("\n--- Testing without date filter ---")
        ds.set_date(None)
        data = ds.fetch(0, 10, {}, [])
        test_logger.info(f"📈 Fetched {len(data)} records (no date filter)")
        
        if data:
            test_logger.info("📋 Sample data:")
            for i, record in enumerate(data[:3]):
                test_logger.info(f"  Record {i+1}: {record}")
        else:
            test_logger.info("❌ No data found without date filter")
            
    except Exception as e:
        test_logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_source()
