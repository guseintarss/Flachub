"""
Management command для создания backup базы данных
Использование: python manage.py backup_db
"""
import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Создаёт резервную копию базы данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Удалить старые бэкапы (оставить 7)'
        )

    def handle(self, *args, **options):
        cleanup = options.get('cleanup', False)
        
        # Создаём директорию для бэкапов
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Получаем настройки БД
        db_settings = connection.settings_dict
        db_name = db_settings.get('NAME', '')
        db_engine = db_settings.get('ENGINE', '')
        
        self.stdout.write(f'Бэкап базы данных: {db_name}')
        self.stdout.write(f'Движок: {db_engine}')
        
        # Имя файла бэкапа
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'db_backup_{timestamp}.sql'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            # Для PostgreSQL используем pg_dump
            if 'postgresql' in db_engine:
                self._backup_postgresql(db_settings, backup_path)
            # Для SQLite просто копируем файл
            elif 'sqlite' in db_engine:
                self._backup_sqlite(db_name, backup_path)
            else:
                raise CommandError(f'Бэкап для {db_engine} не поддерживается')
            
            self.stdout.write(
                self.style.SUCCESS(f'Бэкап создан: {backup_path}')
            )
            
            # Cleanup старых бэкапов
            if cleanup:
                self._cleanup_old_backups(backup_dir)
            
        except Exception as e:
            raise CommandError(f'Ошибка создания бэкапа: {str(e)}')

    def _backup_postgresql(self, db_settings, backup_path):
        """Бэкап PostgreSQL через pg_dump"""
        import subprocess
        
        db_name = db_settings.get('NAME', '')
        db_user = db_settings.get('USER', '')
        db_password = db_settings.get('PASSWORD', '')
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '5432')
        
        # Устанавливаем переменную окружения для пароля
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password
        
        cmd = [
            'pg_dump',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-d', db_name,
            '-F', 'p',  # Plain text format
            '-f', backup_path
        ]
        
        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise CommandError(f'pg_dump failed: {e.stderr}')

    def _backup_sqlite(self, db_path, backup_path):
        """Бэкап SQLite копированием файла"""
        if not os.path.exists(db_path):
            raise CommandError(f'Файл БД не найден: {db_path}')
        
        shutil.copy2(db_path, backup_path)
        
        # Дополнительно создаём SQL дамп
        from django.core.management import call_command
        sql_path = backup_path.replace('.sqlite3', '.sql')
        with open(sql_path, 'w') as f:
            call_command('dumpdata', stdout=f, format='json')

    def _cleanup_old_backups(self, backup_dir):
        """Удаление старых бэкапов, оставляем 7 последних"""
        import glob
        
        # Получаем все файлы бэкапов
        backup_files = glob.glob(os.path.join(backup_dir, 'db_backup_*'))
        backup_files.sort(key=os.path.getmtime, reverse=True)
        
        # Удаляем всё кроме 7 последних
        for old_file in backup_files[7:]:
            os.remove(old_file)
            self.stdout.write(f'Удалён старый бэкап: {old_file}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Оставлено {min(len(backup_files), 7)} последних бэкапов')
        )
