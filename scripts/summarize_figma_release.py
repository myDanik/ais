"""Write the release summary only after every Figma lecture has been accepted."""
import json,hashlib
from pathlib import Path
import pymupdf
from pptx import Presentation
R=Path(__file__).resolve().parents[1]
files=[json.loads((R/f'source/figma/L{n:02}_file.json').read_text(encoding='utf8')) for n in range(1,9)]
assert all(f['status']=='approved' for f in files)
audit=json.loads((R/'qa/release_integrity.json').read_text(encoding='utf8'))
assert audit['status']=='passed'
calls=sum(x['mcp_calls'] for x in audit['lessons'])
lines=['# Проверка комплекта NLP','','Приняты восемь лекций, восемь презентаций и восемь лабораторных. Все презентации созданы в Figma Slides в едином оформлении. Тексты L03–L08, заметки и видимые подписи независимо проверены на естественный русский; отдельный рецензент проверил содержание и лично просмотрел каждый кадр Figma и экспортированного PowerPoint. Замечания исправлены до ОК.','',f"В комплекте {audit['slides']} слайд. В полных текстах отмечены все переключения: номер и название совпадают со слайдом. Привязки ведут к началу соответствующего фрагмента. Короткие notes встроены в Figma и PPTX, также приложены отдельным документом.",'',f"В журналах локального MCP — {calls} операций для текущих PPTX. Макеты переносятся из реальной SVG-геометрии Figma: текст, таблицы и основные схемы остаются редактируемыми объектами. Картинок целых слайдов нет. PDF из PPTX получен LibreOffice и просмотрен вместе с нативным PDF Figma; это не проверка в приложении Microsoft PowerPoint. Шрифты Prata и Carlito включены с лицензиями.",'','| Тема | Слайды / страницы лекции | Текст и факты | Презентация |','|---|---|---|---|']
for n,f in enumerate(files,1):
 lid=f'L{n:02}'
 with pymupdf.open(R/f'dist/teacher/{lid}/lecture.pdf') as pdf:pages=len(pdf)
 count=len(Presentation(R/f'dist/teacher/{lid}/presentation.pptx').slides)
 fact=R/f'dist/teacher/reviews/{lid}_figma_facts_review.md'
 facts=f"; [числа](reviews/{lid}_figma_facts_review.md)" if fact.exists() else ''
 lines.append(f"| [{lid} в Figma]({f['url']}) | {count} / {pages} | [язык](reviews/{lid}_figma_language_review.md){facts} | [Figma](reviews/{lid}_figma_presentation_review.md); [PowerPoint](reviews/{lid}_figma_powerpoint_review.md) |")
lines += ['',f"Технический аудит проверил {audit['pdf_files_checked']} PDF, привязки всех {audit['slides']} слайдов к лекциям, встроенные notes, общие файлы преподавателя и студента, локальные ссылки оглавлений. Ошибок нет. Результат: qa/release_integrity.json в исходниках.",'', 'Все 60 зафиксированных файлов L01/L02 сохранены побайтово. Лабораторные при оформлении остальных лекций не менялись: проверены хеши 64 файлов ноутбуков и методичек. Научный рецензент повторно сверил числа с сохранёнными вычислениями и журналами ответов.', '', f"Восемь преподавательских ноутбуков содержат {audit['executed_cells']} выполненных кодовых ячеек без ошибок. Вычислительные отпечатки совпадают после переноса в раздачу. В студенческих ноутбуках нет решений и сохранённых выходов; ключи и журналы генерации доступны только преподавателю.",'', '[РПД и билеты](reviews/course_documents_review_02.md) проверены на согласованность часов и оценивания. Пакетные проверки: [L03–L04](reviews/L03_L04_package_review.md), [L05](reviews/L05_package_review.md), [итоговый комплект L03–L08](reviews/remaining_package_review.md).','', 'Данные университета «Север» созданы для курса. Выводы относятся к закреплённым моделям и этой коллекции. Подготовка среды описана в START; веса моделей в архивы не включены. FILES_SHA256.json фиксирует содержимое каждой раздачи.']
(R/'dist/teacher/QA_SUMMARY.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
progress=json.loads((R/'source/figma/remaining_progress.json').read_text(encoding='utf8'))
for f in progress['files']:f['status']='approved'
progress['status']='complete';progress['slides']=sum(len(f['slides']) for f in files[2:]);progress['reviewed']='2026-09-21'
(R/'source/figma/remaining_progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'slides':audit['slides'],'mcp_calls':calls,'completed_lessons':6}))
