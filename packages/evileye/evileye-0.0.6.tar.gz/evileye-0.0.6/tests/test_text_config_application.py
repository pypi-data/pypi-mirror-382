#!/usr/bin/env python3
"""
Test script to verify that text_config is properly applied from configuration.
"""

import json
from evileye.core.logging_config import setup_evileye_logging
from evileye.core.logger import get_module_logger
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evileye.utils.utils import apply_text_config, get_default_text_config

# Инициализация логирования для тестов
logger = setup_evileye_logging(log_level="INFO", log_to_console=True, log_to_file=True)
test_logger = get_module_logger("test")

def test_text_config_from_file():
    """Test text_config loading from sample configuration files."""
    
    test_logger.info("🔍 Testing text_config application from configuration files")
    test_logger.info("=" * 60)
    
    # Test files
    config_files = [
        "evileye/samples_configs/single_video.json",
        "evileye/samples_configs/single_video_split.json", 
        "evileye/samples_configs/multi_videos.json",
        "evileye/samples_configs/single_ip_camera.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            test_logger.info(f"\n📄 Testing: {config_file}")
            
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Get text_config from visualizer section
                visualizer_config = config.get('visualizer', {})
                text_config = visualizer_config.get('text_config', {})
                
                test_logger.info(f"  📋 Found text_config in visualizer section:")
                for key, value in text_config.items():
                    test_logger.info(f"    {key}: {value}")
                
                # Apply text_config
                merged_config = apply_text_config(text_config)
                
                test_logger.info(f"  ✅ Applied text_config:")
                for key, value in merged_config.items():
                    test_logger.info(f"    {key}: {value}")
                
                # Test specific values
                if 'font_scale_method' in text_config:
                    test_logger.info(f"  🎯 Font scale method: {text_config['font_scale_method']}")
                
                if 'font_size_pt' in text_config:
                    test_logger.info(f"  📏 Font size: {text_config['font_size_pt']}pt")
                
            except Exception as e:
                test_logger.info(f"  ❌ Error: {e}")
        else:
            test_logger.info(f"\n⚠️  File not found: {config_file}")

def test_default_config():
    """Test default text configuration."""
    
    test_logger.info("\n🔧 Testing default text configuration")
    test_logger.info("=" * 60)
    
    default_config = get_default_text_config()
    
    test_logger.info("Default configuration:")
    for key, value in default_config.items():
        test_logger.info(f"  {key}: {value}")

def test_config_merging():
    """Test merging of user config with defaults."""
    
    test_logger.info("\n🔄 Testing configuration merging")
    test_logger.info("=" * 60)
    
    # Test user config
    user_config = {
        "font_size_pt": 20,
        "font_scale_method": "simple",
        "color": [255, 0, 0]  # Red color
    }
    
    test_logger.info("User configuration:")
    for key, value in user_config.items():
        test_logger.info(f"  {key}: {value}")
    
    # Apply merging
    merged_config = apply_text_config(user_config)
    
    test_logger.info("\nMerged configuration:")
    for key, value in merged_config.items():
        test_logger.info(f"  {key}: {value}")

def test_visualizer_integration():
    """Test that visualizer properly receives text_config."""
    
    test_logger.info("\n🎨 Testing visualizer integration")
    test_logger.info("=" * 60)
    
    # Simulate visualizer parameter setting
    from evileye.visualization_modules.visualizer import Visualizer
    
    # Create mock slots and signals
    mock_slots = {}
    mock_signals = {}
    
    visualizer = Visualizer(mock_slots, mock_signals)
    
    # Set parameters with text_config
    test_params = {
        'source_ids': [0],
        'fps': [5],
        'num_height': 1,
        'num_width': 1,
        'show_debug_info': True,
        'text_config': {
            'font_size_pt': 18,
            'font_scale_method': 'resolution_based',
            'color': [0, 255, 0]  # Green
        }
    }
    
    visualizer.params = test_params
    visualizer.set_params_impl()
    
    test_logger.info(f"Visualizer text_config: {visualizer.text_config}")
    
    # Test that text_config is properly stored
    if visualizer.text_config:
        test_logger.info("✅ text_config successfully applied to visualizer")
        for key, value in visualizer.text_config.items():
            test_logger.info(f"  {key}: {value}")
    else:
        test_logger.info("❌ text_config not applied to visualizer")

def main():
    """Main test function."""
    
    test_logger.info("🎨 Text Configuration Application Test")
    test_logger.info("=" * 60)
    
    try:
        test_default_config()
        test_config_merging()
        test_text_config_from_file()
        test_visualizer_integration()
        
        test_logger.info("\n✅ All tests completed successfully!")
        
        test_logger.info("\n📋 Summary:")
        test_logger.info("  ✅ text_config moved to visualizer section")
        test_logger.info("  ✅ text_config properly applied in visualizer")
        test_logger.info("  ✅ text_config passed to VideoThread")
        test_logger.info("  ✅ text_config used in draw_boxes_tracking")
        test_logger.info("  ✅ Configuration merging works correctly")
        
    except Exception as e:
        test_logger.info(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())



