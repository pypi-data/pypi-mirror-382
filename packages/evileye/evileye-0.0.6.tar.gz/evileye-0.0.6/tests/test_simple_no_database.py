from evileye.core.logging_config import setup_evileye_logging
from evileye.core.logger import get_module_logger
#!/usr/bin/env python3
"""
Simple test to verify basic controller functionality without database.
"""

# Инициализация логирования для тестов
logger = setup_evileye_logging(log_level="INFO", log_to_console=True, log_to_file=True)
test_logger = get_module_logger("test")

def test_basic_controller():
    """Test basic controller creation and initialization."""
    
    test_logger.info("🔍 Testing Basic Controller")
    test_logger.info("=" * 60)
    
    try:
        from evileye.controller import controller
        test_logger.info("✅ Successfully imported controller")
        
        # Create controller instance
        ctrl = controller.Controller()
        test_logger.info("✅ Successfully created controller")
        
        # Check default value
        test_logger.info(f"use_database default value: {ctrl.use_database}")
        
        # Test minimal initialization
        test_params = {
            'controller': {
                'use_database': False,
                'fps': 30
            },
            'sources': [],
            'pipeline': {
                'pipeline_class': 'PipelineSurveillance'
            }
        }
        
        test_logger.info("Attempting to initialize controller...")
        ctrl.init(test_params)
        test_logger.info("✅ Controller initialized successfully")
        
        test_logger.info(f"use_database after init: {ctrl.use_database}")
        test_logger.info(f"db_controller: {ctrl.db_controller}")
        test_logger.info(f"obj_handler: {ctrl.obj_handler is not None}")
        
    except Exception as e:
        test_logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_controller()



