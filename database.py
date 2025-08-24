import psycopg2
import psycopg2.extras
import os
import hashlib
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager
import logging
import base64
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages PostgreSQL database connections and operations."""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'resume_processor'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'password')
        }
        # Initialize encryption key for API keys
        secret = os.getenv('API_CRYPTO_SECRET', 'dev-insecure-default')
        # Derive a Fernet key from the secret
        secret_bytes = secret.encode()
        derived_key = base64.urlsafe_b64encode(hashlib.sha256(secret_bytes).digest())
        self._fernet = Fernet(derived_key)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        email VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Create api_keys table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        api_key_hash VARCHAR(255) NOT NULL,
                        masked_key VARCHAR(50) NOT NULL,
                        api_key_encrypted TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)

                # Ensure api_key_encrypted column exists (for older DBs)
                try:
                    cursor.execute("""
                        ALTER TABLE api_keys
                        ADD COLUMN IF NOT EXISTS api_key_encrypted TEXT
                    """)
                except Exception as e:
                    logger.warning(f"Skipping api_key_encrypted column add: {e}")
                
                # Create user_sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        session_token VARCHAR(255) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Create processing_history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processing_history (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        filename VARCHAR(255) NOT NULL,
                        processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'completed',
                        metadata JSONB
                    )
                """)
                
                # Create processing_results table to store actual results
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processing_results (
                        id SERIAL PRIMARY KEY,
                        history_id INTEGER REFERENCES processing_history(id) ON DELETE CASCADE,
                        result_data JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create custom_prompts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custom_prompts (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        name VARCHAR(100) NOT NULL,
                        prompt_text TEXT NOT NULL,
                        is_default BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create token_usage table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS token_usage (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        processing_history_id INTEGER REFERENCES processing_history(id) ON DELETE CASCADE,
                        input_tokens INTEGER NOT NULL DEFAULT 0,
                        output_tokens INTEGER NOT NULL DEFAULT 0,
                        total_tokens INTEGER NOT NULL DEFAULT 0,
                        input_cost_usd DECIMAL(10, 6) NOT NULL DEFAULT 0,
                        output_cost_usd DECIMAL(10, 6) NOT NULL DEFAULT 0,
                        total_cost_usd DECIMAL(10, 6) NOT NULL DEFAULT 0,
                        model VARCHAR(50) NOT NULL DEFAULT 'gemini-2.5-flash',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Database tables initialized successfully")
    
    def user_exists(self, username: str) -> bool:
        """Check if a user exists by username."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                    return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking if user {username} exists: {e}")
            return False

    def create_user(self, username: str, password: str, email: str = None) -> bool:
        """Create a new user account."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, email)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (username, password_hash, email))
                    user_id = cursor.fetchone()[0]
                    conn.commit()
                    logger.info(f"User {username} created successfully with ID {user_id}")
                    return True
        except psycopg2.IntegrityError:
            logger.warning(f"Username {username} already exists")
            return False
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return False
    
    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials and return user info."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    cursor.execute("""
                        SELECT id, username, email, created_at, last_login
                        FROM users 
                        WHERE username = %s AND password_hash = %s AND is_active = TRUE
                    """, (username, password_hash))
                    user = cursor.fetchone()
                    
                    if user:
                        # Update last login
                        cursor.execute("""
                            UPDATE users SET last_login = CURRENT_TIMESTAMP
                            WHERE id = %s
                        """, (user['id'],))
                        conn.commit()
                        logger.info(f"User {username} logged in successfully")
                        return dict(user)
                    else:
                        logger.warning(f"Invalid login attempt for username: {username}")
                        return None
        except Exception as e:
            logger.error(f"Error verifying user {username}: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information by ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, username, email, created_at, last_login
                        FROM users 
                        WHERE id = %s AND is_active = TRUE
                    """, (user_id,))
                    user = cursor.fetchone()
                    return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def save_api_key(self, user_id: int, api_key: str) -> bool:
        """Save user's API key."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
                    # Encrypt API key for server-side usage
                    encrypted_bytes = self._fernet.encrypt(api_key.encode())
                    api_key_encrypted = encrypted_bytes.decode()
                    
                    # Deactivate existing API keys for this user
                    cursor.execute("""
                        UPDATE api_keys SET is_active = FALSE
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    # Insert new API key
                    cursor.execute("""
                        INSERT INTO api_keys (user_id, api_key_hash, masked_key, api_key_encrypted)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, api_key_hash, masked_key, api_key_encrypted))
                    
                    conn.commit()
                    logger.info(f"API key saved for user {user_id}")
                    return True
        except Exception as e:
            logger.error(f"Error saving API key for user {user_id}: {e}")
            return False
    
    def get_api_key(self, user_id: int) -> Optional[str]:
        """Get user's active API key hash."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT api_key_hash FROM api_keys
                        WHERE user_id = %s AND is_active = TRUE
                        ORDER BY created_at DESC
                        LIMIT 1
                    """, (user_id,))
                    result = cursor.fetchone()
                    return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting API key for user {user_id}: {e}")
            return None

    def get_api_key_plaintext(self, user_id: int) -> Optional[str]:
        """Get user's active API key in plaintext (server-side use only)."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT api_key_encrypted FROM api_keys
                        WHERE user_id = %s AND is_active = TRUE
                        ORDER BY created_at DESC
                        LIMIT 1
                    """, (user_id,))
                    result = cursor.fetchone()
                    if not result:
                        return None
                    encrypted = result[0]
                    if not encrypted:
                        return None
                    decrypted_bytes = self._fernet.decrypt(encrypted.encode())
                    return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Error decrypting API key for user {user_id}: {e}")
            return None
    
    def create_session(self, user_id: int, session_token: str, expires_in_hours: int = 24) -> bool:
        """Create a new user session."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO user_sessions (user_id, session_token, expires_at)
                        VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '%s hours')
                    """, (user_id, session_token, expires_in_hours))
                    conn.commit()
                    logger.info(f"Session created for user {user_id}")
                    return True
        except Exception as e:
            logger.error(f"Error creating session for user {user_id}: {e}")
            return False
    
    def validate_session(self, session_token: str) -> Optional[int]:
        """Validate session token and return user ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT user_id FROM user_sessions
                        WHERE session_token = %s AND expires_at > CURRENT_TIMESTAMP AND is_active = TRUE
                    """, (session_token,))
                    result = cursor.fetchone()
                    return result[0] if result else None
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None
    
    def delete_session(self, session_token: str) -> bool:
        """Delete a user session."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE user_sessions SET is_active = FALSE
                        WHERE session_token = %s
                    """, (session_token,))
                    conn.commit()
                    logger.info(f"Session {session_token} deleted")
                    return True
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    def save_processing_history(self, user_id: int, filename: str, metadata: Dict = None) -> Optional[int]:
        """Save processing history for a user and return the history ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO processing_history (user_id, filename, metadata)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (user_id, filename, psycopg2.extras.Json(metadata) if metadata else None))
                    history_id = cursor.fetchone()[0]
                    conn.commit()
                    logger.info(f"Processing history saved for user {user_id} with ID {history_id}")
                    return history_id
        except Exception as e:
            logger.error(f"Error saving processing history: {e}")
            return None
    
    def get_processing_history(self, user_id: int, limit: int = 10) -> list:
        """Get processing history for a user."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT ph.id, ph.filename, ph.processing_date, ph.status, ph.metadata
                        FROM processing_history ph
                        WHERE ph.user_id = %s
                        ORDER BY ph.processing_date DESC
                        LIMIT %s
                    """, (user_id, limit))
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting processing history: {e}")
            return []
    
    def save_processing_result(self, history_id: int, result_data: Dict[str, Any]) -> bool:
        """Save processing result data."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO processing_results (history_id, result_data)
                        VALUES (%s, %s)
                    """, (history_id, psycopg2.extras.Json(result_data)))
                    conn.commit()
                    logger.info(f"Processing result saved for history {history_id}")
                    return True
        except Exception as e:
            logger.error(f"Error saving processing result: {e}")
            return False
    
    def get_processing_result(self, history_id: int) -> Optional[Dict[str, Any]]:
        """Get processing result data by history ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT result_data, created_at
                        FROM processing_results
                        WHERE history_id = %s
                        ORDER BY created_at DESC
                        LIMIT 1
                    """, (history_id,))
                    result = cursor.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting processing result: {e}")
            return None
    
    def save_custom_prompt(self, user_id: int, name: str, prompt_text: str) -> bool:
        """Save a custom prompt for a user."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO custom_prompts (user_id, name, prompt_text)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (user_id, name, prompt_text))
                    prompt_id = cursor.fetchone()[0]
                    conn.commit()
                    logger.info(f"Custom prompt '{name}' saved for user {user_id}")
                    return True
        except Exception as e:
            logger.error(f"Error saving custom prompt: {e}")
            return False
    
    def get_custom_prompts(self, user_id: int) -> list:
        """Get all custom prompts for a user."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, name, prompt_text, is_default, created_at, updated_at
                        FROM custom_prompts
                        WHERE user_id = %s
                        ORDER BY created_at DESC
                    """, (user_id,))
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting custom prompts: {e}")
            return []
    
    def get_custom_prompt(self, prompt_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific custom prompt by ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, name, prompt_text, is_default, created_at, updated_at
                        FROM custom_prompts
                        WHERE id = %s
                    """, (prompt_id,))
                    result = cursor.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting custom prompt: {e}")
            return None
    
    def delete_custom_prompt(self, prompt_id: int, user_id: int) -> bool:
        """Delete a custom prompt."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM custom_prompts
                        WHERE id = %s AND user_id = %s
                    """, (prompt_id, user_id))
                    deleted_count = cursor.rowcount
                    conn.commit()
                    if deleted_count > 0:
                        logger.info(f"Custom prompt {prompt_id} deleted for user {user_id}")
                        return True
                    return False
        except Exception as e:
            logger.error(f"Error deleting custom prompt: {e}")
            return False
    
    def save_token_usage(self, user_id: int, processing_history_id: int, token_data: Dict[str, Any]) -> bool:
        """Save token usage data for a user."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO token_usage (
                            user_id, processing_history_id, input_tokens, output_tokens, 
                            total_tokens, input_cost_usd, output_cost_usd, total_cost_usd, model
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        user_id,
                        processing_history_id,
                        token_data.get('input_tokens', 0),
                        token_data.get('output_tokens', 0),
                        token_data.get('total_tokens', 0),
                        token_data.get('input_cost_usd', 0),
                        token_data.get('output_cost_usd', 0),
                        token_data.get('total_cost_usd', 0),
                        token_data.get('model', 'gemini-2.5-flash')
                    ))
                    conn.commit()
                    logger.info(f"Token usage saved for user {user_id}")
                    return True
        except Exception as e:
            logger.error(f"Error saving token usage: {e}")
            return False
    
    def get_user_token_usage(self, user_id: int, days: int = 30) -> list:
        """Get token usage for a user over the specified number of days."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            tu.*,
                            ph.filename,
                            ph.processing_date
                        FROM token_usage tu
                        JOIN processing_history ph ON tu.processing_history_id = ph.id
                        WHERE tu.user_id = %s 
                        AND tu.created_at >= CURRENT_DATE - INTERVAL '%s days'
                        ORDER BY tu.created_at DESC
                    """, (user_id, days))
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting user token usage: {e}")
            return []
    
    def get_user_token_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get token usage summary for a user over the specified number of days."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_requests,
                            SUM(input_tokens) as total_input_tokens,
                            SUM(output_tokens) as total_output_tokens,
                            SUM(total_tokens) as total_tokens,
                            SUM(input_cost_usd) as total_input_cost,
                            SUM(output_cost_usd) as total_output_cost,
                            SUM(total_cost_usd) as total_cost,
                            AVG(total_tokens) as avg_tokens_per_request,
                            AVG(total_cost_usd) as avg_cost_per_request
                        FROM token_usage
                        WHERE user_id = %s 
                        AND created_at >= CURRENT_DATE - INTERVAL '%s days'
                    """, (user_id, days))
                    result = cursor.fetchone()
                    return dict(result) if result else {
                        'total_requests': 0,
                        'total_input_tokens': 0,
                        'total_output_tokens': 0,
                        'total_tokens': 0,
                        'total_input_cost': 0,
                        'total_output_cost': 0,
                        'total_cost': 0,
                        'avg_tokens_per_request': 0,
                        'avg_cost_per_request': 0
                    }
        except Exception as e:
            logger.error(f"Error getting user token summary: {e}")
            return {
                'total_requests': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_tokens': 0,
                'total_input_cost': 0,
                'total_output_cost': 0,
                'total_cost': 0,
                'avg_tokens_per_request': 0,
                'avg_cost_per_request': 0
            }
    
    def get_token_usage_history(self, user_id: int, limit: int = 20) -> list:
        """Get token usage history for API endpoints."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            tu.*
                        FROM token_usage tu
                        WHERE tu.user_id = %s 
                        ORDER BY tu.created_at DESC
                        LIMIT %s
                    """, (user_id, limit))
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting token usage history: {e}")
            return []
    
    def get_token_usage_stats(self, user_id: int) -> Dict[str, Any]:
        """Get token usage statistics for dashboard."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            COUNT(DISTINCT ph.id) as total_sessions,
                            COALESCE(SUM(tu.total_tokens), 0) as total_tokens,
                            COALESCE(SUM(tu.total_cost_usd), 0) as total_cost,
                            COALESCE(AVG(tu.total_cost_usd), 0) as average_cost_per_session
                        FROM processing_history ph
                        LEFT JOIN token_usage tu ON ph.id = tu.processing_history_id
                        WHERE ph.user_id = %s
                    """, (user_id,))
                    result = cursor.fetchone()
                    if result:
                        return dict(result)
                    else:
                        return {
                            'total_sessions': 0,
                            'total_tokens': 0,
                            'total_cost': 0,
                            'average_cost_per_session': 0
                        }
        except Exception as e:
            logger.error(f"Error getting token usage stats: {e}")
            return {
                'total_sessions': 0,
                'total_tokens': 0,
                'total_cost': 0,
                'average_cost_per_session': 0
            }

    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE user_sessions 
                        SET is_active = FALSE
                        WHERE expires_at < CURRENT_TIMESTAMP
                    """)
                    deleted_count = cursor.rowcount
                    conn.commit()
                    if deleted_count > 0:
                        logger.info(f"Cleaned up {deleted_count} expired sessions")
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")


# Global database manager instance
db_manager = DatabaseManager()


def init_database():
    """Initialize the database."""
    db_manager.init_database()


def create_demo_user():
    """Create demo user if it doesn't exist."""
    try:
        # Check if demo user already exists
        if db_manager.user_exists("demo"):
            logger.info("Demo user already exists, skipping creation")
            return
        
        # If demo user doesn't exist, create it
        if db_manager.create_user("demo", "demo123", "demo@example.com"):
            logger.info("Demo user created successfully")
        else:
            logger.info("Demo user creation failed")
    except Exception as e:
        logger.error(f"Error creating demo user: {e}")


# Initialize database and demo user on import
if __name__ == "__main__":
    init_database()
    create_demo_user() 