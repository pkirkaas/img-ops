#!/usr/bin/env python3
"""
Test script to demonstrate the app configuration functionality.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the src directory to the Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from img_ops.core import AppConfiguration, AppConfigManager, get_config_manager

def test_app_configuration():
  """Test the AppConfiguration class."""
  print("Testing AppConfiguration class:")
  print("=" * 50)
  
  # Test default configuration
  print("\n1. Creating default configuration:")
  config = AppConfiguration()
  print(f"   Name: {config.name}")
  print(f"   Description: {config.description}")
  print(f"   Paths: {config.paths}")
  print(f"   Method: {config.method}")
  print(f"   Percent: {config.percent}")
  
  # Test custom configuration
  print("\n2. Creating custom configuration:")
  custom_config = AppConfiguration(
    name="Photo Analysis",
    description="Configuration for analyzing family photos",
    paths=["/home/user/photos", "/home/user/vacation"],
    method="ssim",
    percent=85.5
  )
  print(f"   Name: {custom_config.name}")
  print(f"   Description: {custom_config.description}")
  print(f"   Paths: {custom_config.paths}")
  print(f"   Method: {custom_config.method}")
  print(f"   Percent: {custom_config.percent}")
  
  # Test path operations
  print("\n3. Testing path operations:")
  config.add_path("/test/path1")
  config.add_path("/test/path2")
  print(f"   After adding paths: {config.paths}")
  
  # Try adding duplicate
  duplicate_added = config.add_path("/test/path1")
  print(f"   Duplicate path added: {duplicate_added}")
  print(f"   Paths after duplicate attempt: {config.paths}")
  
  # Remove path
  removed = config.remove_path("/test/path1")
  print(f"   Path removed: {removed}")
  print(f"   Paths after removal: {config.paths}")
  
  # Clear all paths
  cleared_count = config.clear_paths()
  print(f"   Cleared {cleared_count} paths")
  print(f"   Paths after clearing: {config.paths}")

def test_app_config_manager():
  """Test the AppConfigManager class."""
  print("\n\nTesting AppConfigManager class:")
  print("=" * 50)
  
  # Create temporary config file for testing
  with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
    temp_config_path = temp_file.name
  
  try:
    # Test creating manager
    print("\n1. Creating configuration manager:")
    manager = AppConfigManager(config_file_path=temp_config_path)
    print(f"   Config file path: {manager.config_file_path}")
    print(f"   Initial configurations: {list(manager.configurations.keys())}")
    
    # Test adding configurations
    print("\n2. Adding configurations:")
    config1 = AppConfiguration(name="Config1", description="First config")
    config2 = AppConfiguration(name="Config2", description="Second config", method="orb")
    
    added1 = manager.add_configuration(config1)
    added2 = manager.add_configuration(config2)
    print(f"   Config1 added: {added1}")
    print(f"   Config2 added: {added2}")
    print(f"   Configuration names: {manager.list_configuration_names()}")
    
    # Test getting configuration
    print("\n3. Getting configurations:")
    retrieved_config = manager.get_configuration("Config1")
    print(f"   Retrieved Config1: {retrieved_config.name if retrieved_config else 'None'}")
    
    # Test get_or_create
    print("\n4. Testing get_or_create:")
    new_config = manager.get_or_create_configuration("Config3")
    print(f"   Created Config3: {new_config.name}")
    print(f"   Configuration names: {manager.list_configuration_names()}")
    
    # Test saving to file
    print("\n5. Testing file operations:")
    manager.save_to_file()
    print("   Configuration saved to file")
    
    # Create new manager and load from file
    manager2 = AppConfigManager(config_file_path=temp_config_path)
    print(f"   Loaded configurations: {manager2.list_configuration_names()}")
    
    # Verify loaded data
    loaded_config = manager2.get_configuration("Config2")
    if loaded_config:
      print(f"   Loaded Config2 method: {loaded_config.method}")
    
    # Test removing configuration
    print("\n6. Testing configuration removal:")
    removed = manager2.remove_configuration("Config1")
    print(f"   Config1 removed: {removed}")
    print(f"   Remaining configurations: {manager2.list_configuration_names()}")
    
  finally:
    # Clean up temporary file
    if os.path.exists(temp_config_path):
      os.unlink(temp_config_path)

def test_validation():
  """Test validation features."""
  print("\n\nTesting validation:")
  print("=" * 50)
  
  # Test invalid method
  print("\n1. Testing invalid method validation:")
  try:
    config = AppConfiguration(method="invalid_method")
    print("   ERROR: Should have raised validation error")
  except ValueError as e:
    print(f"   ✓ Validation error caught: {e}")
  
  # Test invalid percent
  print("\n2. Testing invalid percent validation:")
  try:
    config = AppConfiguration(percent=150)
    print("   ERROR: Should have raised validation error")
  except ValueError as e:
    print(f"   ✓ Validation error caught: {e}")
  
  # Test empty name
  print("\n3. Testing empty name validation:")
  try:
    config = AppConfiguration(name="")
    print("   ERROR: Should have raised validation error")
  except ValueError as e:
    print(f"   ✓ Validation error caught: {e}")
  
  # Test duplicate paths
  print("\n4. Testing duplicate path handling:")
  config = AppConfiguration(paths=["/path1", "/path2", "/path1", "/path3"])
  print(f"   Original paths with duplicates: ['/path1', '/path2', '/path1', '/path3']")
  print(f"   Cleaned paths: {config.paths}")

def test_global_config_manager():
  """Test the global configuration manager."""
  print("\n\nTesting global configuration manager:")
  print("=" * 50)
  
  # Get global manager
  manager1 = get_config_manager()
  manager2 = get_config_manager()
  
  print(f"   Same instance: {manager1 is manager2}")
  
  # Add a configuration to test persistence
  test_config = AppConfiguration(name="GlobalTest", description="Test global config")
  manager1.add_configuration(test_config)
  
  # Check if it's available in the second reference
  retrieved = manager2.get_configuration("GlobalTest")
  print(f"   Global config accessible: {retrieved is not None}")
  if retrieved:
    print(f"   Global config name: {retrieved.name}")

def main():
  """Run all tests."""
  print("App Configuration System Test")
  print("=" * 60)
  
  try:
    test_app_configuration()
    test_app_config_manager()
    test_validation()
    test_global_config_manager()
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    
  except Exception as e:
    print(f"\nTest failed with error: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
  main()