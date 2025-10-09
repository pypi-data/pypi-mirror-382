# Расширение механизма миграций Django для резевного копирования данных

## Описание

Механизм позволяет перед применением миграций Django создать резервную копию изменяемых таблиц.

Возможно два варианта копирования: полная копия и частичная с изменениями после предыдущего запуска.

## Подключение

```python
INSTALLED_APPS = [
    ...
    'django_backup_migrations',
    ...
]
```

## Использование

```sh
$ manage.py backupmigrate [параметры]
```

Параметры:

* \-\-backup-type - тип резервного копирования
* \-\-backup-strategy - стратегия резервного копирования

## Пример использования

```sh
$ python ./manage.py backupmigrate app 0004
```

![Output example](./docs/images/backupmigrate.png)

## Сборка и распространение

```sh
$ python -m build && \
$ twine check ./dist/* && \
$ twine upload ./dist/* --repository-url=http://... -u user.name -p userpassword
```
