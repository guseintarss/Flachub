#!/usr/bin/env python
"""
Скрипт для добавления тегов в базу данных PageGlow
"""

import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PageGlow.settings')
django.setup()

from main.models import TagPost

# Список тегов по категориям
TAGS = [
    # Программирование
    {'name': 'программирование', 'slug': 'programmirovanie'},
    {'name': 'основы_программирования', 'slug': 'osnovy_programmirovaniya'},
    {'name': 'обучение_IT', 'slug': 'obuchenie_IT'},
    {'name': 'для_начинающих', 'slug': 'dlya_nachinayushchih'},
    {'name': 'алгоритмы', 'slug': 'algoritmy'},
    {'name': 'структуры_данных', 'slug': 'struktury_dannyh'},
    {'name': 'логика_программирования', 'slug': 'logika_programmirovaniya'},
    {'name': 'основы_компьютерной_грамотности', 'slug': 'osnovy_kompyuternoy_gramotnosti'},
    {'name': 'IT_для_чайников', 'slug': 'IT_dlya_chaynikov'},
    {'name': 'самообучение_IT', 'slug': 'samoobuchenie_IT'},
    
    # Веб-разработка
    {'name': 'веб-разработка', 'slug': 'veb-razrabotka'},
    {'name': 'фронтенд', 'slug': 'frontend'},
    {'name': 'бэкенд', 'slug': 'backend'},
    {'name': 'fullstack', 'slug': 'fullstack'},
    {'name': 'HTML', 'slug': 'html'},
    {'name': 'CSS', 'slug': 'css'},
    {'name': 'JavaScript', 'slug': 'javascript'},
    {'name': 'TypeScript', 'slug': 'typescript'},
    {'name': 'React', 'slug': 'react'},
    {'name': 'Vue', 'slug': 'vue'},
    {'name': 'Angular', 'slug': 'angular'},
    {'name': 'Node.js', 'slug': 'nodejs'},
    {'name': 'PHP', 'slug': 'php'},
    {'name': 'Django', 'slug': 'django'},
    {'name': 'Flask', 'slug': 'flask'},
    {'name': 'адаптивный_дизайн', 'slug': 'adaptivnyy_dizayn'},
    {'name': 'UX/UI', 'slug': 'ux-ui'},
    {'name': 'REST_API', 'slug': 'rest_api'},
    {'name': 'GraphQL', 'slug': 'graphql'},
    
    # Мобильные технологии
    {'name': 'мобильная_разработка', 'slug': 'mobilnaya_razrabotka'},
    {'name': 'iOS', 'slug': 'ios'},
    {'name': 'Swift', 'slug': 'swift'},
    {'name': 'Android', 'slug': 'android'},
    {'name': 'Kotlin', 'slug': 'kotlin'},
    {'name': 'Java', 'slug': 'java'},
    {'name': 'Flutter', 'slug': 'flutter'},
    {'name': 'React_Native', 'slug': 'react_native'},
    {'name': 'PWA', 'slug': 'pwa'},
    {'name': 'кроссплатформенная_разработка', 'slug': 'krossplatformennaya_razrabotka'},
    {'name': 'мобильные_приложения', 'slug': 'mobilnye_prilozheniya'},
    
    # Искусственный интеллект и машинное обучение
    {'name': 'ИИ', 'slug': 'ii'},
    {'name': 'искусственный_интеллект', 'slug': 'iskusstvennyy_intellekt'},
    {'name': 'машинное_обучение', 'slug': 'mashinnoe_obuchenie'},
    {'name': 'ML', 'slug': 'ml'},
    {'name': 'глубокое_обучение', 'slug': 'glubokoe_obuchenie'},
    {'name': 'нейросети', 'slug': 'neyroseti'},
    {'name': 'ChatGPT', 'slug': 'chatgpt'},
    {'name': 'Midjourney', 'slug': 'midjourney'},
    {'name': 'обработка_естественного_языка', 'slug': 'obrabotka_estestvennogo_yazyka'},
    {'name': 'компьютерное_зрение', 'slug': 'kompyuternoe_zrenie'},
    {'name': 'TensorFlow', 'slug': 'tensorflow'},
    {'name': 'PyTorch', 'slug': 'pytorch'},
    {'name': 'Scikit-learn', 'slug': 'scikit-learn'},
    
    # Инфраструктура и DevOps
    {'name': 'DevOps', 'slug': 'devops'},
    {'name': 'облачные_технологии', 'slug': 'oblachnye_tehnologii'},
    {'name': 'IaaS', 'slug': 'iaas'},
    {'name': 'PaaS', 'slug': 'paas'},
    {'name': 'SaaS', 'slug': 'saas'},
    {'name': 'Docker', 'slug': 'docker'},
    {'name': 'Kubernetes', 'slug': 'kubernetes'},
    {'name': 'CI/CD', 'slug': 'ci-cd'},
    {'name': 'GitHub_Actions', 'slug': 'github_actions'},
    {'name': 'GitLab_CI', 'slug': 'gitlab_ci'},
    {'name': 'серверы', 'slug': 'servera'},
    {'name': 'виртуализация', 'slug': 'virtualizaciya'},
    {'name': 'инфраструктура_как_код', 'slug': 'infrastruktura_kak_kod'},
    {'name': 'Terraform', 'slug': 'terraform'},
    {'name': 'Ansible', 'slug': 'ansible'},
    
    # Кибербезопасность
    {'name': 'кибербезопасность', 'slug': 'kiberbezopasnost'},
    {'name': 'информационная_безопасность', 'slug': 'informacionnaya_bezopasnost'},
    {'name': 'защита_данных', 'slug': 'zashchita_dannyh'},
    {'name': 'шифрование', 'slug': 'shifrovanie'},
    {'name': 'аутентификация', 'slug': 'autentifikaciya'},
    {'name': 'двухфакторная_аутентификация', 'slug': 'dvuhfaktornaya_autentifikaciya'},
    {'name': 'фишинг', 'slug': 'fishing'},
    {'name': 'DDoS', 'slug': 'ddos'},
    {'name': 'ransomware', 'slug': 'ransomware'},
    {'name': 'пентест', 'slug': 'pentest'},
    {'name': 'безопасность_веб-приложений', 'slug': 'bezopasnost_veb-prilozheniy'},
    {'name': 'SSL/TLS', 'slug': 'ssl-tls'},
    
    # Базы данных
    {'name': 'базы_данных', 'slug': 'bazy_dannyh'},
    {'name': 'SQL', 'slug': 'sql'},
    {'name': 'NoSQL', 'slug': 'nosql'},
    {'name': 'MySQL', 'slug': 'mysql'},
    {'name': 'PostgreSQL', 'slug': 'postgresql'},
    {'name': 'MongoDB', 'slug': 'mongodb'},
    {'name': 'Redis', 'slug': 'redis'},
    {'name': 'управление_данными', 'slug': 'upravlenie_dannymi'},
    {'name': 'оптимизация_запросов', 'slug': 'optimizaciya_zaprosov'},
    {'name': 'репликация', 'slug': 'replikaciya'},
    {'name': 'шардирование', 'slug': 'shardirovanie'},
    
    # Инструменты и среды разработки
    {'name': 'IDE', 'slug': 'ide'},
    {'name': 'VS_Code', 'slug': 'vs_code'},
    {'name': 'IntelliJ_IDEA', 'slug': 'intellij_idea'},
    {'name': 'PyCharm', 'slug': 'pycharm'},
    {'name': 'Git', 'slug': 'git'},
    {'name': 'GitHub', 'slug': 'github'},
    {'name': 'GitLab', 'slug': 'gitlab'},
    {'name': 'терминал', 'slug': 'terminal'},
    {'name': 'командная_строка', 'slug': 'komandnaya_stroka'},
    {'name': 'отладка', 'slug': 'otladka'},
    {'name': 'тестирование_кода', 'slug': 'testirovanie_koda'},
    {'name': 'юнит-тесты', 'slug': 'yunit-testy'},
    
    # Тренды и футурология
    {'name': 'технологии_будущего', 'slug': 'tehnologii_budushchego'},
    {'name': 'Web3', 'slug': 'web3'},
    {'name': 'блокчейн', 'slug': 'blokchejn'},
    {'name': 'NFT', 'slug': 'nft'},
    {'name': 'метавселенные', 'slug': 'metavselennoe'},
    {'name': 'VR', 'slug': 'vr'},
    {'name': 'AR', 'slug': 'ar'},
    {'name': 'квантовые_вычисления', 'slug': 'kvantovye_vychisleniya'},
    {'name': 'цифровая_трансформация', 'slug': 'cifrovaya_transformaciya'},
    {'name': 'инновации', 'slug': 'innovacii'},
    {'name': 'технологические_тренды', 'slug': 'tehnologicheskie_trendy'},
    
    # Методологии и процессы
    {'name': 'Agile', 'slug': 'agile'},
    {'name': 'Scrum', 'slug': 'scrum'},
    {'name': 'Kanban', 'slug': 'kanban'},
    {'name': 'управление_проектами', 'slug': 'upravlenie_proektami'},
    {'name': 'продуктовая_разработка', 'slug': 'produktovaya_razrabotka'},
    {'name': 'документация', 'slug': 'dokumentaciya'},
    {'name': 'код-ревью', 'slug': 'kod-revyu'},
    {'name': 'рефакторинг', 'slug': 'refaktoring'},
    {'name': 'техническая_долг', 'slug': 'tehnicheskaya_dolg'},
    
    # Личный опыт и кейсы
    {'name': 'история_успеха', 'slug': 'istoriya_uspeha'},
    {'name': 'личный_опыт', 'slug': 'lichnyy_opyt'},
    {'name': 'карьерный_рост_в_IT', 'slug': 'karernyy_rost_v_IT'},
    {'name': 'фриланс', 'slug': 'frilans'},
    {'name': 'удалённая_работа', 'slug': 'udalyonnaya_rabota'},
    {'name': 'собеседование_в_IT', 'slug': 'sobesedovanie_v_IT'},
    {'name': 'портфолио_разработчика', 'slug': 'portfolo_razrabotchika'},
    {'name': 'профессиональное_развитие', 'slug': 'professionalnoe_razvitie'},
    {'name': 'менторство', 'slug': 'mentorstvo'},
    
    # Разное
    {'name': 'гаджеты', 'slug': 'gadzety'},
    {'name': 'железо', 'slug': 'zhelezo'},
    {'name': 'процессоры', 'slug': 'processory'},
    {'name': 'видеокарты', 'slug': 'videokarty'},
    {'name': 'сети', 'slug': 'seti'},
    {'name': 'интернет', 'slug': 'internet'},
    {'name': 'хостинг', 'slug': 'hosting'},
    {'name': 'домен', 'slug': 'domen'},
    {'name': 'SEO', 'slug': 'seo'},
    {'name': 'аналитика', 'slug': 'analitika'},
    {'name': 'Big_Data', 'slug': 'big_data'},
    {'name': 'IoT', 'slug': 'iot'},
    {'name': 'робототехника', 'slug': 'robototehnika'},
    
    # Гаджеты и устройства
    {'name': 'смартфоны', 'slug': 'smartfony'},
    {'name': 'планшеты', 'slug': 'planety'},
    {'name': 'ноутбуки', 'slug': 'noutbuki'},
    {'name': 'умные_часы', 'slug': 'umnye_chasy'},
    {'name': 'беспроводные_наушники', 'slug': 'besprovodnye_naushniki'},
    {'name': 'VR-гарнитуры', 'slug': 'vr-garnitury'},
    {'name': 'игровые_консоли', 'slug': 'igrovye_konsoli'},
    {'name': 'фотоаппараты', 'slug': 'fotoapparaty'},
    {'name': 'экшн-камеры', 'slug': 'ekshn-kamery'},
    {'name': 'электронные_книги', 'slug': 'elektronnye_knigi'},
    {'name': 'периферийные_устройства', 'slug': 'periferiynye_ustroystva'},
    {'name': 'аксессуары_для_гаджетов', 'slug': 'aksessuary_dlya_gadzhetov'},
    
    # Цифровые сервисы и приложения
    {'name': 'облачные_хранилища', 'slug': 'oblachnye_hranilishcha'},
    {'name': 'онлайн-офисы', 'slug': 'onlayn-ofisy'},
    {'name': 'мессенджеры', 'slug': 'mesendzhery'},
    {'name': 'социальные_сети', 'slug': 'socialnye_seti'},
    {'name': 'стриминговые_сервисы', 'slug': 'strimingovye_servisy'},
    {'name': 'навигационные_приложения', 'slug': 'navigacionnye_prilozheniya'},
    {'name': 'приложения_для_продуктивности', 'slug': 'prilozheniya_dlya_produktivnosti'},
    {'name': 'сервисы_видеоконференций', 'slug': 'servisy_videokonferenciy'},
    {'name': 'цифровые_подписки', 'slug': 'cifrovye_podpiski'},
    {'name': 'онлайн-банкинг', 'slug': 'onlayn-banking'},
    
    # Интернет и сети
    {'name': 'Wi-Fi', 'slug': 'wi-fi'},
    {'name': 'мобильный_интернет', 'slug': 'mobilnyy_internet'},
    {'name': '5G', 'slug': '5g'},
    {'name': 'спутниковый_интернет', 'slug': 'sputnikovyy_internet'},
    {'name': 'домашний_интернет', 'slug': 'domashniy_internet'},
    {'name': 'роутеры', 'slug': 'routery'},
    {'name': 'сетевые_технологии', 'slug': 'setevye_tehnologii'},
    {'name': 'скорость_интернета', 'slug': 'skorost_interneta'},
    {'name': 'киберпространство', 'slug': 'kiberprostranstvo'},
    {'name': 'цифровая_среда', 'slug': 'cifrovaya_sreda'},
    
    # Кибербезопасность и приватность
    {'name': 'защита_личных_данных', 'slug': 'zashchita_lichnyh_dannyh'},
    {'name': 'приватность_в_интернете', 'slug': 'privatnost_v_internete'},
    {'name': 'безопасные_пароли', 'slug': 'bezopasnye_paroli'},
    {'name': 'мошенничество_онлайн', 'slug': 'moshennichestvo_onlayn'},
    {'name': 'антивирусные_программы', 'slug': 'antivirusnye_programmy'},
    {'name': 'цифровой_след', 'slug': 'cifrovoy_sled'},
    {'name': 'безопасность_детей_в_сети', 'slug': 'bezopasnost_detey_v_seti'},
    {'name': 'защита_от_слежки', 'slug': 'zashchita_ot_slezhki'},
    
    # Цифровая грамотность и образование
    {'name': 'цифровая_грамотность', 'slug': 'cifrovaya_gramotnost'},
    {'name': 'онлайн-обучение', 'slug': 'onlayn-obuchenie'},
    {'name': 'образовательные_платформы', 'slug': 'obrazovatelnye_platformy'},
    {'name': 'дистанционное_обучение', 'slug': 'distancionnoe_obuchenie'},
    {'name': 'электронные_курсы', 'slug': 'elektronnye_kursy'},
    {'name': 'навыки_будущего', 'slug': 'navyki_budushchego'},
    {'name': 'работа_с_документами', 'slug': 'rabota_s_dokumentami'},
    {'name': 'поиск_информации_в_интернете', 'slug': 'poisk_informacii_v_internete'},
    {'name': 'критическое_мышление_в_цифре', 'slug': 'kriticheskoe_myshlenie_v_cifre'},
    {'name': 'основы_интернета', 'slug': 'osnovy_interneta'},
    
    # Игры и развлечения
    {'name': 'видеоигры', 'slug': 'videoigry'},
    {'name': 'игровая_индустрия', 'slug': 'igrovaya_industriya'},
    {'name': 'киберспорт', 'slug': 'kibersport'},
    {'name': 'стриминг_игр', 'slug': 'striming_igr'},
    {'name': 'инди-игры', 'slug': 'indi-igry'},
    {'name': 'мобильные_игры', 'slug': 'mobilnye_igry'},
    {'name': 'игровые_сообщества', 'slug': 'igrovye_soobshchestva'},
    {'name': 'виртуальные_миры', 'slug': 'virtualnye_miry'},
    {'name': 'игровые_тренды', 'slug': 'igrovye_trendy'},
    {'name': 'обзоры_игр', 'slug': 'obzory_igr'},
    
    # Медиа и контент
    {'name': 'подкасты', 'slug': 'podkasty'},
    {'name': 'видеоблоги', 'slug': 'videoblogi'},
    {'name': 'контент-креаторы', 'slug': 'kontent-kreatory'},
    {'name': 'монетизация_контента', 'slug': 'monetizaciya_kontenta'},
    {'name': 'авторские_права', 'slug': 'avtorskie_prava'},
    {'name': 'цифровой_контент', 'slug': 'cifrovoy_kontent'},
    {'name': 'стриминг', 'slug': 'striming'},
    {'name': 'онлайн-журналистика', 'slug': 'onlayn-zhurnalistika'},
    {'name': 'цифровое_творчество', 'slug': 'cifrovoe_tvorchestvo'},
    {'name': 'креативные_инструменты', 'slug': 'kreativnye_instrumenty'},
    
    # Технологии в жизни и обществе
    {'name': 'умный_дом', 'slug': 'umnyy_dom'},
    {'name': 'носимые_технологии', 'slug': 'nosimye_tehnologii'},
    {'name': 'технологии_для_здоровья', 'slug': 'tehnologii_dlya_zdorovya'},
    {'name': 'фитнес-трекеры', 'slug': 'fitnes-trekery'},
    {'name': 'технологии_в_образовании', 'slug': 'tehnologii_v_obrazovanii'},
    {'name': 'технологии_в_медицине', 'slug': 'tehnologii_v_medicine'},
    {'name': 'автоматизация_быта', 'slug': 'avtomatizaciya_byta'},
    {'name': 'будущее_технологий', 'slug': 'budushchee_tehnologiy'},
    
    # Работа и карьера
    {'name': 'цифровые_профессии', 'slug': 'cifrovye_professii'},
    {'name': 'онлайн-заработок', 'slug': 'onlayn-zarabotok'},
    {'name': 'портфолио', 'slug': 'portfolo'},
    {'name': 'резюме', 'slug': 'rezyume'},
    {'name': 'собеседование', 'slug': 'sobesedovanie'},
    {'name': 'soft_skills', 'slug': 'soft_skills'},
    {'name': 'управление_временем', 'slug': 'upravlenie_vremenem'},
    
    # Тренды и общество
    {'name': 'цифровая_этика', 'slug': 'cifrovaya_etika'},
    {'name': 'цифровое_неравенство', 'slug': 'cifrovoe_neravenstvo'},
    {'name': 'влияние_технологий_на_общество', 'slug': 'vliyanie_tehnologiy_na_obshchestvo'},
    {'name': 'стартапы', 'slug': 'startapy'},
    {'name': 'венчурные_инвестиции', 'slug': 'venchurnye_investicii'},
    {'name': 'цифровая_экономика', 'slug': 'cifrovaya_ekonomika'},
    
    # Дизайн и творчество
    {'name': 'графический_дизайн', 'slug': 'graficheskiy_dizayn'},
    {'name': 'UI/UX', 'slug': 'ui-ux'},
    {'name': 'дизайн_интерфейсов', 'slug': 'dizayn_interfeysov'},
    {'name': 'цифровое_искусство', 'slug': 'cifrovoe_iskusstvo'},
    {'name': '3D-моделирование', 'slug': '3d-modelirovanie'},
    {'name': 'анимация', 'slug': 'animaciya'},
    {'name': 'обработка_фото', 'slug': 'obrabotka_foto'},
    {'name': 'фоторедактирование', 'slug': 'fotoredaktirovanie'},
    {'name': 'креативное_программное_обеспечение', 'slug': 'kreativnoe_programmnoe_obespechenie'},
    {'name': 'инструменты_дизайнера', 'slug': 'instrumenty_dizaynera'},
    
    # Наука и футурология
    {'name': 'дроны', 'slug': 'drony'},
    {'name': 'автономные_транспортные_средства', 'slug': 'avtonomnye_transportnye_sredstva'},
    {'name': 'биотехнологии', 'slug': 'biotehnologii'},
    {'name': 'нанотехнологии', 'slug': 'nanotehnologii'},
    {'name': 'космические_технологии', 'slug': 'kosmicheskie_tehnologii'},
    {'name': 'футурология', 'slug': 'futurologiya'},
    {'name': 'научные_открытия', 'slug': 'nauchnye_otkrytiya'},
    {'name': 'технологические_прорывы', 'slug': 'tehnologicheskie_proryvy'},
    
    # Экология и устойчивое развитие
    {'name': 'экологичные_гаджеты', 'slug': 'ekologichnye_gadzhety'},
    {'name': 'утилизация_электроники', 'slug': 'utilizaciya_elektroniki'},
    {'name': 'углеродный_след_цифровых_сервисов', 'slug': 'uglerodnyy_sled_cifrovyh_servisov'},
    {'name': 'энергоэффективность_устройств', 'slug': 'energoeffektivnost_ustroystv'},
    {'name': 'зелёные_технологии', 'slug': 'zelyonye_tehnologii'},
    {'name': 'цифровая_экология', 'slug': 'cifrovaya_ekologiya'},
]


def add_tags():
    """Добавляет теги в базу данных"""
    created_count = 0
    updated_count = 0
    
    for tag_data in TAGS:
        tag, created = TagPost.objects.get_or_create(
            slug=tag_data['slug'],
            defaults={'tag': tag_data['name']}
        )
        if created:
            created_count += 1
            print(f"✓ Добавлен тег: {tag.tag}")
        else:
            updated_count += 1
            print(f"• Уже существует: {tag.tag}")
    
    print(f"\n{'='*50}")
    print(f"Готово! Добавлено: {created_count}, Уже существовало: {updated_count}")
    print(f"Всего тегов в базе: {TagPost.objects.count()}")


if __name__ == '__main__':
    add_tags()
