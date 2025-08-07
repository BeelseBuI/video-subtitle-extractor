[简体中文](README.md) | [English](README_en.md) | Русский

## Описание проекта

![License](https://img.shields.io/badge/License-Apache%202-red.svg)
![python version](https://img.shields.io/badge/Python-3.12+-blue.svg)
![support os](https://img.shields.io/badge/OS-Windows/macOS/Linux-green.svg)

**Video-subtitle-extractor (VSE)** — это свободный проект, который извлекает встроенные в видео субтитры и создаёт для каждого видео отдельный файл **srt**. Основные возможности:

- извлечение кадров с субтитрами;
- определение области расположения субтитров;
- распознавание текста кадра;
- фильтрация текста, не относящегося к субтитрам;
- удаление водяных знаков, логотипов и встроенных субтитров (совместно с проектом [video-subtitle-remover](https://github.com/YaoFANGUK/video-subtitle-remover/tree/main));
- удаление повторяющихся строк и сохранение результата в форматах **srt** или **txt**;
- пакетная обработка нескольких видео;
- поддержка **87 языков**.

### Режимы работы
- **быстрый** — использует лёгкую модель. Работает быстрее всего, но может пропустить часть субтитров;
- **авто** — автоматически выбирает модель: на CPU — лёгкую, на GPU — точную;
- **точный** — использует точную модель и почти не пропускает субтитры, но работает очень медленно.

### Особенности
- полностью офлайн: не требуются сторонние API;
- поддержка ускорения на GPU.

## Использование

1. Нажмите «Open» и выберите файл(ы) видео;
2. Отрегулируйте область поиска субтитров;
3. Нажмите «Run».
   - Для одиночного файла выберите одно видео.
   - Для пакетной обработки выберите несколько видео одинакового разрешения и зоны субтитров.

### Удаление или замена текста
Измените файл `backend/configs/typoMap.json`, чтобы удалить или заменить определённые фразы в итоговом файле субтитров.

### Веб-интерфейс и графический запуск

Запустите мини‑сервер:
```bash
python scripts/web_server.py --output output.mp4
```
Затем откройте в браузере <http://127.0.0.1:5000> и введите заголовок видео.

Для упрощённого запуска существует графический скрипт `scripts/host_gui.py`. Он устанавливает зависимости, позволяет сохранить настройки и стартует сервер одним кликом. Чтобы собрать автономный исполняемый файл для Windows:
```bash
pip install pyinstaller
pyinstaller --onefile scripts/host_gui.py
```

## Загрузка
- Windows (одиночный файл): <https://github.com/YaoFANGUK/video-subtitle-extractor/releases/download/2.0.0/vse.exe>
- Windows GPU: <https://github.com/YaoFANGUK/video-subtitle-extractor/releases/download/2.0.0/vse_windows_gpu_v2.0.0.7z>
- Windows CPU: <https://github.com/YaoFANGUK/video-subtitle-extractor/releases/download/2.0.0/vse_windows_cpu_v2.0.0.zip>
- macOS: <https://github.com/YaoFANGUK/video-subtitle-extractor/releases/download/0.1.0/vse_macOS_CPU.dmg>

> Предлагайте идеи и сообщайте об ошибках в разделе Issues/Discussion.

## Благодарности

Проект развивается благодаря сообществу. Спасибо всем, кто делает вклад!
