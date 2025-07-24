from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator, AnyHttpUrl
from typing import List, Union

class Settings(BaseSettings):
    """
    Application settings and configuration.
    
    This class defines all configuration parameters for the application.
    Values are loaded from environment variables or .env file, with defaults provided.
    """
    # Core application settings
    PROJECT_NAME: str = "My Project"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # CORS settings (for future use)
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = []
    
    # Security settings (for future use)
    SECRET_KEY: str = "changethisinproduction"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """
        Validate that the database URL is properly formatted.
        
        Args:
            v: The database URL to validate
            
        Returns:
            The validated database URL
            
        Raises:
            ValueError: If the database URL is empty or invalid
        """
        if not v or not v.strip():
            raise ValueError('DATABASE_URL cannot be empty')
        
        # Basic validation for common database URL formats
        valid_prefixes = ['sqlite:///', 'postgresql://', 'mysql://', 'oracle://', 'mssql://']
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(
                'DATABASE_URL must start with a valid prefix: ' + 
                ', '.join(valid_prefixes)
            )
        
        return v
    
    @field_validator('BACKEND_CORS_ORIGINS')
    @classmethod
    def validate_cors_origins(cls, v: List[Union[str, AnyHttpUrl]]) -> List[Union[str, AnyHttpUrl]]:
        """
        Validate that CORS origins are properly formatted.
        
        Args:
            v: List of CORS origins to validate
            
        Returns:
            The validated list of CORS origins
        """
        # If the list is empty, return it as is
        if not v:
            return v
            
        # Validate each origin in the list
        validated_origins = []
        for origin in v:
            # AnyHttpUrl objects are already validated by Pydantic
            if isinstance(origin, AnyHttpUrl):
                validated_origins.append(origin)
            elif isinstance(origin, str):
                # Validate string origins
                if origin.startswith("http://") or origin.startswith("https://"):
                    validated_origins.append(origin)
                else:
                    raise ValueError(f"Invalid CORS origin: {origin}. Origins must start with http:// or https://")
            else:
                raise ValueError(f"Invalid CORS origin type: {type(origin)}. Must be string or AnyHttpUrl")
                
        return validated_origins
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )

# Create a global instance
settings = Settings()