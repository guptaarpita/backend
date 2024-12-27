from django.db import connections
from django.conf import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Database connection configuration
def get_database_connection():
    try:
        connection = connections['default']
        if not connection.is_usable():
            connection.connect()
        logger.info("Connected to the database")
        return connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
