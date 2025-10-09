# История изменений
Все изменения проекта должны быть отражены в этом файле.

Формат основан на [Keep a Changelog](http://keepachangelog.com/)
и проект следует [Семантическому версионированию](http://semver.org/).


## [x.y.z] - гггг-мм-дд
 
Здесь должно быть расширенное описание того, что было сделано, какие есть планы у команды по дальнейшему развитию. 
Желательно будущие цели привязывать к конкретным задачам. Т.е. на каждую цель нужно поставить отдельную задачу и 
отразить ее номер здесь.
 
### Добавлено

- [ПРОЕКТ-ZZZZ](https://jira.bars.group/browse/ПРОЕКТ-ZZZZ)
  PATCH Название задачи или изменения.

- [ПРОЕКТ-YYYY](https://jira.bars.group/browse/ПРОЕКТ-YYYY)
  MINOR Название задачи или изменения.

- [ПРОЕКТ-XXXX](https://jira.bars.group/browse/ПРОЕКТ-XXXX)
  MAJOR Название задачи или изменения.
 
### Изменено
 
### Исправлено

### Удалено


## [0.8.0] - 2025-10-08

Переименование m3-django-compat в m3-django-compatibility.

### Изменено

- [PYTD-20](https://jira.bars.group/browse/PYTD-20)
  MINOR Переименование m3-django-compat в m3-django-compatibility.


## [0.7.2] - 2025-09-15

### Изменено

- [EDUCLLG-7932](https://jira.bars.group/browse/EDUCLLG-7932)
  PATCH из атрибута order_number убрано дефолтное значение DEFAULT_ORDER_NUMBER, указан новый тип


## [0.7.1] - 2025-09-02
 
Добавление параметра is_reversed для получения значений модели-перечисления в обратном порядке.
 
### Добавлено

- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  PATCH Добавление параметра is_reversed для получения значений модели-перечисления в обратном порядке.

### Исправлено

- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  PATCH Исправлена потенциальная ошибка при расчете порядкового номера пустой модели-перечислении.


## [0.7.0] - 2025-08-29
 
Произведены работы по изменению алгоритма расчета порядкового номера элемента модели-перечисления. Произведен уход от 
использования значения по умолчанию. Теперь, если порядковый номер не задан, то новый элемент будет добавляться в конец 
списка и присвоится соответствующее порядковое значение.

Добавлено свойство класса модели перечисления `is_strict_order_number`. Флаг указывает на необходимость соблюдения 
уникальности порядкового номера. Ранее допускалось дублирование значений порядковых номеров, если это не имело значения.
Но при ручном указании порядкового номера могли возникать ошибки, если добавлялось множество значений 
модели-перечисления.

В FictiveForeignKeyField добавлено свойство `to`, в котором указывается модель в виде строки 
'<app_label>.<model_class_name>'. Таким образом появляется возможность выстраивания связей между моделями. 
 
### Добавлено

- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  MINOR Добавлено свойство модели перечисления `is_strict_order_number`.

- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  MINOR В FictiveForeignKeyField добавлено свойство `to`.

### Изменено

- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  MINOR Изменен алгоритм подсчета порядкового номера при добавлении новых элементов модели-перечисления.


## [0.6.0] - 2025-07-29

Добавлена поддержка django 4.1

### Добавлено

- [EDUKNDG-15602](https://jira.bars.group/browse/EDUKNDG-15602)
  PATCH Поддержка Django 4.1.13


## [0.5.3] - 2025-03-21

Повышение версий зависимостей для сборки пакета.

### Изменено

- [EDUDEVOPS-66](https://jira.bars.group/browse/EDUDEVOPS-66)
  PATCH Повышение версий зависимостей для сборки пакета.


## [0.5.2] - 2025-03-19
 
Замена setup.py на pyproject.toml.
 
### Изменено

- [EDUDEVOPS-66](https://jira.bars.group/browse/EDUDEVOPS-66)
  PATCH Замена setup.py на pyproject.toml.


## [0.5.1] - 2025-03-13
 
Внедрение автоматизации версионирования.
 
### Изменено

- [EDUDEVOPS-66](https://jira.bars.group/browse/EDUDEVOPS-66)
  PATCH Внедрение автоматизации версионирования через setuptools-git-versioning.


## [0.5.0] - 2025-03-10
 
Добавлена информация о базе данных в логи SQL-запросов и изменено поведение логирования.
 
### Добавлено

- [EDUKNDG-15238](https://jira.bars.group/browse/EDUKNDG-15238)
  PATCH Добавлена информация о базе данных в логах SQL-запросов.

### Изменено

- [EDUKNDG-15238](https://jira.bars.group/browse/EDUKNDG-15238)
  PATCH Обновлены форматтеры логов для отображения имени базы данных в SQL-логах.

- [EDUKNDG-15238](https://jira.bars.group/browse/EDUKNDG-15238)
  PATCH Изменено поведение логирования: SQL-запросы теперь записываются только в файл независимо от режима DEBUG.

## [0.4.1] - 2025-02-07
 
Перенос замены wrapper-ов в настройки.
 
### Изменено

- [EDUKNDG-15222](https://jira.bars.group/browse/EDUKNDG-15222)
  PATCH Перенос замены wrapper-ов в настройки.
 

## [0.4.0] - 2024-10-26
 
Изменена структура проекта и зависимостей. Произведено переименование из m3_db_utils в m3-db-utils.
 
### Добавлено

- [PYTD-49](https://jira.bars.group/browse/PYTD-49)
  PATCH Изменена структура проекта и зависимостей.

- [PYTD-49](https://jira.bars.group/browse/PYTD-49)
  MINOR Добавлены сигналы before_handle_migrate_signal и after_handle_migrate_signal для выполнения действий до прогона 
    миграций и после.

### Изменено

- [PYTD-49](https://jira.bars.group/browse/PYTD-49)
  PATCH Изменение структуры проекта.

- [PYTD-49](https://jira.bars.group/browse/PYTD-49)
  PATCH Изменение структуры зависимостей.
 
## [0.3.13] - 2024-01-30
 
Добавлен пакет m3-django-compat.
 
### Добавлено

- [EDUKNDG-12751](https://jira.bars.group/browse/EDUKNDG-12751)
  MINOR Добавлен пакет m3-django-compat. Правка конфига isort. Заменен classproperty.


## [0.3.12] - 2023-12-16
 
Переименование FictiveForeignKey на FictiveForeignKeyField.
 
### Добавлено

- [EDUSCHL-21067](https://jira.bars.group/browse/EDUSCHL-21067)
  PATCH Переименование FictiveForeignKey на FictiveForeignKeyField.


## [0.3.11] - 2023-12-16
 
Добавление фиктивного внешнего ключа.
 
### Добавлено

- [EDUSCHL-21067](https://jira.bars.group/browse/EDUSCHL-21067)
  PATCH Добавление фиктивного внешнего ключа.


## [0.3.10] - 2023-12-10

У модели TitleFieldMixin, IntegerValueMixin, PositiveIntegerValueMixin, CharValueMixin вновь сделаны 
абстрактными.

- [EDUSCHL-20965](https://jira.bars.group/browse/EDUSCHL-20965)
  PATCH - У модели TitleFieldMixin, IntegerValueMixin, PositiveIntegerValueMixin, CharValueMixin вновь сделаны 
  абстрактными.

### Изменено

- [EDUSCHL-20965](https://jira.bars.group/browse/EDUSCHL-20965)
  PATCH - У моделей-перечислений IntegerModelEnum и TitledIntegerModelEnum изменён тип поля value
  с PositiveIntegerField на IntegerField.

## [0.3.9] - 2023-12-07

У моделей-перечислений IntegerModelEnum и TitledIntegerModelEnum изменён тип поля value
с PositiveIntegerField на IntegerField.
Добавлены модели-перечисления PositiveIntegerModelEnum и TitledPositiveIntegerModelEnum с типом PositiveIntegerField
для поля value.

### Изменено

- [EDUSCHL-20965](https://jira.bars.group/browse/EDUSCHL-20965)
  PATCH - У моделей-перечислений IntegerModelEnum и TitledIntegerModelEnum изменён тип поля value
  с PositiveIntegerField на IntegerField.

### Добавлено

- [EDUSCHL-20965](https://jira.bars.group/browse/EDUSCHL-20965)
  MINOR - Добавлены модели-перечисления PositiveIntegerModelEnum и TitledPositiveIntegerModelEnum с
  типом PositiveIntegerField для поля value.


## [0.3.8] - 2023-11-02
 
Исправлен циклический импорт.
 
### Исправлено

- PATCH Исправлен циклический импорт в m3_db_utils.mixins и m3_db_utils.models.


## [0.3.7] - 2023-10-31
 
Добавление механизмов регистрации классов в TitledModelEnum.
 
### Добавлено

- PATCH Добавлен миксин BaseEnumRegisterMixin с интерфейсом регистрации класса в модель-перечисление.


## [0.3.6] - 2023-10-11
 
Переформатирование, добавление repr ModelEnumValue.
 
### Добавлено

- [EDUSCHL-20559](https://jira.bars.group/browse/EDUSCHL-20559)
  PATCH Переформатирование, добавление repr ModelEnumValue.


## [0.3.5] - 2023-08-19
 
Добавление константы LOOKUP_SEP.
 
### Добавлено
- [EDUSCHL-20277](https://jira.bars.group/browse/EDUSCHL-20277)
  PATCH Добавление константы LOOKUP_SEP.

- [EDUSCHL-20277](https://jira.bars.group/browse/EDUSCHL-20277)
  PATCH Добавление констант PK и ID.


0.3.4

* (EDUSCHL-19919) Добавлена возможность расширения модели-перечисления множеством элементов.

0.3.3

* (EDUSCHL-18423) Убрано кеширование.

0.3.2

* Отказ от m3_legacy.

0.3.1

* (EDUSCHL-18086) Доработка логирования именованных запросов.

0.3.0

* (EDUSCHL-18086) Добавление возможности логирования SQL-запросов.

0.2.1

* (EDUSCHL-17752) Перемещение m3_db_utils_after_migrate_receiver.

0.2.0

* EDUSCHL-17752 Убрано заполнение значений моделей перечислений на post_migrate на откуп приложениям из-за возникающих ошибок при прогоне миграций.

0.1.3

* EDUSCHL-17752 Добавлена совместимость с django 1.11 в классе актуализирующем значения моделей-перечислений;
* EDUSCHL-17752 Добавлены методы получения значений и ключей модели перечисления.

0.1.2

* EDUSCHL-17810 Добавление файлов в MANIFEST.in.

0.1.1

* EDUSCHL-17810 Добавление парсинга зависимостей из requirements.txt в setup.py.

0.1.0

* EDUSCHL-17810 Понижение версии Django до 1.11.29;
* EDUSCHL-17810 Обеспечение обратной совместимости.

0.0.7

* BOBUH-19787 Исправление опечаток в комментариях к коду;
* BOBUH-19787 Добавление поля order_number в модель-перечисление.

0.0.6

* BOBUH-18885 Исправление ошибки получения записей таблицы модели-перечисления, если значения модели-перечисления указываются в родительской модели-перечислении.

0.0.5

* BOBUH-18382 Исправление ошибки создания записей в таблице модели-перечисления, если значения модели-перечисления указываются в родительской модели-перечислении.

0.0.4

* BOBUH-18943 Отказ от зашитого title в модели-перечислении;
* BOBUH-18943 Добавление возможности указания более широкого набора полей в значении модели-перечисления, чем полей модели, для возможности использования значений связанных, но не хранящихся в базе данных;
* BOBUH-18943 Расширение существующих моделей-перечислений;
* BOBUH-18943 Удаление метода get_choices, для явного указания необходимости использования моделей-перечислений с внешними ключами;
* BOBUH-18943 Исправление ошибки с отсутствующим полем в значении модели-перечислении, имеющим дефолтное значение или необязательным в модели.

0.0.3

* BOBUH-18362 Замена значения модели-перечисления с кортежа на экземпляр класса; 
* BOBUH-18362 Добавлен патчинг значений моделей-перечислений ключами самих перечислений; 
* BOBUH-18362 В модели перечислении первичный ключ заменен на key.

0.0.2

* Добавление моделей-перечислений;
* Реализация механизмов для обновления значений моделей-перечислений в БД;
* Актуализация механизма сборки документации.

0.0.1

* Инициализация проекта;
* Добавление каркаса документации.