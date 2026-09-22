# Работа с исходниками курса

Исходники предназначены преподавателю и содержат решения и ключи. Студентам выдаётся NLP_student.zip.

## Где редактировать

- `source/lectures` — полные тексты; `source/plans` — планы преподавателя.
- `source/labs/Lxx.json` — пояснения, задания и локальные изменения кода; `Lxx_guide.md` — методички.
- `source/labs/Lxx.py` — вычислительная основа, заготовки, решения и проверки.
- `src/lectureN.ts` — конвертация снимков Figma; `src/theme.ts` и `src/components.ts` — общие типы и компоненты.
- Макеты L01–L08 находятся в Figma Slides. Адреса, содержание, storyboard и notes — в `source/figma`, реальные снимки геометрии — в `assets/figma/Lxx`. После редактирования Figma обновите SVG и повторите визуальную проверку нативного PDF и PowerPoint.
- Все полные тексты содержат подзаголовки с точными номерами и названиями слайдов. Короткие notes хранятся в `source/figma/Lxx_content.json` и входят в Figma и PowerPoint.
- `course`, `course/exam_bank.json` и `data` — общие документы, билеты и исходные данные.

## Сборка темы

Команды выполняются из корня исходников. Подготовка Python и моделей описана в START; Node-зависимости устанавливаются через `npm.cmd ci`. На Windows используйте npm.cmd, если политика PowerShell запрещает запуск npm.ps1.

```powershell
.venv/Scripts/python.exe -X utf8 scripts/build_notebooks.py --lesson 5
.venv/Scripts/python.exe -X utf8 scripts/run_notebook.py --lesson 5
.venv/Scripts/python.exe -X utf8 scripts/build_documents.py --lesson 5
npm.cmd run build -- --deck L05
```

Сборка презентации создаёт PPTX, PDF и PNG. Изменение только пояснений не требует повторного вычисления неизменённого кода: сборщик сохраняет проверенные результаты при совпадении вычислительного отпечатка. После изменения кода, данных или моделей выполните ноутбук заново и перечитайте выводы.

Редактируйте текущие JSON/MD. Общие документы из `course/*.md` собираются командой `.venv/Scripts/python.exe -X utf8 scripts/build_common.py`.

## Окружение презентаций

Нужны Node.js, Python, LibreOffice, Poppler и шрифты Prata и Carlito. Версии зависимостей сохранены в package-lock.json и requirements.txt, учебная среда — в course/requirements-lock.txt. При установленном LibreOffice можно задать LIBREOFFICE_BIN. Шрифты и лицензии находятся в assets/fonts; scripts/install_design_font.py и scripts/install_carlito.py регистрируют их для текущего пользователя Windows.

Локальные исходники MCP и подготовка сборки включены в архив. После установки зависимостей используйте scripts/setup_mcp.mjs. Он собирает сервер; scripts/mcp_render.mjs запускает его для создания слайдов. Нативное подключение сервера к окну Codex не требуется.

Полный порядок и создание новой презентации по storyboard описаны в PRESENTATIONS.md и SKILL.md. Перед выпуском просмотрите все PNG и проведите независимую проверку затронутых материалов. Затем используйте scripts/package_course.py для раздачи и архивов.
