import os
from pathlib import Path
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.database import Base
from app import models
config=context.config
default_data_dir = Path(__file__).resolve().parents[2] / "data"
data_dir = Path(os.environ.get("TELCORD_DATA_DIR", default_data_dir)).resolve()
data_dir.mkdir(parents=True, exist_ok=True)
config.set_main_option("sqlalchemy.url", f"sqlite:///{(data_dir / 'telcord.db').as_posix()}")
target_metadata=Base.metadata
def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"),target_metadata=target_metadata,literal_binds=True); 
    with context.begin_transaction(): context.run_migrations()
def run_migrations_online():
    connectable=engine_from_config(config.get_section(config.config_ini_section),prefix="sqlalchemy.",poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection,target_metadata=target_metadata)
        with context.begin_transaction(): context.run_migrations()
run_migrations_offline() if context.is_offline_mode() else run_migrations_online()
