import os
import glob

replacements = {
    'h-[350px]': 'h-full',
    'min-h-[300px]': 'h-full'
}

chart_files = glob.glob('e:/AegisGAN_live/frontend/src/components/*Chart.jsx') + glob.glob('e:/AegisGAN_live/frontend/src/components/*Graph.jsx') + ['e:/AegisGAN_live/frontend/src/components/TopAttackers.jsx']

for file_path in chart_files:
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
