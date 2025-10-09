import ast
import inspect
from abc import (
    abstractmethod,
)
from dataclasses import (
    dataclass,
)
from enum import (
    Enum,
)
from typing import (
    Iterable,
)

from django.apps import (
    apps,
)
from django.db import (
    migrations,
)
from django.db.migrations.operations.fields import (
    FieldOperation,
)
from django.db.migrations.operations.models import (
    ModelOperation as DjangoModelOperation,
)
from django.db.migrations.operations.special import (
    RunSQL,
)
from django.db.migrations.state import (
    ProjectState,
)


SCHEMA_NAME = 'backup'


class BackupType(Enum):

    FULL = 'full'
    PARTIAL = 'partial'


class BackupStrategy:
    """Абстрактная стратегия резервного копирования."""

    @abstractmethod
    def backup(self, tables: Iterable[str], backup_type: BackupType, **options):
        """Резервное копирование таблиц `tables` с типом копии `backup_type`."""


@dataclass
class ModelOperation:
    """Операция над моделью Django.

    Содержит данные, однозначно определяющие объект манипуляций.
    """

    app_label: str
    model_name: str
    operation: FieldOperation
    backwards: bool

    def get_model(self, state: ProjectState):
        """Получить модель приложения по их именам.

        Сначала производится поиск по историческим моделям, затем - по актуальным.
        """
        try:
            return state.apps.get_model(self.app_label, self.model_name)
        except LookupError:
            return apps.get_model(self.app_label, self.model_name)

    def get_table_name(self, state: ProjectState):
        return self.get_model(state)._meta.db_table


def is_get_model_call(item: ast.AST) -> bool:
    return (
        isinstance(item, ast.Call) and
        getattr(item.func, 'attr', None) == 'get_model'
    )


def get_planned_operations(
    plan: list[tuple[migrations.Migration, bool]]
) -> Iterable[ModelOperation]:
    """Получить операции над моделью Django из плана миграции."""

    for migration, backwards in plan:
        for operation in migration.operations:
            if isinstance(operation, RunSQL):
                raise NotImplementedError('Определение таблиц по SQL не реализовано')

            elif isinstance(operation, (DjangoModelOperation, )) and backwards:
                yield ModelOperation(
                    app_label=migration.app_label,
                    model_name=operation.name,
                    operation=operation,
                    backwards=backwards
                )

            elif isinstance(operation, (FieldOperation, )):
                yield ModelOperation(
                    app_label=migration.app_label,
                    model_name=operation.model_name,
                    operation=operation,
                    backwards=backwards
                )

            elif isinstance(operation, (migrations.RunPython, )):
                for fn in operation.code, operation.reverse_code:
                    if not fn or fn.__name__ == 'noop':
                        continue

                    for item in ast.walk(ast.parse(inspect.getsource(fn))):
                        if is_get_model_call(item) and all(
                            isinstance(arg, ast.Constant) for arg in item.args
                        ):
                            yield ModelOperation(
                                app_label=item.args[0].value,
                                model_name=item.args[1].value,
                                operation=operation,
                                backwards=backwards
                            )


def get_full_qualname(cls):
    """Получение полного имени класса.

    .. code-block:: python
      assert get_full_qualname(SomeTask) == 'package.module.SomeTask'

    """
    assert inspect.isclass(cls)
    return f'{cls.__module__}.{cls.__qualname__}'
