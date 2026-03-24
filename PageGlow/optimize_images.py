#!/usr/bin/env python
"""
Скрипт для оптимизации изображений в проекте PageGlow
Конвертирует изображения в формат WebP и создает миниатюры
"""

import os
import sys
from pathlib import Path
from PIL import Image
from django.conf import settings

# Настройка Django
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PageGlow.settings')

import django
django.setup()

def optimize_image(image_path, max_size=(1920, 1080), quality=85):
    """
    Оптимизация изображения:
    - Изменение размера до max_size
    - Конвертация в WebP
    - Сжатие с quality
    """
    try:
        img = Image.open(image_path)
        
        # Конвертация в RGB если необходимо (для PNG с прозрачностью)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Изменение размера с сохранением пропорций
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Сохранение в WebP
        webp_path = str(image_path).rsplit('.', 1)[0] + '.webp'
        img.save(
            webp_path,
            'WEBP',
            quality=quality,
            method=6,
            exact=False
        )
        
        # Удаляем оригинал если WebP меньше
        original_size = os.path.getsize(image_path)
        webp_size = os.path.getsize(webp_path)
        
        if webp_size < original_size:
            os.remove(image_path)
            print(f"✓ Оптимизировано: {image_path.name} ({original_size} → {webp_size} байт, -{100 - (webp_size*100//original_size)}%)")
            return webp_path
        else:
            os.remove(webp_path)
            print(f"⚠ Пропущено: {image_path.name} (WebP больше оригинала)")
            return str(image_path)
            
    except Exception as e:
        print(f"✗ Ошибка обработки {image_path}: {e}")
        return str(image_path)


def create_thumbnail(image_path, size=(400, 300)):
    """
    Создание миниатюры изображения
    """
    try:
        img = Image.open(image_path)
        
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Crop и resize для thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        thumb_path = str(image_path).rsplit('.', 1)[0] + '_thumb.webp'
        img.save(thumb_path, 'WEBP', quality=80, method=6)
        
        print(f"✓ Создана миниатюра: {thumb_path}")
        return thumb_path
        
    except Exception as e:
        print(f"✗ Ошибка создания миниатюры {image_path}: {e}")
        return None


def optimize_all_images(media_root=None):
    """
    Оптимизация всех изображений в медиа-директории
    """
    if media_root is None:
        media_root = settings.MEDIA_ROOT
    
    media_path = Path(media_root)
    photo_dirs = [
        media_path / 'photos',
        media_path / 'users',
    ]
    
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp')
    
    total = 0
    optimized = 0
    saved_bytes = 0
    
    for photo_dir in photo_dirs:
        if not photo_dir.exists():
            continue
            
        for image_path in photo_dir.rglob('*'):
            if image_path.suffix.lower() not in supported_formats:
                continue
            if '_thumb' in str(image_path):
                continue
                
            total += 1
            original_size = os.path.getsize(image_path)
            
            # Оптимизация
            optimized_path = optimize_image(image_path)
            
            if optimized_path != str(image_path):
                optimized += 1
                saved_bytes += original_size - os.path.getsize(optimized_path)
    
    print(f"\n{'='*50}")
    print(f"Всего изображений: {total}")
    print(f"Оптимизировано: {optimized}")
    print(f"Сэкономлено: {saved_bytes / 1024 / 1024:.2f} MB")
    print(f"{'='*50}")


if __name__ == '__main__':
    print("🚀 Оптимизация изображений PageGlow")
    print("="*50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--thumbnail':
            # Создание миниатюр для всех изображений
            media_path = Path(settings.MEDIA_ROOT)
            for image_path in (media_path / 'photos').rglob('*.jpg'):
                create_thumbnail(image_path)
        else:
            # Оптимизация конкретного файла
            optimize_image(Path(sys.argv[1]))
    else:
        # Оптимизация всех изображений
        optimize_all_images()
