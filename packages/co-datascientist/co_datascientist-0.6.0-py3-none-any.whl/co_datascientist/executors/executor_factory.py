"""Factory for creating appropriate code executors based on configuration."""

import logging
from typing import Dict, Any

from .base_executor import BaseExecutor
from .local_executor import LocalExecutor
from .gcloud_executor import GCloudExecutor
from .databricks_executor import DatabricksExecutor
from .AWS_executer import AWSExecutor


class ExecutorFactory:
    """Factory class for creating appropriate code executors."""
    
    @staticmethod
    def create_executor(python_path: str = "python", config: Dict[str, Any] = None) -> BaseExecutor:
        """Create an appropriate executor based on the configuration.
        
        Args:
            python_path: Path to Python interpreter
            config: Configuration dictionary that may contain platform-specific settings
            
        Returns:
            BaseExecutor: An executor instance for the appropriate platform
        """
        if not config:
            return LocalExecutor(python_path, config)
        
        # Check for cloud platform configurations in priority order
        if config.get('aws'):
            logging.info("Creating AWS ECS executor")
            return AWSExecutor(python_path, config)

        if config.get('gcloud'):
            logging.info("Creating GCloud executor")
            return GCloudExecutor(python_path, config)

        if config.get('databricks'):
            logging.info("Creating Databricks executor")
            return DatabricksExecutor(python_path, config)

        # Default to local execution
        logging.info("Creating Local executor (default)")
        return LocalExecutor(python_path, config)
    
    @staticmethod
    def get_available_executors(python_path: str = "python", config: Dict[str, Any] = None) -> Dict[str, bool]:
        """Check which executors are available on this system.
        
        Args:
            python_path: Path to Python interpreter
            config: Configuration dictionary
            
        Returns:
            Dict mapping executor names to their availability status
        """
        executors = {
            'local': LocalExecutor(python_path, config),
            'aws': AWSExecutor(python_path, config),
            'gcloud': GCloudExecutor(python_path, config),
            'databricks': DatabricksExecutor(python_path, config)
        }
        
        return {name: executor.is_available() for name, executor in executors.items()}
