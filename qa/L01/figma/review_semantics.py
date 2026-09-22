from pathlib import Path
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict

OUT = Path(__file__).parent
ROOT = OUT.parents[2]
lecture = (ROOT / 'source/lectures/L01.md').read_text(encoding='utf-8')
meta = json.loads((ROOT / 'source/figma/L01_content.json').read_text(encoding='utf-8'))
with (ROOT / 'data/requests.csv').open(encoding='utf-8-sig', newline='') as handle:
    rows = list(csv.DictReader(handle))
groups = defaultdict(list)
for row in rows:
    groups[row['group_id']].append(row)
positions = [lecture.find(slide['anchor']) for slide in meta]
pattern = r'\w+|[^\w\s]'
sample = 'ИТ-поддержка: вход не работает!'
result = {
    'slides': len(meta),
    'notes_nonempty': all(slide['notes'] and all(slide['notes']) for slide in meta),
    'anchors_found': sum(pos >= 0 for pos in positions),
    'anchor_order_reversals': [i + 1 for i, pos in enumerate(positions) if i and pos < positions[i-1]],
    'corpus': {
        'rows': len(rows),
        'groups': len(groups),
        'group_size_distribution': dict(Counter(len(value) for value in groups.values())),
        'fields': list(rows[0]),
        'split_crossing_groups': [key for key, value in groups.items() if len({row['split'] for row in value}) > 1],
        'example_variants': [row['text'] for row in next(iter(groups.values()))],
    },
    'tokenization': {
        'input': sample,
        'split': sample.split(),
        'regex_pattern': pattern,
        'regex': re.findall(pattern, sample),
        'address': re.findall(pattern, 'help@sever.example'),
    },
    'unicode': {
        'composed': [f'U+{ord(char):04X}' for char in 'й'],
        'decomposed': [f'U+{ord(char):04X}' for char in 'и\u0306'],
        'nfc_equal': unicodedata.normalize('NFC', 'й') == unicodedata.normalize('NFC', 'и\u0306'),
        'alphabets_remain_distinct': unicodedata.normalize('NFC', 'a') != unicodedata.normalize('NFC', 'а'),
    },
    'normalization': {
        'input': '  Не  отменяйте запись!  ',
        'collapsed': ' '.join('  Не  отменяйте запись!  '.split()),
        'final_exercise_collapsed': ' '.join('  Не  отменяйте запись на 12 октября!  '.split()),
    },
}
(OUT / 'review_semantics.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({key: result[key] for key in ['slides', 'notes_nonempty', 'anchors_found', 'anchor_order_reversals']}))
