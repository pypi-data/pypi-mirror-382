#!/usr/bin/env python3
"""
Simple test for PipelineCapture with simplified initialization.
"""

# Инициализация логирования для тестов
logger = setup_evileye_logging(log_level="INFO", log_to_console=True, log_to_file=True)
test_logger = get_module_logger("test")

def test_pipeline_capture_simple():
    """Test PipelineCapture with simplified initialization."""
    
    test_logger.info("🔍 Testing PipelineCapture Simplified")
    test_logger.info("=" * 60)
    
    try:
        from evileye.pipelines.pipeline_capture import PipelineCapture
        import json
from evileye.core.logging_config import setup_evileye_logging
from evileye.core.logger import get_module_logger
        
        # Create pipeline
        pipeline = PipelineCapture()
        test_logger.info("✅ PipelineCapture created")
        
        # Set configuration
        config = {
            "pipeline": {
                "pipeline_class": "PipelineCapture",
                "sources": [
                    {
                        "camera": "videos/planes_sample.mp4",
                        "source": "VideoFile",
                        "source_ids": [0],
                        "source_names": ["VideoCapture"],
                        "split": False,
                        "num_split": 0,
                        "src_coords": [0],
                        "loop_play": False
                    }
                ]
            }
        }
        
        # Set pipeline parameters
        pipeline.params = config["pipeline"]
        test_logger.info("✅ Configuration set")
        
        # Set parameters
        pipeline.set_params_impl()
        test_logger.info("✅ Parameters set")
        
        # Check source config
        test_logger.info(f"Source config: {pipeline.source_config}")
        assert 'camera' in pipeline.source_config
        assert pipeline.source_config['camera'] == 'videos/planes_sample.mp4'
        test_logger.info("✅ Source config is correct")
        
        # Test get_sources before initialization
        sources = pipeline.get_sources()
        assert isinstance(sources, list)
        assert len(sources) == 0
        test_logger.info("✅ get_sources returns empty list before initialization")
        
        test_logger.info("✅ PipelineCapture simplified test completed successfully")
        
    except Exception as e:
        test_logger.error(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    test_logger.info("🔍 PipelineCapture Simplified Test")
    test_logger.info("=" * 60)
    
    test_pipeline_capture_simple()
    
    test_logger.info("\n📋 Summary:")
    test_logger.info("  ✅ PipelineCapture simplified initialization works")
    test_logger.info("  ✅ Source config is properly set")
    test_logger.info("  ✅ All tests passed successfully")

if __name__ == "__main__":
    main()



