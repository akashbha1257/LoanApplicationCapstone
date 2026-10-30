import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    # API Configuration
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    MODEL_ID = os.getenv('MODEL_ID', 'claude-opus-4-5-20251101-v1:0')  # Using available model

    # Database Configuration - Use SQLite for easier setup
    USE_SQLITE = True  # Switch to SQLite for easier local development

    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'loan_admin')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'secure_password_123')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'loan_application_db')

    # MCP Server Configuration
    MCP_HOST = os.getenv('MCP_HOST', 'localhost')
    MCP_PORT = int(os.getenv('MCP_PORT', 8080))

    # Application Configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Database connection string
    @property
    def DATABASE_URL(self):
        if self.USE_SQLITE:
            # Use SQLite database file in project directory
            db_path = Path(__file__).parent.parent.parent / "loan_app.db"
            return f"sqlite:///{db_path}"
        else:
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

config = Config()
