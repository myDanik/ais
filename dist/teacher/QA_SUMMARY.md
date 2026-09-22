# Проверка комплекта NLP

Приняты восемь лекций, восемь презентаций и восемь лабораторных. Все презентации созданы в Figma Slides в едином оформлении. Тексты L03–L08, заметки и видимые подписи независимо проверены на естественный русский; отдельный рецензент проверил содержание и лично просмотрел каждый кадр Figma и экспортированного PowerPoint. Замечания исправлены до ОК.

В комплекте 191 слайд. В полных текстах отмечены все переключения: номер и название совпадают со слайдом. Привязки ведут к началу соответствующего фрагмента. Короткие notes встроены в Figma и PPTX, также приложены отдельным документом.

В журналах локального MCP — 3465 операций для текущих PPTX. Макеты переносятся из реальной SVG-геометрии Figma: текст, таблицы и основные схемы остаются редактируемыми объектами. Картинок целых слайдов нет. PDF из PPTX получен LibreOffice и просмотрен вместе с нативным PDF Figma; это не проверка в приложении Microsoft PowerPoint. Шрифты Prata и Carlito включены с лицензиями.

| Тема | Слайды / страницы лекции | Текст и факты | Презентация |
|---|---|---|---|
| [L01 в Figma](https://www.figma.com/slides/OBqHFG8UVRENgZheAnNGMG) | 23 / 12 | [язык](reviews/L01_figma_language_review.md) | [Figma](reviews/L01_figma_presentation_review.md); [PowerPoint](reviews/L01_figma_powerpoint_review.md) |
| [L02 в Figma](https://www.figma.com/slides/t1THZMdu1UfCR5h9udzSV5) | 23 / 11 | [язык](reviews/L02_figma_language_review.md); [числа](reviews/L02_figma_facts_review.md) | [Figma](reviews/L02_figma_presentation_review.md); [PowerPoint](reviews/L02_figma_powerpoint_review.md) |
| [L03 в Figma](https://www.figma.com/slides/3zSCQpTw4wqVEoGM8rHcNh) | 23 / 9 | [язык](reviews/L03_figma_language_review.md); [числа](reviews/L03_figma_facts_review.md) | [Figma](reviews/L03_figma_presentation_review.md); [PowerPoint](reviews/L03_figma_powerpoint_review.md) |
| [L04 в Figma](https://www.figma.com/slides/nmDKsYmBWXnqAGU6Q6e2kW) | 24 / 9 | [язык](reviews/L04_figma_language_review.md); [числа](reviews/L04_figma_facts_review.md) | [Figma](reviews/L04_figma_presentation_review.md); [PowerPoint](reviews/L04_figma_powerpoint_review.md) |
| [L05 в Figma](https://www.figma.com/slides/iWEEh2xcCzsairLLrpO7eN) | 24 / 10 | [язык](reviews/L05_figma_language_review.md); [числа](reviews/L05_figma_facts_review.md) | [Figma](reviews/L05_figma_presentation_review.md); [PowerPoint](reviews/L05_figma_powerpoint_review.md) |
| [L06 в Figma](https://www.figma.com/slides/PMxgmP3frzQXWJa3ztQtQs) | 24 / 9 | [язык](reviews/L06_figma_language_review.md); [числа](reviews/L06_figma_facts_review.md) | [Figma](reviews/L06_figma_presentation_review.md); [PowerPoint](reviews/L06_figma_powerpoint_review.md) |
| [L07 в Figma](https://www.figma.com/slides/1pX1lytnPVflurO7lqKQQq) | 25 / 9 | [язык](reviews/L07_figma_language_review.md); [числа](reviews/L07_figma_facts_review.md) | [Figma](reviews/L07_figma_presentation_review.md); [PowerPoint](reviews/L07_figma_powerpoint_review.md) |
| [L08 в Figma](https://www.figma.com/slides/mfVmTY7dC1EFHUnGKIARcS) | 25 / 10 | [язык](reviews/L08_figma_language_review.md); [числа](reviews/L08_figma_facts_review.md) | [Figma](reviews/L08_figma_presentation_review.md); [PowerPoint](reviews/L08_figma_powerpoint_review.md) |

Технический аудит проверил 83 PDF, привязки всех 191 слайдов к лекциям, встроенные notes, общие файлы преподавателя и студента, локальные ссылки оглавлений. Ошибок нет. Результат: qa/release_integrity.json в исходниках.

Все 60 зафиксированных файлов L01/L02 сохранены побайтово. Лабораторные при оформлении остальных лекций не менялись: проверены хеши 64 файлов ноутбуков и методичек. Научный рецензент повторно сверил числа с сохранёнными вычислениями и журналами ответов.

Восемь преподавательских ноутбуков содержат 112 выполненных кодовых ячеек без ошибок. Вычислительные отпечатки совпадают после переноса в раздачу. В студенческих ноутбуках нет решений и сохранённых выходов; ключи и журналы генерации доступны только преподавателю.

[РПД и билеты](reviews/course_documents_review_02.md) проверены на согласованность часов и оценивания. Пакетные проверки: [L03–L04](reviews/L03_L04_package_review.md), [L05](reviews/L05_package_review.md), [итоговый комплект L03–L08](reviews/remaining_package_review.md).

Данные университета «Север» созданы для курса. Выводы относятся к закреплённым моделям и этой коллекции. Подготовка среды описана в START; веса моделей в архивы не включены. FILES_SHA256.json фиксирует содержимое каждой раздачи.
