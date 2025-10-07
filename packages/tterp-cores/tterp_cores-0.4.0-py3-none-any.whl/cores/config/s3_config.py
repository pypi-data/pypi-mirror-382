from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Config(BaseSettings):
    """S3 Configuration settings."""
    
    S3_URL: str | None = None
    S3_REGION: str | None = None
    
    # TVS config
    S3_TVS_ACCESS_KEY: str | None = None
    S3_TVS_SECRET_KEY: str | None = None
    S3_TVS_BUCKET_NAME: str | None = None
    S3_TVS_ENDPOINT_URL: str | None = None
    
    # S3 Logging configuration
    S3_LOG_LEVEL: str = "DEBUG"
    S3_LOG_ENABLED: bool = True
    S3_LOG_MAX_SIZE: int = 10485760  # 10MB
    S3_LOG_BACKUP_COUNT: int = 5
    S3_LOG_OPERATIONS: bool = True  # Log all S3 operations
    S3_LOG_PERFORMANCE: bool = True  # Log performance metrics
    S3_LOG_ERRORS_ONLY: bool = False  # Only log errors (overrides other settings)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def should_log_operation(self, operation_type: str = "info") -> bool:
        """
        Determine if an operation should be logged based on configuration.
        
        Args:
            operation_type: Type of operation (info, error, debug, success)
            
        Returns:
            bool: True if should log
        """
        if not self.S3_LOG_ENABLED:
            return False
            
        if self.S3_LOG_ERRORS_ONLY and operation_type not in ["error", "warning"]:
            return False
            
        return True


s3_config = S3Config()
