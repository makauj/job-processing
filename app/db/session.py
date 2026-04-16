from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_user_password_hash_column() -> None:
	inspector = inspect(engine)
	if "users" not in inspector.get_table_names():
		return

	user_columns = {column["name"] for column in inspector.get_columns("users")}
	if "password_hash" in user_columns:
		return

	with engine.begin() as connection:
		connection.execute(
			text("ALTER TABLE users ADD COLUMN password_hash VARCHAR DEFAULT '' NOT NULL")
		)

	engine.dispose()


def get_db() -> Generator[Session, None, None]:
	ensure_user_password_hash_column()
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
