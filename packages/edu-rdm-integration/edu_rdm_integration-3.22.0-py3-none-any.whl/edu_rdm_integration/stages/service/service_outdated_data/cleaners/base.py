from abc import (
    ABCMeta,
    abstractmethod,
)

from django.conf import (
    settings,
)
from django.db import (
    connection,
)

from educommon import (
    logger,
)


class BaseServiceOutdatedDataCleaner(metaclass=ABCMeta):
    """Базовый класс уборщика устаревших сервисных данных."""

    model = None

    SELECT_RDM_CHUNK_BOUNDED_SQL = """
        DO $$
        DECLARE
            chunk_size INT := {chunk_size};
            last_id INT := 0;
            first_id INT;
            last_chunk_id INT;
        BEGIN
            DROP TABLE IF EXISTS rdm_chunk_bounds;
            CREATE TEMP TABLE rdm_chunk_bounds (
                chunk_number INT,
                first_id INT,
                last_id INT
            );

            DROP TABLE IF EXISTS tmp_chunk;
            CREATE TEMP TABLE tmp_chunk (id INT) ON COMMIT DROP;

            WHILE TRUE LOOP
                TRUNCATE tmp_chunk;

                INSERT INTO tmp_chunk (id)
                SELECT id
                FROM {table_name}
                WHERE id > last_id
                ORDER BY id
                LIMIT chunk_size;

                IF NOT FOUND THEN
                    EXIT;
                END IF;

                SELECT MIN(id), MAX(id)
                INTO first_id, last_chunk_id
                FROM tmp_chunk;

                INSERT INTO rdm_chunk_bounds (chunk_number, first_id, last_id)
                VALUES (
                    (SELECT COUNT(*) FROM rdm_chunk_bounds) + 1,
                    first_id,
                    last_chunk_id
                );

                last_id := last_chunk_id;
            END LOOP;
        END $$;

        SELECT * FROM rdm_chunk_bounds ORDER BY chunk_number;
    """

    REMOVE_OUTDATED_DATA_SQL = """
        WITH deleted_rows AS (
            DELETE FROM {table_name}
            WHERE id IN (
                WITH tbl AS (
                    SELECT *
                    FROM {table_name}
                    WHERE id >= {first_id}
                        AND id <= {last_id}
                )
                SELECT tbl.id
                FROM tbl
                WHERE {conditions}
            )
            RETURNING id
        )
        SELECT COUNT(*) AS deleted_count FROM deleted_rows;
    """

    def __init__(
        self,
        *args,
        safe: bool = False,
        log_sql: bool = False,
        **kwargs
    ):
        """Инициализация уборщика."""
        self._safe = safe
        self._log_sql = log_sql
        self._deleted_count = 0

        super().__init__(*args, **kwargs)

    @abstractmethod
    def get_merged_conditions(self) -> str:
        """Возвращает условия для удаления устаревших данных."""

    @classmethod
    def get_table_name(cls) -> str:
        """Возвращает имя таблицы в базе данных."""
        if cls.model is None:
            raise NotImplementedError('Необходимо задать атрибут "model"')
        return cls.model._meta.db_table

    def get_orphan_reference_condition(
        self,
        reference_table: str,
        reference_field: str,
        local_field: str = 'id'
    ) -> str:
        """Условие проверки отсутствия записей в связанной таблице."""
        return f"""
            NOT EXISTS (
                SELECT 1
                FROM {reference_table} ref
                WHERE ref.{reference_field} = tbl.{local_field}
            )
        """

    def get_status_condition(
        self,
        related_table: str,
        related_field: str,
        status_value: str,
        days: int,
        local_field: str = 'id'
    ) -> str:
        """Условие проверки записи с заданным статусом и возрастом."""
        return f"""
            EXISTS (
                SELECT 1
                FROM {related_table} sub
                WHERE sub.{related_field} = tbl.{local_field}
                  AND sub.status_id = '{status_value}'
                  AND sub.ended_at <= NOW() - INTERVAL '{days} days'
            )
        """

    def get_chunk_bounds(self):
        """Возвращает границы чанков для текущей таблицы."""
        sql = self.SELECT_RDM_CHUNK_BOUNDED_SQL.format(
            table_name=self.get_table_name(),
            chunk_size=settings.CLEANUP_MODELS_OUTDATED_DATA_CHUNK_SIZE,
        )
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def _log_query(self, sql: str):
        """Логирует SQL-запрос."""
        try:
            import sqlparse
            sql = sqlparse.format(sql, reindent=True, strip_comments=True)
        except ImportError:
            pass

        logger.info(
            f'Запрос для удаления устаревших данных модели {self.get_table_name()}:\n{sql}\n'
        )

    def _execute_delete_sql(self, delete_sql: str) -> int:
        """Выполняет SQL-запрос на удаление (или только логирует в safe-режиме)."""
        deleted = 0
        if self._log_sql:
            self._log_query(delete_sql)

        if self._safe:
            logger.info(
                f'Безопасный режим включен — запрос удаления для {self.get_table_name()} не выполнен.'
            )
            return 0
        else:
            with connection.cursor() as cursor:
                cursor.execute(delete_sql)
                result = cursor.fetchone()
                deleted = result[0] if result else 0

        return deleted

    def run(self):
        """Запуск очистки данных."""
        conditions = self.get_merged_conditions()

        # Разделяем по чанкам
        chunk_bounded = self.get_chunk_bounds()
        for chunk_number, first_id, last_id in chunk_bounded:
            while True:
                delete_sql = self.REMOVE_OUTDATED_DATA_SQL.format(
                    table_name=self.get_table_name(),
                    first_id=first_id,
                    last_id=last_id,
                    conditions=conditions,
                )
                deleted = self._execute_delete_sql(delete_sql)
                self._deleted_count += deleted

                if deleted < self.chunk_size:
                    break

        logger.info(
            f'Удалено устаревших записей сервисной модели {self.model.__name__}: {self._deleted_count}'
        )
