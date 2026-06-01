# Item & Block IDs Extractor

Утилита для извлечения идентификаторов блоков и предметов из JAR-файлов модов Minecraft. Результат содержит ID с локализованными названиями, если они доступны.

## Возможности

- **Извлечение блоков** — парсинг файлов из `assets/<namespace>/blockstates/` внутри JAR
- **Извлечение предметов** — парсинг файлов из `assets/<namespace>/models/item/` внутри JAR
- **Локализация** — подстановка названий из языковых файлов `assets/<namespace>/lang/<locale>.json`
- **Fallback** — если запрошенная локаль не найдена, используется `en_us`
- **Дедупликация** — объединённый список всех уникальных ID с приоритетом записей, содержащих название

## Установка

Python 3.10+ (используются `zipfile`, `json`, `os`, `re` — никаких внешних зависимостей).

```bash
git clone [<repo-url>](https://github.com/QueenDekim/items-n-blocks-id-extractor.git)
cd items-n-blocks-id-extractor
```

## Настройка

Создайте файл `.env` в корне проекта на основе примера:

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```env
mod_path="C:/path/to/your/mod.jar"
lang="en_us"
```

### Параметры

| Параметр   | Обязательный | По умолчанию | Описание                                                            |
| ---------- | :----------: | :----------: | ------------------------------------------------------------------- |
| `mod_path` |      Да      |      —       | Путь к JAR-файлу мода                                               |
| `lang`     |     Нет      |   `en_us`    | Код локали для языкового файла (например `ru_ru`, `uk_ua`, `zh_cn`) |

## Использование

```bash
python get_ids.py
```

### Пример вывода в консоль

```
JAR:  C:/mods/create-0.5.1f.jar
Lang: en_us

=== Blocks (42) ===
  create:andesite_casing - Andesite Casing
  create:belt - Belt
  ...

=== Items (87) ===
  create:andesite_alloy - Andesite Alloy
  create:andesite_casing - Andesite Casing
  ...

=== All unique IDs (120) ===
  create:andesite_alloy - Andesite Alloy
  create:andesite_casing - Andesite Casing
  ...
```

### Выходной файл

Результат сохраняется в файл рядом со скриптом. Имя файла включает локаль:

```
ids_<locale>.txt
```

Примеры:

| `lang` в `.env` | Имя файла          |
|-----------------|--------------------|
| `en_us`         | `ids_en_us.txt`    |
| `ru_ru`         | `ids_ru_ru.txt`    |
| `uk_ua`         | `ids_uk_ua.txt`    |

Формат файла — по одной записи на строку:

```
namespace:path - Localized Name
namespace:path_without_name
```

Если для ID не найдено локализованное название, строка содержит только ID без дефиса и имени.

## Как это работает

1. Открывает JAR-файл как ZIP-архив
2. Обнаруживает все пространства имён (`namespace`) внутри `assets/`
3. Для каждого `namespace` загружает языковой файл `assets/<ns>/lang/<locale>.json`
4. Извлекает ID блоков из `assets/<ns>/blockstates/*.json` и подставляет названия по ключу `block.<ns>.<name>`
5. Извлекает ID предметов из `assets/<ns>/models/item/*.json` и подставляет названия по ключу `item.<ns>.<name>`
6. Объединяет списки, удаляя дубликаты и предпочитая записи с названиями
7. Сохраняет результат в `ids_<locale>.txt`

## Лицензия

Проект предоставляется как есть. Используйте свободно.