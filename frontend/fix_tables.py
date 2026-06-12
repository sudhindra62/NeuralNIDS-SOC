import os

replacements = {
    'text-slate-400': 'text-slate-500',
    'text-slate-300': 'text-slate-700',
    'text-slate-500': 'text-slate-600',
    'border-white/5': 'border-black/5',
    'border-white/10': 'border-black/10',
    'hover:bg-white/5': 'hover:bg-black/5',
    'bg-white/5': 'bg-black/5',
    'bg-slate-900/50': 'bg-slate-100/50',
    'bg-black/30': 'bg-slate-200/50',
    'text-sky-300': 'text-sky-600',
    'border-slate-800': 'border-slate-200',
    'bg-red-500/20': 'bg-red-100',
    'text-red-400': 'text-red-600'
}

files = [
    'e:/AegisGAN_live/frontend/src/components/AttackTable.jsx',
    'e:/AegisGAN_live/frontend/src/components/TopAttackers.jsx',
    'e:/AegisGAN_live/frontend/src/components/LiveAlerts.jsx'
]

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        for old, new in replacements.items():
            new_content = new_content.replace(old, new)
            
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Updated {file_path}')
    except Exception as e:
        print(f'Error reading {file_path}: {e}')
