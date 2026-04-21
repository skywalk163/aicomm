# -*- coding: utf-8 -*-
"""数据库迁移环境配置"""

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from kotti import Base
from kotti import get_settings

config = context.config


def run_migrations_offline():
    """离线模式运行迁移"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """在线模式运行迁移"""
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    connection = engine.connect()
    context.configure(connection=connection, target_metadata=Base.metadata)

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
