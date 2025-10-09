import sys
from abc import (
    abstractmethod,
)
from itertools import (
    chain,
)
from typing import (
    Iterable,
    Optional,
    Union,
)

from django.db import (
    connections,
)
from django.utils import (
    timezone,
)

from django_backup_migrations.core.domain.model import (
    SCHEMA_NAME,
    BackupStrategy,
    BackupType,
)


class _BaseStrategy(BackupStrategy):

    create_schema_query = f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA_NAME}";'

    drop_by_name_query = 'DROP TABLE IF EXISTS %(table_name)s;'

    drop_by_token_query = f"""\
        DO
        $$
        DECLARE
           row record;
        BEGIN
            FOR row IN (
              SELECT table_name
              FROM information_schema.tables
              WHERE table_schema = '{SCHEMA_NAME}'
              AND table_name LIKE '%%_backup_%%_%(version_token)s'
            )
           LOOP
             EXECUTE 'DROP TABLE "' || row.table_name || '"';
           END LOOP;
        END;
        $$
    """

    get_copy_list_query: str = f"""\
        SELECT table_schema || '.' || table_name
        FROM information_schema.tables
        WHERE table_schema = '{SCHEMA_NAME}'
        AND table_name LIKE '%(table_name)s_backup_%%'
        ORDER BY substring(table_name, '\\d{8}_\\d{12}')
    """

    def __init__(self, version_token: Optional[str] = None):
        self.__version_token = version_token

    @abstractmethod
    def backup(self, tables: Iterable[str], backup_type: BackupType, **options):
        self._ensure_schema_exists(**options)

    def rollback(self, version_token=None, **options):
        self._ensure_schema_exists(**options)

        if not version_token:
            version_token = self._get_version_token()

        with self._get_connection(**options).cursor() as cursor:
            cursor.execute(
                self.drop_by_token_query % {
                    'version_token': version_token
                }
            )
        sys.stdout.write(f'  Удалены таблицы с токеном {version_token}\n')

    def clean_obsolete(self, tables: Iterable[str], keep: int, **options):
        """Очистка устаревших данных."""
        self._ensure_schema_exists(**options)

        with self._get_connection(**options).cursor() as cursor:
            for table in tables:
                backups = self._get_copy_list(table, **options)

                try:
                    last_full_to_keep = [i for i in backups if 'backup_full' in i][-keep]
                except IndexError:
                    return

                tables_to_drop = backups[:backups.index(last_full_to_keep)]
                for table_name in tables_to_drop:
                    cursor.execute(
                        self.drop_by_name_query % {
                            'table_name': table_name
                        }
                    )
                    sys.stdout.write(f'  Удалена таблица {table_name}\n')

    def _get_version_token(self):
        if not self.__version_token:
            self.__version_token = timezone.now().strftime('%Y%m%d_%H%M%S%f')

        return self.__version_token

    def _ensure_schema_exists(self, **options):
        with self._get_connection(**options).cursor() as cursor:
            cursor.execute(self.create_schema_query)

    def _get_connection(self, **options):
        return connections[options['database']]

    def _get_copy_list(self, table_name, **options):
        with self._get_connection(**options).cursor() as cursor:
            cursor.execute(
                self.get_copy_list_query % {'table_name': table_name}
            )
            return list(chain.from_iterable(cursor.fetchall()))


class _BackupByTypeStrategy(_BaseStrategy):

    backup_type: BackupType

    full_backup_query: str = f"""\
        DO
        $$
        BEGIN
          IF EXISTS (
            SELECT
            FROM information_schema.tables
            WHERE table_schema = current_schema()
            AND table_name = '%(source_table_name)s')
          THEN
            CREATE TABLE "{SCHEMA_NAME}"."%(backup_table_name)s" AS TABLE "%(source_table_name)s";
          END IF;
        END;
        $$
    """

    def _full_backup(self, source_table_name, **options):
        backup_table_name = self._format_backup_name(source_table_name, BackupType.FULL)
        params = {
            'source_table_name': source_table_name,
            'backup_table_name': backup_table_name
        }
        with self._get_connection(**options).cursor() as cursor:
            cursor.execute(self.full_backup_query % params)

        result_table = f'{SCHEMA_NAME}.{backup_table_name}'

        sys.stdout.write(f'  Полная копия {source_table_name} сохранена в {result_table}\n')

        return result_table

    def _format_backup_name(self, table_name: str, backup_type: BackupType):
        return f'{table_name}_backup_{backup_type.value}_{self._get_version_token()}'


class FullBackupStrategy(_BackupByTypeStrategy):

    backup_type = BackupType.FULL

    def backup(self, tables: Iterable[str], backup_type: BackupType, **options):
        backup_type = self.backup_type
        super().backup(tables, backup_type, **options)

        for table_name in tables:
            self._full_backup(table_name, **options)


class PartialBackupStrategy(_BackupByTypeStrategy):

    backup_type = BackupType.PARTIAL

    get_last_backup_type_table_query: str = f"""\
        SELECT table_schema || '.' || table_name
        FROM information_schema.tables
        WHERE table_schema = '{SCHEMA_NAME}'
        AND table_name LIKE '%(table_name)s_backup_%(backup_type)s_%%'
        ORDER BY table_name DESC
        LIMIT 1
    """

    create_partial_backup_query = """\
        do
        $$
        declare
            resultdiff text;
            diffname text;
            tablename text;
            nexttable text;
            tablenames text[];
            tablenames_len int;
            has_backup int;

        begin
            tablenames := '{%(table_array)s}'::text[];
            tablenames_len = array_length(tablenames, 1);

            EXECUTE 'DROP TABLE IF EXISTS "diff1"';

            EXECUTE format('
                CREATE TEMP TABLE "diff1" as (
                    (
                        SELECT * FROM %%1$s EXCEPT SELECT * FROM %%2$s
                    )
                )
                ', tablenames[2], tablenames[1]
            );

            resultdiff = 'diff1';

            for i in 2..tablenames_len
              LOOP
                nexttable = tablenames[i+1];
                EXIT WHEN nexttable is null;

                diffname = format('diff%%1$s', i-1);
                resultdiff = format('diff%%1$s', i);

                EXECUTE format('DROP TABLE IF EXISTS "diff%%1$s"', i);

                EXECUTE format('
                    CREATE TEMP TABLE "%%3$s" AS (
                        (
                            SELECT * FROM %%2$s EXCEPT SELECT * FROM %%1$s
                        )
                    )
                ', diffname, nexttable, resultdiff);

              END LOOP;

              EXECUTE format('SELECT 1 FROM "%%1$s" LIMIT 1', resultdiff) into has_backup;

              IF has_backup THEN
                  EXECUTE format('CREATE TABLE "backup"."%(target_table)s" AS TABLE "%%1$s";', resultdiff);
              END IF;

        end;
        $$;
    """

    def backup(self, tables: Iterable[str], backup_type: BackupType, **options):
        """Выполняет резервное копирование для указанных таблиц, используя тип резервного копирования стратегии."""
        backup_type = self.backup_type
        super().backup(tables, backup_type, **options)

        for table_name in tables:
            self._backup(table_name, **options)

    def _backup(self, table_name, **options):
        last_full_copy, created = self._get_or_create_full_copy(table_name, **options)
        if created:
            return

        schema_changed = self._schema_changed(table_name, last_full_copy, **options)
        if schema_changed:
            self._full_backup(table_name, **options)
        else:
            self._partial_backup(table_name, last_full_copy, **options)

    def _partial_backup(self, table_name, last_full_copy, **options):
        all_copies = self._get_copy_list(table_name, **options)
        last_full_and_its_partials = all_copies[all_copies.index(last_full_copy):]

        with self._get_connection(**options).cursor() as cursor:
            params = {
                'table_array': ','.join((*last_full_and_its_partials, table_name)),
                'target_table': self._format_backup_name(table_name, BackupType.PARTIAL)
            }
            cursor.execute(self.create_partial_backup_query % params)
            sys.stdout.write(f'  Частичная копия {table_name} сохранена в {params["target_table"]}\n')

    def _schema_changed(self, table_name, last_full_copy, **options):
        last_full_copy = last_full_copy.split('.')[-1]
        with self._get_connection(**options).cursor() as cursor:
            tables = (table_name, last_full_copy)
            query = """\
                SELECT COUNT(*) FROM (
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = '%s'
                    EXCEPT
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = '%s'
                ) diff
            """
            results = []
            for table1, table2 in (tables, tables[::-1]):
                cursor.execute(query % (table1, table2))
                results.append(cursor.fetchone()[0] > 0)

            return any(results)

    def _get_or_create_full_copy(self, table_name, **options) -> tuple[str, bool]:
        full_copy = self._get_last_full_copy(table_name, **options)
        if not full_copy:
            return self._full_backup(table_name, **options), True

        return full_copy, False

    def _get_last_full_copy(self, table_name, **options) -> Union[str, None]:
        with self._get_connection(**options).cursor() as cursor:
            cursor.execute(
                self.get_last_backup_type_table_query % {
                    'table_name': table_name,
                    'backup_type': BackupType.FULL.value
                }
            )
            last_full_copy = cursor.fetchone()

            if last_full_copy:
                return last_full_copy[0]

            return None


class DBTableBackupStrategy(_BaseStrategy):

    def __init__(self, version_token:Optional[str] = None):
        super().__init__(version_token=version_token)
        token = self._get_version_token()
        self.__strategies = {
            BackupType.FULL: FullBackupStrategy(token),
            BackupType.PARTIAL: PartialBackupStrategy(token)
        }

    def backup(
        self,
        tables: Iterable[str],
        backup_type: BackupType = BackupType.FULL,
        **options
    ) -> BackupStrategy:
        """Создает резервную копию указанных таблиц."""
        try:
            strategy = self.__strategies[backup_type]
        except KeyError:
            raise ValueError(f'Неподдерживаемый тип резервного копирования: {backup_type}')

        strategy.backup(tables, backup_type=backup_type, **options)

        return strategy
