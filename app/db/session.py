"""Session et connexion à la base de données."""

import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import Optional
import logging
from contextlib import contextmanager

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseSession:
    """Gestionnaire de connexions PostgreSQL avec pooling."""
    
    _pool: Optional[SimpleConnectionPool] = None
    
    @classmethod
    def init_pool(cls, min_conn: int = 1, max_conn: int = 10):
        """
        Initialise le pool de connexions.
        
        Args:
            min_conn: Nombre minimum de connexions
            max_conn: Nombre maximum de connexions
        """
        if cls._pool is None:
            try:
                cls._pool = SimpleConnectionPool(
                    min_conn,
                    max_conn,
                    host=settings.db_host,
                    port=settings.db_port,
                    database=settings.db_name,
                    user=settings.db_user,
                    password=settings.db_password
                )
                logger.info("Pool de connexions DB initialisé")
            except Exception as e:
                logger.error(f"Erreur initialisation pool DB: {e}")
                raise
    
    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        Context manager pour obtenir une connexion du pool.
        
        Usage:
            with DatabaseSession.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ...")
        """
        if cls._pool is None:
            cls.init_pool()
        
        conn = None
        try:
            conn = cls._pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Erreur DB: {e}")
            raise
        finally:
            if conn:
                cls._pool.putconn(conn)
    
    @classmethod
    def close_pool(cls):
        """Ferme le pool de connexions."""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            logger.info("Pool de connexions fermé")
