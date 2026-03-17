#!/usr/bin/env python
"""
Скрипт для заполнения БД навыками для PageGlow маркетплейса
Подходит для фриланс проектов по разработке и дизайну
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PageGlow.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from marketplace.models import Skill, SkillCategory

# Определяем навыки по категориям
SKILLS_DATA = {
    SkillCategory.LANGUAGE: [
        ('python', 'Python', 'fab fa-python', 'Python язык программирования', True),
        ('javascript', 'JavaScript', 'fab fa-js', 'JavaScript - язык для веб-разработки', True),
        ('typescript', 'TypeScript', 'fab fa-js-square', 'TypeScript - типизированный JavaScript', True),
        ('php', 'PHP', 'fab fa-php', 'PHP - язык серверной части', True),
        ('java', 'Java', 'fab fa-java', 'Java - мощный ООП язык', True),
        ('csharp', 'C#', 'fas fa-code', 'C# - язык .NET платформы', False),
        ('cpp', 'C++', 'fas fa-code', 'C++ - системное программирование', False),
        ('go', 'Go', 'fas fa-code', 'Go - язык для микросервисов', False),
        ('rust', 'Rust', 'fas fa-code', 'Rust - безопасный системный язык', False),
        ('ruby', 'Ruby', 'fas fa-gem', 'Ruby - динамический язык', False),
    ],
    SkillCategory.FRAMEWORK: [
        ('react', 'React', 'fab fa-react', 'React - библиотека для UI', True),
        ('vue', 'Vue.js', 'fab fa-vuejs', 'Vue.js - прогрессивный фреймворк', True),
        ('angular', 'Angular', 'fab fa-angular', 'Angular - полнофункциональный фреймворк', True),
        ('django', 'Django', 'fab fa-python', 'Django - мощный Python фреймворк', True),
        ('flask', 'Flask', 'fab fa-python', 'Flask - микрофреймворк Python', True),
        ('laravel', 'Laravel', 'fab fa-laravel', 'Laravel - элегантный PHP фреймворк', True),
        ('spring', 'Spring Boot', 'fab fa-java', 'Spring Boot - Java фреймворк', True),
        ('fastapi', 'FastAPI', 'fab fa-python', 'FastAPI - быстрый Python фреймворк', True),
        ('nextjs', 'Next.js', 'fab fa-react', 'Next.js - React фреймворк для production', True),
        ('nuxt', 'Nuxt.js', 'fab fa-vuejs', 'Nuxt.js - Vue фреймворк', False),
        ('express', 'Express.js', 'fab fa-js', 'Express.js - Node.js фреймворк', True),
        ('tailwind', 'Tailwind CSS', 'fab fa-css3', 'Tailwind CSS - утилити-фреймворк', True),
        ('bootstrap', 'Bootstrap', 'fab fa-bootstrap', 'Bootstrap - популярный CSS фреймворк', True),
    ],
    SkillCategory.DATABASE: [
        ('postgresql', 'PostgreSQL', 'fas fa-database', 'PostgreSQL - мощная реляционная БД', True),
        ('mysql', 'MySQL', 'fas fa-database', 'MySQL - популярная реляционная БД', True),
        ('mongodb', 'MongoDB', 'fas fa-database', 'MongoDB - NoSQL документная БД', True),
        ('redis', 'Redis', 'fas fa-database', 'Redis - кэширование и очереди', True),
        ('firebase', 'Firebase', 'fas fa-database', 'Firebase - BaaS платформа Google', True),
        ('sqlite', 'SQLite', 'fas fa-database', 'SQLite - встроенная БД', False),
        ('elasticsearch', 'Elasticsearch', 'fas fa-database', 'Elasticsearch - полнотекстовый поиск', False),
    ],
    SkillCategory.TOOL: [
        ('git', 'Git', 'fab fa-git', 'Git - система контроля версий', True),
        ('github', 'GitHub', 'fab fa-github', 'GitHub - хостинг проектов', True),
        ('gitlab', 'GitLab', 'fab fa-gitlab', 'GitLab - платформа DevOps', True),
        ('docker', 'Docker', 'fab fa-docker', 'Docker - контейнеризация приложений', True),
        ('kubernetes', 'Kubernetes', 'fab fa-docker', 'Kubernetes - оркестрация контейнеров', True),
        ('aws', 'AWS', 'fab fa-aws', 'AWS - облачные сервисы Amazon', True),
        ('azure', 'Azure', 'fab fa-microsoft', 'Azure - облачные сервисы Microsoft', True),
        ('gcp', 'Google Cloud', 'fab fa-google', 'Google Cloud - облачные сервисы Google', True),
        ('jenkins', 'Jenkins', 'fas fa-cogs', 'Jenkins - CI/CD платформа', False),
        ('postman', 'Postman', 'fas fa-envelope', 'Postman - тестирование API', True),
        ('slack', 'Slack', 'fab fa-slack', 'Slack - командное общение', False),
        ('jira', 'Jira', 'fas fa-tasks', 'Jira - управление проектами', False),
        ('vercel', 'Vercel', 'fas fa-cloud', 'Vercel - hosting для Next.js', True),
        ('heroku', 'Heroku', 'fas fa-cloud', 'Heroku - облачный hosting', False),
    ],
    SkillCategory.DESIGN: [
        ('figma', 'Figma', 'fas fa-pencil-ruler', 'Figma - дизайн и прототипирование', True),
        ('sketch', 'Sketch', 'fas fa-pencil-ruler', 'Sketch - дизайн для Mac', True),
        ('adobe-xd', 'Adobe XD', 'fas fa-palette', 'Adobe XD - дизайн интерфейсов', True),
        ('photoshop', 'Photoshop', 'fas fa-palette', 'Photoshop - редактирование изображений', True),
        ('illustrator', 'Illustrator', 'fas fa-palette', 'Illustrator - векторная графика', True),
        ('ui-design', 'UI Design', 'fas fa-palette', 'UI дизайн - дизайн интерфейсов', True),
        ('ux-design', 'UX Design', 'fas fa-users', 'UX дизайн - опыт пользователя', True),
        ('web-design', 'Web Design', 'fas fa-globe', 'Web Design - дизайн веб-сайтов', True),
    ],
    SkillCategory.MOBILE: [
        ('react-native', 'React Native', 'fab fa-react', 'React Native - кроссплатформа', True),
        ('flutter', 'Flutter', 'fas fa-mobile', 'Flutter - кроссплатформа', True),
        ('swift', 'Swift', 'fab fa-apple', 'Swift - разработка iOS', True),
        ('kotlin', 'Kotlin', 'fab fa-android', 'Kotlin - разработка Android', True),
        ('android', 'Android', 'fab fa-android', 'Android - разработка приложений', True),
        ('ios', 'iOS', 'fab fa-apple', 'iOS - разработка приложений', True),
    ],
    SkillCategory.TESTING: [
        ('jest', 'Jest', 'fab fa-js', 'Jest - тестирование JavaScript', True),
        ('pytest', 'Pytest', 'fab fa-python', 'Pytest - тестирование Python', True),
        ('selenium', 'Selenium', 'fas fa-bug', 'Selenium - автоматизированное тестирование', True),
        ('cypress', 'Cypress', 'fas fa-bug', 'Cypress - e2e тестирование', True),
        ('mocha', 'Mocha', 'fab fa-js', 'Mocha - фреймворк тестирования', False),
    ],
    SkillCategory.DEVOPS: [
        ('linux', 'Linux', 'fab fa-linux', 'Linux - операционная система', True),
        ('nginx', 'Nginx', 'fas fa-server', 'Nginx - веб-сервер', True),
        ('apache', 'Apache', 'fas fa-server', 'Apache - веб-сервер', False),
        ('terraform', 'Terraform', 'fas fa-cogs', 'Terraform - инфраструктура как код', True),
        ('ansible', 'Ansible', 'fas fa-cogs', 'Ansible - автоматизация', True),
        ('prometheus', 'Prometheus', 'fas fa-chart-line', 'Prometheus - мониторинг', True),
        ('grafana', 'Grafana', 'fas fa-chart-line', 'Grafana - визуализация метрик', True),
    ],
}

def populate_skills():
    """Заполнить БД навыками"""
    created_count = 0
    already_exist = 0
    
    for category, skills in SKILLS_DATA.items():
        print(f"\n📚 Категория: {category} ({dict(SkillCategory.choices)[category]})")
        
        for slug, name, icon, description, is_popular in skills:
            skill, created = Skill.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'category': category,
                    'icon': icon,
                    'description': description,
                    'is_popular': is_popular,
                }
            )
            
            if created:
                created_count += 1
                status = '✅ СОЗДАН'
            else:
                already_exist += 1
                status = '⏭️  УЖЕ СУЩЕСТВУЕТ'
            
            print(f"  {status}: {name} ({slug})")
    
    print(f"\n{'='*50}")
    print(f"📊 ИТОГИ:")
    print(f"  ✅ Создано новых: {created_count}")
    print(f"  ⏭️  Уже существовало: {already_exist}")
    print(f"  📈 Всего в БД: {Skill.objects.count()}")
    
    # Статистика по категориям
    print(f"\n📋 Статистика по категориям:")
    from django.db.models import Count
    stats = Skill.objects.values('category').annotate(count=Count('id')).order_by('category')
    for stat in stats:
        category_name = dict(SkillCategory.choices).get(stat['category'], 'Неизвестно')
        print(f"  - {category_name}: {stat['count']} навыков")

if __name__ == '__main__':
    populate_skills()
