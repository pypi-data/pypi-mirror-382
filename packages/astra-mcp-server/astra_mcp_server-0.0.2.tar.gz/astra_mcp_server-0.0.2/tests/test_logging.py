#!/usr/bin/env python3
"""
Test script to verify logging configuration.
This script tests that logs go only to the file and stdout remains available.
"""

import sys
from logger import get_logger

def test_logging():
    """Test the logging configuration."""
    print("=== Testing Logging Configuration ===")
    print("This message should appear on stdout (not in log file)")
    
    # Get logger instance
    logger = get_logger("test_logger")
    
    # Test different log levels
    logger.debug("This is a DEBUG message - should go to logs/logs.log only")
    logger.info("This is an INFO message - should go to logs/logs.log only")
    logger.warning("This is a WARNING message - should go to logs/logs.log only")
    logger.error("This is an ERROR message - should go to logs/logs.log only")
    
    print("=== Test completed ===")
    print("Check logs/logs.log file to verify the log messages are there")
    print("This stdout message should NOT be in the log file")

if __name__ == "__main__":
    test_logging()
