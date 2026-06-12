import os
import glob

replacements = {
    "backgroundColor: '#0f172a'": "backgroundColor: 'rgba(255,255,255,0.9)'",
    "color: '#f8fafc'": "color: '#0f172a'",
    "border: '1px solid rgba(255,255,255,0.1)'": "border: '1px solid rgba(0,0,0,0.1)'",
    "stroke='#1e293b'": "stroke='#e2e8f0'",
    "stroke='#475569'": "stroke='#64748b'",
    'stroke="#1e293b"': 'stroke="#e2e8f0"',
    'stroke="#475569"': 'stroke="#64748b"',
    'stroke="#94a3b8"': 'stroke="#64748b"',
    'fill="#94a3b8"': 'fill="#64748b"',
    'stroke="#f8fafc"': 'stroke="#0f172a"',
    'fill="#f8fafc"': 'fill="#0f172a"'
}

chart_files = glob.glob('e:/AegisGAN_live/frontend/src/components/*Chart.jsx') + glob.glob('e:/AegisGAN_live/frontend/src/components/*Graph.jsx')

for file_path in chart_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
        
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {file_path}')
