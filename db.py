import os
import logging
from typing import Optional, List, Dict

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() == 'true'

def _prepare_query(query: str) -> str:
    if not USE_SQLITE:
        query = query.replace('?', '%s')
    return query

if USE_SQLITE:
    import sqlite3
    DATABASE = os.path.join(os.path.dirname(__file__), 'taller.db')
    
    def get_connection():
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all(query: str, params: tuple = None) -> List[Dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(_prepare_query(query), params or ())
            columns = [col[0] for col in cursor.description] if cursor.description else []
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        except sqlite3.Error as e:
            logger.error(f"DB Error: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    def get_one(query: str, params: tuple = None) -> Optional[Dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(_prepare_query(query), params or ())
            columns = [col[0] for col in cursor.description] if cursor.description else []
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None
        except sqlite3.Error as e:
            logger.error(f"DB Error: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    def execute(query: str, params: tuple = None) -> int:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(_prepare_query(query), params or ())
            conn.commit()
            return cursor.lastrowid or cursor.rowcount
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"DB Error: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    def execute_many(query: str, list_params: List[tuple]):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.executemany(_prepare_query(query), list_params)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"DB Error: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    def init_db():
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            with open(os.path.join(os.path.dirname(__file__), 'database.sql'), 'r') as f:
                sql = f.read()
            cursor.executescript(sql)
            conn.commit()
            logger.info("Base de datos SQLite inicializada")
        finally:
            cursor.close()
            conn.close()
    
    def get_db_connection():
        return get_connection()
    
    def test_connection() -> bool:
        try:
            conn = get_connection()
            conn.close()
            return True
        except:
            return False

else:
    import pymysql
    from pymysql import cursors
    from dotenv import load_dotenv
    load_dotenv()
    
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'taller_db'),
        'charset': 'utf8mb4',
        'cursorclass': cursors.DictCursor,
        'autocommit': False
    }
    
    def get_connection():
        try:
            return pymysql.connect(**DB_CONFIG)
        except pymysql.Error as e:
            logger.error(f"Error de conexion: {e}")
            raise
    
    def get_all(query: str, params: tuple = None) -> List[Dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(_prepare_query(query), params or ())
            results = cursor.fetchall()
            return [dict(row) for row in results] if results else []
        except pymysql.Error as e:
            logger.error(f"DB Error: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    def get_one(query: str, params: tuple = None) -> Optional[Dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(_prepare_query(query), params or ())
            result = cursor.fetchone()
            return dict(result) if result else None
        except pymysql.Error as e:
            logger.error(f"DB Error: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    def execute(query: str, params: tuple = None) -> int:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(_prepare_query(query), params or ())
            conn.commit()
            return cursor.lastrowid or cursor.rowcount
        except pymysql.Error as e:
            if conn: conn.rollback()
            logger.error(f"DB Error: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    def execute_many(query: str, list_params: List[tuple]):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.executemany(_prepare_query(query), list_params)
            conn.commit()
        except pymysql.Error as e:
            if conn: conn.rollback()
            logger.error(f"DB Error: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    def init_db():
        conn = None
        cursor = None
        try:
            base_config = {k: v for k, v in DB_CONFIG.items() if k != 'database'}
            conn = pymysql.connect(**base_config)
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS taller_db")
            conn.commit()
            conn.close()
            
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            with open(os.path.join(os.path.dirname(__file__), 'database.sql'), 'r') as f:
                sql = f.read()
            
            statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in statements:
                if statement and 'CREATE DATABASE' not in statement:
                    try:
                        cursor.execute(statement)
                    except pymysql.Error as e:
                        logger.warning(f"Skip: {e}")
            
            conn.commit()
            logger.info("Base de datos MySQL inicializada")
        except pymysql.Error as e:
            if conn: conn.rollback()
            logger.error(f"Error: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    def get_db_connection():
        return get_connection()
    
    def test_connection() -> bool:
        try:
            conn = get_connection()
            conn.close()
            return True
        except:
            return False