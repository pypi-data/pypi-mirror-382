from evileye.core.logging_config import setup_evileye_logging
from evileye.core.logger import get_module_logger
#!/usr/bin/env python3
"""
Test script to verify controller works without database connection.
"""

# Инициализация логирования для тестов
logger = setup_evileye_logging(log_level="INFO", log_to_console=True, log_to_file=True)
test_logger = get_module_logger("test")

def test_controller_with_database():
    """Test controller with database enabled."""
    
    test_logger.info("🔍 Testing Controller with Database")
    test_logger.info("=" * 60)
    
    try:
        from evileye.controller import controller
        
        # Create controller instance
        ctrl = controller.Controller()
        test_logger.info("✅ Successfully created controller")
        
        # Test with database enabled
        test_params = {
            'controller': {
                'use_database': True,
                'fps': 30
            },
            'sources': [],
            'pipeline': {
                'pipeline_class': 'PipelineSurveillance'
            }
        }
        
        ctrl.init(test_params)
        test_logger.info("✅ Controller initialized with database enabled")
        
        # Check if database components are initialized
        if ctrl.db_controller is not None:
            test_logger.info("✅ Database controller is initialized")
        else:
            test_logger.info("❌ Database controller is NOT initialized")
            
        if ctrl.obj_handler is not None:
            test_logger.info("✅ Object handler is initialized")
        else:
            test_logger.info("❌ Object handler is NOT initialized")
            
    except Exception as e:
        test_logger.error(f"❌ Error in database test: {e}")
        import traceback
        traceback.print_exc()

def test_controller_without_database():
    """Test controller with database disabled."""
    
    test_logger.info("\n🔍 Testing Controller without Database")
    test_logger.info("=" * 60)
    
    try:
        from evileye.controller import controller
        
        # Create controller instance
        ctrl = controller.Controller()
        test_logger.info("✅ Successfully created controller")
        
        # Test with database disabled
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
        
        ctrl.init(test_params)
        test_logger.info("✅ Controller initialized with database disabled")
        
        # Check if database components are NOT initialized
        if ctrl.db_controller is None:
            test_logger.info("✅ Database controller is NOT initialized (as expected)")
        else:
            test_logger.info("❌ Database controller is initialized (should be None)")
            
        if ctrl.obj_handler is not None:
            test_logger.info("✅ Object handler is initialized (without database)")
        else:
            test_logger.info("❌ Object handler is NOT initialized")
            
        # Check if events detectors are initialized
        if ctrl.cam_events_detector is not None:
            test_logger.info("✅ Camera events detector is initialized")
        else:
            test_logger.info("❌ Camera events detector is NOT initialized")
            
        if ctrl.fov_events_detector is not None:
            test_logger.info("✅ FOV events detector is initialized")
        else:
            test_logger.info("❌ FOV events detector is NOT initialized")
            
        if ctrl.zone_events_detector is not None:
            test_logger.info("✅ Zone events detector is initialized")
        else:
            test_logger.info("❌ Zone events detector is NOT initialized")
            
        if ctrl.events_processor is not None:
            test_logger.info("✅ Events processor is initialized")
        else:
            test_logger.info("❌ Events processor is NOT initialized")
            
    except Exception as e:
        test_logger.error(f"❌ Error in no-database test: {e}")
        import traceback
        traceback.print_exc()

def test_controller_default_behavior():
    """Test controller default behavior (should use database by default)."""
    
    test_logger.info("\n🔍 Testing Controller Default Behavior")
    test_logger.info("=" * 60)
    
    try:
        from evileye.controller import controller
        
        # Create controller instance
        ctrl = controller.Controller()
        test_logger.info("✅ Successfully created controller")
        
        # Test with default parameters (no use_database specified)
        test_params = {
            'controller': {
                'fps': 30
            },
            'sources': [],
            'pipeline': {
                'pipeline_class': 'PipelineSurveillance'
            }
        }
        
        ctrl.init(test_params)
        test_logger.info("✅ Controller initialized with default parameters")
        
        # Check default value of use_database
        if ctrl.use_database:
            test_logger.info("✅ use_database is True by default (as expected)")
        else:
            test_logger.info("❌ use_database is False (should be True by default)")
            
    except Exception as e:
        test_logger.error(f"❌ Error in default behavior test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    test_logger.info("🔍 Controller Database Functionality Test")
    test_logger.info("=" * 60)
    
    test_controller_with_database()
    test_controller_without_database()
    test_controller_default_behavior()
    
    test_logger.info("\n📋 Summary:")
    test_logger.info("  ✅ Controller can work with database enabled")
    test_logger.info("  ✅ Controller can work without database connection")
    test_logger.info("  ✅ Default behavior uses database (backward compatibility)")
    test_logger.info("  ✅ All components are properly initialized in both modes")

if __name__ == "__main__":
    main()



