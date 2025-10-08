#!/usr/bin/env python3
"""
EvilEye Configuration Creator

This script creates new configuration files for the EvilEye surveillance system.
"""

import argparse
import json
import sys
import os
from pathlib import Path

from evileye.utils.utils import normalize_config_path
from evileye.core.logging_config import setup_evileye_logging
from evileye.core.logger import get_module_logger

# Add project root to path for imports when running as script
sys.path.insert(0, str(Path(__file__).parent.parent))

# Инициализация логирования
logger = setup_evileye_logging(log_level="INFO", log_to_console=True, log_to_file=True)
create_logger = get_module_logger("create")

from evileye.controller import controller


def create_args_parser():
    """Create argument parser for the create script"""
    parser = argparse.ArgumentParser(
        description="Create new EvilEye configuration file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  evileye-create my_config                    # Create configs/my_config.json
  evileye-create configs/custom.json          # Create specific path
  evileye-create --sources 2                  # Create config with 2 sources
  evileye-create --pipeline PipelineSurveillance  # Use specific pipeline
  evileye-create --source-type video_file     # Set source type for all sources
  evileye-create --list-pipelines             # List available pipeline classes
        """
    )
    
    parser.add_argument(
        'config_name',
        nargs='?',
        type=str,
        help="Name of the configuration file (without .json extension)"
    )
    
    parser.add_argument(
        '--sources',
        type=int,
        default=0,
        help="Number of video sources to include in the configuration (default: 0)"
    )
    
    parser.add_argument(
        '--pipeline',
        type=str,
        default='PipelineSurveillance',
        help="Pipeline class name to use (default: PipelineSurveillance)"
    )
    
    parser.add_argument(
        '--source-type',
        choices=['video_file', 'ip_camera', 'device'],
        default='video_file',
        help="Source type for all sources (default: video_file)"
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='configs',
        help="Output directory for configuration files (default: configs)"
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help="Overwrite existing configuration file"
    )
    
    parser.add_argument(
        '--list-pipelines',
        action='store_true',
        help="List available pipeline classes"
    )
    
    return parser


def list_pipeline_classes():
    """List available pipeline classes"""
    try:
        controller_instance = controller.Controller()
        pipeline_classes = controller_instance.get_available_pipeline_classes()
        
        if not pipeline_classes:
            create_logger.info("No pipeline classes found.")
            return
        
        create_logger.info("Available pipeline classes:")
        create_logger.info("=" * 40)
        for i, class_name in enumerate(pipeline_classes, 1):
            create_logger.info(f"{i}. {class_name}")
        
        create_logger.info(f"\nTotal: {len(pipeline_classes)} pipeline class(es)")
        create_logger.info("\nUse --pipeline <class_name> to specify a pipeline when creating a configuration.")
        
    except Exception as e:
        create_logger.info(f"Error listing pipeline classes: {e}")


def create_config_file(config_name, sources=0, pipeline_class='PipelineSurveillance', 
                      source_type='video_file', output_dir='configs', force=False):
    """Create a new configuration file"""
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine output file path
    if config_name is None:
        config_name = f"new_config_{pipeline_class}"
    
    if not config_name.endswith('.json'):
        config_name += '.json'
    
    # For output directory, we don't want to normalize if it's already "configs"
    if output_dir == "configs":
        output_path = os.path.join(output_dir, config_name)
    else:
        # Normalize output directory path for other directories
        normalized_output_dir = normalize_config_path(output_dir)
        output_path = os.path.join(normalized_output_dir, config_name)
    
    # Check if file already exists
    if os.path.exists(output_path) and not force:
        create_logger.info(f"Configuration file '{output_path}' already exists!")
        create_logger.info(f"   Use --force to overwrite or choose a different name.")
        return False
    
    # Create controller instance and generate configuration
    create_logger.info(f"Creating configuration:")
    create_logger.info(f"   Pipeline: {pipeline_class}")
    create_logger.info(f"   Sources: {sources}")
    create_logger.info(f"   Source type: {source_type}")
    create_logger.info(f"   Output: {output_path}")
    
    try:
        controller_instance = controller.Controller()
        config_data = controller_instance.create_config(num_sources=sources, pipeline_class=pipeline_class)

        # Write configuration to file
        with open(output_path, 'w') as f:
            json.dump(config_data, f, indent=4)
        
        create_logger.info(f"Configuration created successfully!")
        create_logger.info(f"   File: {output_path}")
        create_logger.info(f"   Size: {os.path.getsize(output_path)} bytes")
        
        return True
        
    except Exception as e:
        create_logger.info(f"Error creating configuration: {e}")
        return False


def main():
    """Main entry point for the configuration creator"""
    parser = create_args_parser()
    args = parser.parse_args()
    
    # Handle list pipelines
    if args.list_pipelines:
        list_pipeline_classes()
        return 0
    
    # Validate arguments
    if args.config_name is None:
        create_logger.info("Configuration name is required!")
        create_logger.info("   Usage: evileye-create <config_name>")
        create_logger.info("   Use --help for more information.")
        return 1
    
    # Create configuration
    success = create_config_file(
        config_name=args.config_name,
        sources=args.sources,
        pipeline_class=args.pipeline,
        source_type=args.source_type,
        output_dir=args.output_dir,
        force=args.force
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
