from django.core.management.base import (
    CommandError,
    no_translations,
)
from django.core.management.commands.migrate import (
    Command as CommandBase,
)
from django.db import (
    connections,
)
from django.db.migrations.executor import (
    MigrationExecutor,
)
from django.db.migrations.loader import (
    AmbiguityError,
)
from django.utils.module_loading import (
    import_string,
)

from django_backup_migrations.core.domain.model import (
    BackupType,
    get_full_qualname,
    get_planned_operations,
)
from django_backup_migrations.core.strategies.dbtable import (
    DBTableBackupStrategy,
)


DEFAULT_BACKUP_TYPE = BackupType.FULL.value

DEFAULT_BACKUP_STRATEGY = get_full_qualname(DBTableBackupStrategy)


class Command(CommandBase):

    help = 'Выполняет резервное копирование данных, затем запускает миграции БД'

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--backup-type',
            default=DEFAULT_BACKUP_TYPE,
            help=f'Backup type: full or partial. Default - {DEFAULT_BACKUP_TYPE}'
        )
        parser.add_argument(
            '--backup-strategy',
            default=DEFAULT_BACKUP_STRATEGY,
            help=f'Backup strategy. Default - {DEFAULT_BACKUP_STRATEGY}'
        )

    @no_translations
    def handle(self, *args, **options):
        strategy = import_string(options['backup_strategy'])()
        tables = self._get_affected_tables(**options)

        self.stdout.write(self.style.MIGRATE_HEADING('Таблицы к копированию:'))
        for table in tables or ['None']:
            self.stdout.write(self.style.MIGRATE_LABEL(f"  {table}"))

        strategy.backup(tables, backup_type=BackupType(options.pop('backup_type')), **options)

        super().handle(*args, **options)

    def _get_affected_tables(self, **options) -> set[str]:
        connection = self._get_connection(**options)

        executor = MigrationExecutor(connection, self.migration_progress_callback)

        targets = self._get_target_migrations(executor, **options)

        plan = executor.migration_plan(targets)

        pre_migrate_state = executor._create_project_state(with_applied_migrations=True)

        ops = get_planned_operations(plan)

        affected_tables = set(op.get_table_name(pre_migrate_state) for op in ops)

        return affected_tables

    def _get_target_migrations(self, executor, **options):

        app_label = options.get('app_label')

        if app_label and options["migration_name"]:
            migration_name = options["migration_name"]

            if migration_name == "zero":
                targets = [(app_label, None)]

            else:
                try:
                    migration = executor.loader.get_migration_by_prefix(
                        app_label, migration_name
                    )
                except AmbiguityError:
                    raise CommandError(
                        "More than one migration matches '%s' in app '%s'. "
                        "Please be more specific." % (migration_name, app_label)
                    )
                except KeyError:
                    raise CommandError(
                        "Cannot find a migration matching '%s' from app '%s'."
                        % (migration_name, app_label)
                    )
                target = (app_label, migration.name)

                # Partially applied squashed migrations are not included in the
                # graph, use the last replacement instead.
                if (
                    target not in executor.loader.graph.nodes and
                    target in executor.loader.replacements
                ):
                    incomplete_migration = executor.loader.replacements[target]
                    target = incomplete_migration.replaces[-1]

                targets = [target]

        elif app_label:
            targets = [
                key for key in executor.loader.graph.leaf_nodes() if key[0] == app_label
            ]

        else:
            targets = executor.loader.graph.leaf_nodes()

        return targets

    def _get_connection(self, **options):
        return connections[options["database"]]
