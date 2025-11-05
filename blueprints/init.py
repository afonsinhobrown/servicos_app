from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import config

# Configuração global do banco
engine = create_engine(config.SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

# Exportar explicitamente
__all__ = ['db_session', 'engine', 'SessionLocal']