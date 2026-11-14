// Демо-данные для статического стенда ФлакХаб.
// Стенд живёт целиком в браузере: API подменяется в src/demo/installDemo.js,
// а состояние хранится в localStorage. Никаких запросов к Django нет.
import { DEMO_CREDENTIALS } from './credentials'

const asset = name => `${import.meta.env.BASE_URL}demo/img/${name}`

const NOW = Date.now()
const DAY = 24 * 60 * 60 * 1000

function ago(days = 0, hours = 0, minutes = 0) {
  return new Date(NOW - days * DAY - hours * 60 * 60 * 1000 - minutes * 60 * 1000).toISOString()
}

export const DEMO_STORAGE_KEY = 'flachub-demo-state'
export const DEMO_SEED_VERSION = 4
export { DEMO_CREDENTIALS }

const users = [
  {
    id: 1,
    username: 'demo',
    password: 'demo1234',
    email: 'demo@flachub.test',
    first_name: 'Демо',
    last_name: 'Пользователь',
    about_me: 'Тестирую ФлакХаб и собираю обратную связь. Пишу про фронтенд, инструменты и пет-проекты.',
    avatar: null,
    banner_image: null,
    banner_gradient_start: '#0c1f18',
    banner_gradient_end: '#2f7d5a',
    data_birth: '1998-04-12',
    phone_namber: '79990000001',
    show_email: true,
    show_phone: true,
    show_birth_date: true,
    date_joined: ago(96),
    is_staff: false,
    is_superuser: false,
    is_active: true,
    reputation: 320,
  },
  {
    id: 2,
    username: 'admin',
    password: 'admin1234',
    email: 'admin@flachub.test',
    first_name: 'Администратор',
    last_name: 'ФлакХаба',
    about_me: 'Слежу за порядком, модерирую публикации и помогаю сообществу расти.',
    avatar: null,
    banner_image: asset('mountain.webp'),
    banner_gradient_start: '#0c1210',
    banner_gradient_end: '#3e5a4b',
    data_birth: '',
    phone_namber: '',
    show_email: true,
    show_phone: false,
    show_birth_date: false,
    date_joined: ago(420),
    is_staff: true,
    is_superuser: true,
    is_active: true,
    reputation: 5400,
  },
  {
    id: 3,
    username: 'alex_dev',
    password: 'demo1234',
    email: 'alex@flachub.test',
    first_name: 'Алексей',
    last_name: 'Морозов',
    about_me: 'Backend-разработчик. Django, DRF, PostgreSQL. Люблю простые решения сложных задач.',
    avatar: asset('alex.webp'),
    banner_image: asset('mountain.webp'),
    banner_gradient_start: '#0c1f18',
    banner_gradient_end: '#2f7d5a',
    data_birth: '1992-09-03',
    phone_namber: '',
    show_email: true,
    show_phone: false,
    show_birth_date: false,
    date_joined: ago(380),
    is_staff: false,
    is_superuser: false,
    is_active: true,
    reputation: 1280,
  },
  {
    id: 4,
    username: 'maria_coder',
    password: 'demo1234',
    email: 'maria@flachub.test',
    first_name: 'Мария',
    last_name: 'Соколова',
    about_me: 'Frontend-разработчица. React, TypeScript и доступные интерфейсы. Верю, что хороший UI незаметен.',
    avatar: asset('maria.webp'),
    banner_image: null,
    banner_gradient_start: '#1e0f0b',
    banner_gradient_end: '#b05a3c',
    data_birth: '1996-01-27',
    phone_namber: '',
    show_email: true,
    show_phone: false,
    show_birth_date: false,
    date_joined: ago(300),
    is_staff: false,
    is_superuser: false,
    is_active: true,
    reputation: 860,
  },
  {
    id: 5,
    username: 'ivan_admin',
    password: 'demo1234',
    email: 'ivan@flachub.test',
    first_name: 'Иван',
    last_name: 'Петров',
    about_me: 'DevOps-инженер. Docker, Linux, бесперебойная доставка изменений в прод.',
    avatar: null,
    banner_image: asset('forest.webp'),
    banner_gradient_start: '#0c1210',
    banner_gradient_end: '#3e5a4b',
    data_birth: '',
    phone_namber: '',
    show_email: true,
    show_phone: false,
    show_birth_date: false,
    date_joined: ago(260),
    is_staff: false,
    is_superuser: false,
    is_active: true,
    reputation: 430,
  },
  {
    id: 6,
    username: 'olga_devops',
    password: 'demo1234',
    email: 'olga@flachub.test',
    first_name: 'Ольга',
    last_name: 'Смирнова',
    about_me: 'Инфраструктура, CI/CD и наблюдаемость. Автоматизирую всё, что повторяется дважды.',
    avatar: null,
    banner_image: null,
    banner_gradient_start: '#101820',
    banner_gradient_end: '#466a80',
    data_birth: '',
    phone_namber: '',
    show_email: true,
    show_phone: false,
    show_birth_date: false,
    date_joined: ago(340),
    is_staff: false,
    is_superuser: false,
    is_active: true,
    reputation: 2100,
  },
  {
    id: 7,
    username: 'dmitry_front',
    password: 'demo1234',
    email: 'dmitry@flachub.test',
    first_name: 'Дмитрий',
    last_name: 'Волков',
    about_me: 'Пишу на React и TypeScript, разбираю чужой код и помогаю делать его понятнее.',
    avatar: null,
    banner_image: null,
    banner_gradient_start: '#1b150c',
    banner_gradient_end: '#9a682f',
    data_birth: '',
    phone_namber: '',
    show_email: true,
    show_phone: false,
    show_birth_date: false,
    date_joined: ago(220),
    is_staff: false,
    is_superuser: false,
    is_active: true,
    reputation: 720,
  },
  {
    id: 8,
    username: 'anna_design',
    password: 'demo1234',
    email: 'anna@flachub.test',
    first_name: 'Анна',
    last_name: 'Лебедева',
    about_me: 'Продуктовый дизайнер. Дизайн-системы, типографика и интерфейсы, в которых хочется остаться.',
    avatar: null,
    banner_image: null,
    banner_gradient_start: '#17131f',
    banner_gradient_end: '#6a5a8a',
    data_birth: '',
    phone_namber: '',
    show_email: true,
    show_phone: false,
    show_birth_date: false,
    date_joined: ago(150),
    is_staff: false,
    is_superuser: false,
    is_active: true,
    reputation: 150,
  },
]

const categories = [
  { id: 1, name: 'Python', slug: 'python' },
  { id: 2, name: 'JavaScript', slug: 'javascript' },
  { id: 3, name: 'Backend', slug: 'backend' },
  { id: 4, name: 'Frontend', slug: 'frontend' },
  { id: 5, name: 'DevOps', slug: 'devops' },
  { id: 6, name: 'Базы данных', slug: 'databases' },
  { id: 7, name: 'Алгоритмы', slug: 'algorithms' },
  { id: 8, name: 'Дизайн', slug: 'design' },
]

const tags = [
  { id: 1, tag: 'django', slug: 'django' },
  { id: 2, tag: 'react', slug: 'react' },
  { id: 3, tag: 'docker', slug: 'docker' },
  { id: 4, tag: 'python', slug: 'python' },
  { id: 5, tag: 'javascript', slug: 'javascript' },
  { id: 6, tag: 'postgresql', slug: 'postgresql' },
  { id: 7, tag: 'linux', slug: 'linux' },
  { id: 8, tag: 'api', slug: 'api' },
  { id: 9, tag: 'testing', slug: 'testing' },
  { id: 10, tag: 'git', slug: 'git' },
  { id: 11, tag: 'typescript', slug: 'typescript' },
  { id: 12, tag: 'css', slug: 'css' },
  { id: 13, tag: 'redis', slug: 'redis' },
  { id: 14, tag: 'sql', slug: 'sql' },
  { id: 15, tag: 'algorithms', slug: 'algorithms' },
  { id: 16, tag: 'design', slug: 'design' },
  { id: 17, tag: 'database', slug: 'database' },
  { id: 18, tag: 'fastapi', slug: 'fastapi' },
  { id: 19, tag: 'devops', slug: 'devops' },
  { id: 20, tag: 'ux', slug: 'ux' },
]

const posts = [
  {
    id: 1,
    title: 'Django REST Framework: от сериализаторов до продакшена',
    slug: 'django-rest-framework-ot-serializatorov-do-prodakshena',
    photo: asset('dev-django.webp'),
    post_type: 'article',
    is_published: true,
    authorId: 3,
    categoryId: 3,
    tagIds: [1, 4, 8],
    time_create: ago(1, 2),
    time_update: ago(1, 2),
    views: 4280,
    likes: [1, 4, 6, 7],
    favorites: [1, 6],
    content: `
      <h2>Зачем вообще нужен DRF</h2>
      <p>Django отлично справляется с рендерингом HTML, но мобильному приложению и SPA нужен стабильный JSON-контракт. Django REST Framework даёт готовые сериализаторы, пагинацию, права доступа и browsable API — и всё это без изобретения собственного велосипеда.</p>
      <h2>Сериализатор — это контракт</h2>
      <p>Сериализатор описывает не только поля модели, но и то, что клиент имеет право увидеть. Например, email автора стоит отдавать только при включённой настройке приватности.</p>
      <pre><code class="language-python">class PostSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'author', 'likes_count')

    def get_likes_count(self, obj):
        return obj.number_of_likes()</code></pre>
      <h2>Что проверить перед продакшеном</h2>
      <ul>
        <li>Пагинация включена на всех списочных эндпоинтах.</li>
        <li>Права проверяются на уровне объекта, а не только вьюхи.</li>
        <li>Запросы не порождают N+1: используйте <code>select_related</code> и <code>prefetch_related</code>.</li>
        <li>Ошибки валидации возвращаются в одном предсказуемом формате.</li>
      </ul>
      <blockquote>Хороший API — это не тот, который работает у автора, а тот, который предсказуемо ведёт себя у клиента.</blockquote>
      <p>В следующем материале разберём кэширование и версионирование API, чтобы обновления не ломали мобильные клиенты.</p>
    `,
  },
  {
    id: 2,
    title: 'React 19: что реально изменилось для разработчика',
    slug: 'react-19-chto-realno-izmenilos-dlya-razrabotchika',
    photo: asset('dev-react.webp'),
    post_type: 'article',
    is_published: true,
    authorId: 4,
    categoryId: 4,
    tagIds: [2, 5, 11],
    time_create: ago(2, 4),
    time_update: ago(2, 4),
    views: 3120,
    likes: [1, 3, 7],
    favorites: [1, 3],
    content: `
      <h2>Actions вместо ручных состояний</h2>
      <p>React 19 сделал работу с формами и асинхронными действиями заметно приятнее. <code>useActionState</code> объединяет состояние, ошибку и pending-статус в одном хуке.</p>
      <pre><code class="language-javascript">const [state, formAction, pending] = useActionState(
  async (_, formData) => {
    const res = await fetch('/api/profile/', {
      method: 'POST',
      body: formData,
    })
    return res.ok ? { ok: true } : { error: 'Не сохранилось' }
  },
  { ok: false },
)</code></pre>
      <h2>Компилятор — не магия</h2>
      <p>React Compiler уменьшает количество ручных <code>useMemo</code> и <code>useCallback</code>, но не отменяет правил: состояние должно быть иммутабельным, а компоненты — предсказуемыми.</p>
      <h2>Что осталось прежним</h2>
      <ul>
        <li>Список ключей и согласованность состояния.</li>
        <li>Проверка доступности интерфейса.</li>
        <li>Понимание того, где заканчивается клиент и начинается сервер.</li>
      </ul>
      <p>Мой вывод: обновляться стоит, но миграцию лучше начинать с небольших форм и списков, а не со всего приложения сразу.</p>
    `,
  },
  {
    id: 3,
    title: 'Docker Compose для полного стека: от локального запуска до продакшена',
    slug: 'docker-compose-dlya-polnogo-steka',
    photo: asset('dev-docker.webp'),
    post_type: 'article',
    is_published: true,
    authorId: 6,
    categoryId: 5,
    tagIds: [3, 7, 19],
    time_create: ago(3, 1),
    time_update: ago(3, 1),
    views: 2710,
    likes: [3, 4, 7],
    favorites: [3],
    content: `
      <h2>Один compose — один стенд</h2>
      <p>Когда в проекте появляются база, кэш, воркеры и фронтенд, ручной запуск быстро становится ритуалом. Compose фиксирует инфраструктуру в файле, который можно запустить одной командой.</p>
      <pre><code class="language-yaml">services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_PASSWORD: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 10

  web:
    build: .
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"</code></pre>
      <h2>Healthcheck важнее depends_on</h2>
      <p>Без healthcheck контейнер приложения может стартовать раньше базы и упасть. Условие <code>service_healthy</code> делает запуск предсказуемым.</p>
      <h2>Секреты не хранят в compose</h2>
      <ul>
        <li>Пароли и токены — в переменных окружения или секретах платформы.</li>
        <li>Локальный <code>.env</code> не коммитится.</li>
        <li>Образы собираются с зафиксированными версиями.</li>
      </ul>
      <p>Продакшен-конфигурация отличается от локальной, но принципы те же: явные зависимости, проверяемые состояния и воспроизводимость.</p>
    `,
  },
  {
    id: 4,
    title: 'PostgreSQL: индексы, которые ускоряют запросы в 100 раз',
    slug: 'postgresql-indeksy-kotorye-uskoryayut-zaprosy',
    photo: asset('dev-postgres.webp'),
    post_type: 'article',
    is_published: true,
    authorId: 5,
    categoryId: 6,
    tagIds: [6, 14, 17],
    time_create: ago(4, 3),
    time_update: ago(4, 3),
    views: 1980,
    likes: [3, 6],
    favorites: [1],
    content: `
      <h2>Сначала план, потом индекс</h2>
      <p>Индекс без понимания запроса — это лотерея. Начните с <code>EXPLAIN (ANALYZE, BUFFERS)</code> и найдите место, где база читает больше строк, чем нужно.</p>
      <pre><code class="language-sql">EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title
FROM posts
WHERE is_published = true
ORDER BY time_create DESC
LIMIT 20;</code></pre>
      <h2>Когда помогает составной индекс</h2>
      <p>Для запросов с фильтром и сортировкой порядок колонок имеет значение. Индекс <code>(is_published, time_create DESC)</code> может закрыть и фильтр, и сортировку.</p>
      <h2>GIN для поиска</h2>
      <p>Полнотекстовый поиск, JSONB и массивы часто выигрывают от GIN-индексов. Но у них выше стоимость записи, поэтому проверяйте реальный профиль нагрузки.</p>
      <ul>
        <li>Не индексируйте всё подряд.</li>
        <li>Следите за размером и bloat индексов.</li>
        <li>Проверяйте эффект на продовых объёмах, а не на десяти строках.</li>
      </ul>
    `,
  },
  {
    id: 5,
    title: 'ФлакХаб вышел в открытый тест: что внутри',
    slug: 'flachub-vyshel-v-otkrytyy-test',
    photo: asset('flachub-logo.webp'),
    post_type: 'news',
    is_published: true,
    authorId: 2,
    categoryId: 3,
    tagIds: [8, 9],
    time_create: ago(5, 2),
    time_update: ago(5, 2),
    views: 1540,
    likes: [1, 4, 6, 7],
    favorites: [1],
    content: `
      <h2>Что открылось</h2>
      <p>ФлакХаб — платформа для IT-специалистов: статьи, новости, идеи и разборы кода. На тестовом стенде доступны лента, профили, комментарии, подписки, личные сообщения и админ-панель.</p>
      <h2>Как посмотреть</h2>
      <p>Стенд работает без backend: данные лежат в браузере. Войдите как <strong>demo</strong> с паролем <strong>demo1234</strong> или как <strong>admin</strong> с паролем <strong>admin1234</strong>. Всё, что вы создадите, останется только в вашем браузере.</p>
      <h2>Что особенно интересно проверить</h2>
      <ul>
        <li>Разборы кода: возьмите открытый разбор и оставьте замечание к строке.</li>
        <li>Профиль: загрузите аватар и баннер, переключите темы.</li>
        <li>Админку: роли, блокировки и графики активности.</li>
        <li>Редактор: создайте публикацию с обложкой и тегами.</li>
      </ul>
      <p>Замечания и идеи присылайте в Telegram сообщества — кнопка есть в подвале сайта.</p>
    `,
  },
  {
    id: 6,
    title: 'Разбор кода: обработка ошибок в async/await',
    slug: 'razbor-koda-obrabotka-oshibok-v-async-await',
    photo: asset('dev-async.webp'),
    post_type: 'review',
    is_published: true,
    authorId: 4,
    categoryId: 4,
    tagIds: [5, 9],
    time_create: ago(6, 1),
    time_update: ago(6, 1),
    views: 1220,
    likes: [1, 3],
    favorites: [1],
    content: `
      <h2>Что хочу проверить</h2>
      <p>Этот фрагмент загружает пользователей для дашборда. Меня интересует обработка ошибок, отмена запросов и поведение при частичном сбое. Подскажите, где код поведёт себя неожиданно.</p>
      <p>Особенно важно: что произойдёт, если один из запросов вернёт 500 или зависнет.</p>
    `,
    code_snippet: [
      'async function loadUser(id) {',
      '  const response = await fetch(`/api/users/${id}`)',
      '  const data = await response.json()',
      '  return data',
      '}',
      '',
      'async function loadDashboard(ids) {',
      '  const users = []',
      '  for (const id of ids) {',
      '    users.push(await loadUser(id))',
      '  }',
      '  return users',
      '}',
    ].join('\n'),
    code_language: 'JavaScript',
    review_focus: 'Обработка ошибок и отмена запросов',
    review_status: 'open',
    reviewerId: null,
    review_accepted_at: null,
  },
  {
    id: 7,
    title: 'Разбор кода: N+1 запросы в Django ORM',
    slug: 'razbor-koda-n-1-zaprosy-v-django-orm',
    photo: asset('dev-orm.webp'),
    post_type: 'review',
    is_published: true,
    authorId: 7,
    categoryId: 3,
    tagIds: [1, 4, 17],
    time_create: ago(8, 4),
    time_update: ago(3, 2),
    views: 890,
    likes: [1, 2, 6],
    favorites: [1],
    content: `
      <h2>Контекст</h2>
      <p>Выгрузка постов для админки внезапно стала медленной. На маленькой базе всё хорошо, на тестовой — десятки секунд. Подозреваю N+1, но хочу увидеть проблему глазами.</p>
      <p>Разбор уже завершён: принятое замечание подсвечено в комментариях.</p>
    `,
    code_snippet: [
      'def published_posts(request):',
      '    posts = Post.objects.filter(is_published=True)',
      '    result = []',
      '    for post in posts:',
      '        result.append({',
      '            "title": post.title,',
      '            "author": post.author.username,',
      '            "category": post.cat.name if post.cat else None,',
      '        })',
      '    return JsonResponse({"items": result})',
    ].join('\n'),
    code_language: 'Python',
    review_focus: 'Производительность и количество запросов',
    review_status: 'completed',
    reviewerId: 1,
    review_accepted_at: ago(3, 1),
  },
  {
    id: 8,
    title: 'Идея: публичный roadmap и голосование за фичи',
    slug: 'ideya-publichnyy-roadmap-i-golosovanie',
    photo: asset('mountain.webp'),
    post_type: 'idea',
    is_published: true,
    authorId: 4,
    categoryId: 4,
    tagIds: [16, 8, 20],
    time_create: ago(9, 2),
    time_update: ago(9, 2),
    views: 760,
    likes: [1, 3],
    favorites: [1],
    content: `
      <h2>Проблема</h2>
      <p>Сейчас предложения теряются в чатах и комментариях. Не видно, что уже запланировано, что отложено и почему.</p>
      <h2>Предложение</h2>
      <p>Сделать публичную страницу roadmap с тремя колонками: «Идеи», «В работе», «Готово». У каждой карточки — автор, описание и голосование.</p>
      <ul>
        <li>Голосование одним кликом, без создания отдельного аккаунта.</li>
        <li>Статус меняется только командой, но история изменений видна всем.</li>
        <li>Связь с публикациями: идея может ссылаться на статью или разбор.</li>
      </ul>
      <h2>Что это даст</h2>
      <p>Прозрачность, меньше повторяющихся запросов и понятный приоритет для разработки. Первую версию можно собрать на существующих моделях постов.</p>
    `,
  },
  {
    id: 9,
    title: 'GitHub Actions: CI/CD за один вечер',
    slug: 'github-actions-ci-cd-za-odin-vecher',
    photo: asset('dev-ci.webp'),
    post_type: 'article',
    is_published: true,
    authorId: 6,
    categoryId: 5,
    tagIds: [10, 3, 9],
    time_create: ago(10, 5),
    time_update: ago(10, 5),
    views: 2350,
    likes: [3, 4, 7],
    favorites: [3],
    content: `
      <h2>Минимальный пайплайн</h2>
      <p>Начинать стоит не с идеального workflow, а с трёх шагов: установка зависимостей, линтер и тесты. Этого достаточно, чтобы перестать ловить синтаксические ошибки в ветке.</p>
      <pre><code class="language-yaml">name: CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test</code></pre>
      <h2>Кэш и матрицы</h2>
      <p>Кэш зависимостей экономит минуты на каждом запуске. Матрица версий помогает проверить совместимость, но не стоит запускать десять комбинаций ради десяти комбинаций.</p>
      <h2>Деплой только из main</h2>
      <ul>
        <li>Секреты хранятся в настройках репозитория.</li>
        <li>Деплой запускается после успешных тестов.</li>
        <li>Есть возможность откатиться к предыдущему артефакту.</li>
      </ul>
    `,
  },
  {
    id: 10,
    title: 'TypeScript: продвинутые типы, которые спасают проект',
    slug: 'typescript-prodvinutye-tipy-kotorye-spasayut-proekt',
    photo: asset('dev-ts.webp'),
    post_type: 'article',
    is_published: true,
    authorId: 4,
    categoryId: 4,
    tagIds: [11, 5],
    time_create: ago(12, 1),
    time_update: ago(12, 1),
    views: 1670,
    likes: [1, 7],
    favorites: [1],
    content: `
      <h2>Utility-типы — это язык</h2>
      <p><code>Pick</code>, <code>Omit</code>, <code>Partial</code> и <code>Record</code> знакомы многим. Но настоящая сила появляется, когда из существующих типов строятся производные, а не дублируются вручную.</p>
      <pre><code class="language-typescript">type ApiPost = {
  id: number
  title: string
  content: string
  isPublished: boolean
}

type PostPreview = Pick&lt;ApiPost, 'id' | 'title'&gt;
type DraftPost = Omit&lt;ApiPost, 'id'&gt; &amp; { id?: number }</code></pre>
      <h2>Дискриминированные объединения</h2>
      <p>Состояния интерфейса удобно описывать через <code>type</code>, а не через набор независимых флагов. Тогда TypeScript не даст отрисовать данные, которых ещё нет.</p>
      <h2>Практическое правило</h2>
      <p>Если тип становится сложнее бизнес-логики, возможно, проблема не в TypeScript. Сначала упростите данные, потом добавляйте условные типы.</p>
    `,
  },
  {
    id: 11,
    title: '5 книг, которые изменили мой подход к коду',
    slug: '5-knig-kotorye-izmenili-podhod-k-kodu',
    photo: null,
    post_type: 'post',
    is_published: true,
    authorId: 3,
    categoryId: 3,
    tagIds: [4, 10],
    time_create: ago(13, 3),
    time_update: ago(13, 3),
    views: 640,
    likes: [4],
    favorites: [],
    content: `
      <p>Небольшая подборка без спойлеров. Это не «обязательно к прочтению», а книги, которые в своё время поменяли мой взгляд на разработку.</p>
      <ul>
        <li><strong>«Чистый код»</strong> — не про стиль, а про цену сопровождения.</li>
        <li><strong>«Рефакторинг»</strong> — маленькими шагами безопаснее, чем большим переписыванием.</li>
        <li><strong>«Паттерны проектирования»</strong> — полезны, когда понимаешь, какую проблему решают.</li>
        <li><strong>«Высоконагруженные приложения»</strong> — про данные и узкие места, а не про модные инструменты.</li>
        <li><strong>«Психология программирования»</strong> — про людей, которые пишут и читают код.</li>
      </ul>
      <p>Если выбрали что-то одно — начните с «Рефакторинга». Он ближе всего к ежедневной работе.</p>
    `,
  },
  {
    id: 12,
    title: 'Дизайн-система для пет-проекта: токены, компоненты и тёмная тема',
    slug: 'dizayn-sistema-dlya-pet-proekta',
    photo: asset('design.webp'),
    post_type: 'article',
    is_published: true,
    authorId: 8,
    categoryId: 8,
    tagIds: [16, 12, 20],
    time_create: ago(14, 2),
    time_update: ago(14, 2),
    views: 1120,
    likes: [1, 4],
    favorites: [1],
    content: `
      <h2>С чего начать</h2>
      <p>Не с библиотеки компонентов, а с токенов. Цвет, отступ, радиус и типографика должны быть переменными. Тогда тёмная тема — это замена значений, а не второй набор стилей.</p>
      <pre><code class="language-css">:root {
  --surface: #ffffff;
  --text: #111827;
  --border: #e5e7eb;
  --radius: 12px;
}

html.dark-mode {
  --surface: #191a1b;
  --text: #f3f4f6;
  --border: #2d2f31;
}</code></pre>
      <h2>Компоненты переиспользуют токены</h2>
      <p>Кнопка, карточка и поле ввода не знают о конкретных цветах. Они используют семантические переменные, поэтому тема переключается без правок в компонентах.</p>
      <h2>Проверка доступности</h2>
      <ul>
        <li>Контраст текста не ниже 4.5:1.</li>
        <li>Фокус видим и не зависит только от цвета.</li>
        <li>Размеры интерактивных элементов не меньше 44×44 на мобильных.</li>
      </ul>
      <p>Дизайн-система окупается, когда в проекте появляется третий экран с теми же кнопками и полями.</p>
    `,
  },
  {
    id: 13,
    title: 'Redis в реальном проекте: кэш, очереди и блокировки',
    slug: 'redis-v-realnom-proekte',
    photo: asset('dev-docker.webp'),
    post_type: 'article',
    is_published: true,
    authorId: 5,
    categoryId: 3,
    tagIds: [13, 4, 17],
    time_create: ago(16, 4),
    time_update: ago(16, 4),
    views: 830,
    likes: [3],
    favorites: [],
    content: `
      <h2>Три роли Redis</h2>
      <p>В одном проекте Redis может быть кэшем, брокером лёгких очередей и хранилищем блокировок. Смешивать эти роли в одном инстансе без изоляции рискованно.</p>
      <h2>Кэш с предсказуемым TTL</h2>
      <p>Кэшируйте только то, что готовы быстро пересобрать. TTL и инвалидация должны быть частью контракта, а не сюрпризом для следующего разработчика.</p>
      <pre><code class="language-python">cache.set(f"post:{slug}", data, timeout=300)
...
cache.delete(f"post:{slug}")</code></pre>
      <h2>Блокировка с осторожностью</h2>
      <ul>
        <li>Всегда ставьте TTL на lock-ключ.</li>
        <li>Освобождайте блокировку только владельцем.</li>
        <li>Не строите на Redis строгую транзакционность, если она критична.</li>
      </ul>
    `,
  },
  {
    id: 14,
    title: 'Черновик: чем я пользуюсь каждый день',
    slug: 'chernovik-chem-ya-polzuyus-kazhdyy-den',
    photo: null,
    post_type: 'article',
    is_published: false,
    authorId: 1,
    categoryId: 4,
    tagIds: [5, 9],
    time_create: ago(0, 3),
    time_update: ago(0, 3),
    views: 0,
    likes: [],
    favorites: [],
    content: `
      <h2>Вступление</h2>
      <p>Черновик для проверки автосохранения и вкладки «Черновики» в профиле. Здесь будет подборка инструментов, которые реально использую каждый день.</p>
      <p>План: редактор, заметки, терминал, браузер и одна маленькая утилита, которая экономит больше всего времени.</p>
    `,
  },
  {
    id: 15,
    title: 'Алгоритмы сортировки: что выбрать в 2026',
    slug: 'algoritmy-sortirovki-chto-vybrat',
    photo: asset('forest.webp'),
    post_type: 'article',
    is_published: true,
    authorId: 7,
    categoryId: 7,
    tagIds: [15, 4],
    time_create: ago(18, 6),
    time_update: ago(18, 6),
    views: 1430,
    likes: [3, 6],
    favorites: [1],
    content: `
      <h2>На практике чаще всего нужен sort</h2>
      <p>Встроенные сортировки языка обычно быстрее и стабильнее самописных. Но понимать сложность всё равно полезно: на собеседованиях и при выборе структуры данных.</p>
      <h2>Короткая шпаргалка</h2>
      <ul>
        <li><strong>QuickSort</strong> — хорош в среднем, но чувствителен к выбору опорного элемента.</li>
        <li><strong>MergeSort</strong> — стабильный и предсказуемый, требует O(n) памяти.</li>
        <li><strong>HeapSort</strong> — O(n log n) в худшем случае, но плохо дружит с кэшем.</li>
        <li><strong>Counting/Radix</strong> — отличны для целых чисел в известном диапазоне.</li>
      </ul>
      <h2>Что важнее скорости</h2>
      <p>Стабильность, читаемость и объём данных. На массиве из ста элементов разница между алгоритмами почти никогда не важнее ясности кода.</p>
    `,
  },
  {
    id: 16,
    title: 'Разбор кода: валидация формы на React',
    slug: 'razbor-koda-validaciya-formy-na-react',
    photo: null,
    post_type: 'review',
    is_published: true,
    authorId: 1,
    categoryId: 4,
    tagIds: [2, 5],
    time_create: ago(0, 7),
    time_update: ago(0, 7),
    views: 210,
    likes: [3, 4],
    favorites: [],
    content: `
      <h2>Что хочу проверить</h2>
      <p>Небольшая форма профиля. Интересуют валидация, доступность и обработка ошибок при отправке. Код намеренно упрощён — это фрагмент из пет-проекта.</p>
      <p>Подскажите, какие проблемы заметны сразу и что стоит исправить в первую очередь.</p>
    `,
    code_snippet: [
      'function ProfileForm({ user }) {',
      '  const [email, setEmail] = useState(user.email)',
      '',
      '  const submit = () => {',
      "    fetch('/api/profile/', {",
      "      method: 'POST',",
      '      body: JSON.stringify({ email }),',
      '    })',
      '  }',
      '',
      '  return (',
      '    <form onSubmit={submit}>',
      '      <input value={email} onChange={e => setEmail(e.target.value)} />',
      '      <button>Сохранить</button>',
      '    </form>',
      '  )',
      '}',
    ].join('\n'),
    code_language: 'JavaScript',
    review_focus: 'Валидация, доступность и ошибки сети',
    review_status: 'open',
    reviewerId: null,
    review_accepted_at: null,
  },
]

const comments = [
  {
    id: 1,
    postId: 1,
    authorId: 4,
    parentId: null,
    content: 'Отличная статья! Особенно про проверку прав на уровне объекта — как раз на этой неделе поймали такой баг.',
    created_at: ago(1, 1),
    likes: [1, 3],
    line_start: null,
    line_end: null,
    severity: '',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 2,
    postId: 1,
    authorId: 3,
    parentId: 1,
    content: 'Спасибо! В следующем материале покажу, как это тестировать через APIClient.',
    created_at: ago(1, 0, 30),
    likes: [4],
    line_start: null,
    line_end: null,
    severity: '',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 3,
    postId: 2,
    authorId: 1,
    parentId: null,
    content: 'Попробовал useActionState на форме логина — стало меньше кода и исчезла пара гонок. Спасибо за пример!',
    created_at: ago(2, 1),
    likes: [4],
    line_start: null,
    line_end: null,
    severity: '',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 4,
    postId: 3,
    authorId: 7,
    parentId: null,
    content: 'Healthcheck спас меня на прошлой неделе. Без него миграции периодически падали при старте.',
    created_at: ago(3, 0, 20),
    likes: [6],
    line_start: null,
    line_end: null,
    severity: '',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 5,
    postId: 6,
    authorId: 3,
    parentId: null,
    content: 'fetch не бросает исключение на 500. Без проверки response.ok функция вернёт JSON ошибки как будто это пользователь.',
    created_at: ago(6, 0, 40),
    likes: [1, 4],
    line_start: 2,
    line_end: 3,
    severity: 'blocker',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 6,
    postId: 6,
    authorId: 7,
    parentId: null,
    content: 'Последовательные await в цикле умножают время загрузки на количество пользователей. Лучше Promise.all с ограничением параллелизма.',
    created_at: ago(5, 20),
    likes: [4],
    line_start: 9,
    line_end: 12,
    severity: 'major',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 7,
    postId: 6,
    authorId: 4,
    parentId: 5,
    content: 'Согласна. Добавлю try/catch и AbortController — хочу, чтобы при уходе со страницы запросы отменялись.',
    created_at: ago(5, 18),
    likes: [],
    line_start: null,
    line_end: null,
    severity: '',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 8,
    postId: 7,
    authorId: 1,
    parentId: null,
    content: 'Здесь классический N+1: author и cat подгружаются в цикле. select_related("author", "cat") уберёт лишние запросы.',
    created_at: ago(8, 3),
    likes: [2, 7],
    line_start: 5,
    line_end: 6,
    severity: 'major',
    is_resolved: true,
    is_accepted: true,
  },
  {
    id: 9,
    postId: 7,
    authorId: 2,
    parentId: null,
    content: 'Добавлю к замечанию: проверьте ещё, что для списка не нужен весь объект Post. values() может быть уместнее.',
    created_at: ago(7, 12),
    likes: [7],
    line_start: 6,
    line_end: 6,
    severity: 'minor',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 10,
    postId: 8,
    authorId: 3,
    parentId: null,
    content: 'Идея хорошая. Важно только не превратить roadmap в свалку — нужен критерий, кто и когда переносит карточки между колонками.',
    created_at: ago(9, 1),
    likes: [4],
    line_start: null,
    line_end: null,
    severity: '',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 11,
    postId: 9,
    authorId: 5,
    parentId: null,
    content: 'Добавил бы кэш pip/npm и concurrency, чтобы отменять старые запуски. В остальном отличный минимальный пример.',
    created_at: ago(10, 2),
    likes: [6],
    line_start: null,
    line_end: null,
    severity: '',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 12,
    postId: 12,
    authorId: 1,
    parentId: null,
    content: 'Про контраст особенно актуально: часто тёмная тема делается «на глаз» и потом ломает доступность.',
    created_at: ago(14, 1),
    likes: [8],
    line_start: null,
    line_end: null,
    severity: '',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 13,
    postId: 16,
    authorId: 3,
    parentId: null,
    content: 'Форма отправляется по onSubmit, но кнопка внутри формы без type="submit" в некоторых браузерах не отправит её. И нет preventDefault.',
    created_at: ago(0, 6),
    likes: [1, 4],
    line_start: 13,
    line_end: 15,
    severity: 'major',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 14,
    postId: 16,
    authorId: 7,
    parentId: null,
    content: 'У поля нет label и aria-invalid. Скринридер не поймёт, что именно сломалось при ошибке валидации.',
    created_at: ago(0, 5),
    likes: [4],
    line_start: 12,
    line_end: 12,
    severity: 'blocker',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 15,
    postId: 16,
    authorId: 1,
    parentId: 13,
    content: 'Спасибо, поправлю в следующей итерации. Отдельно вынесу состояние ошибки и disabled на время запроса.',
    created_at: ago(0, 4),
    likes: [],
    line_start: null,
    line_end: null,
    severity: '',
    is_resolved: false,
    is_accepted: false,
  },
  {
    id: 16,
    postId: 4,
    authorId: 1,
    parentId: null,
    content: 'Про EXPLAIN полезно. Добавьте, пожалуйста, пример с частичным индексом для is_published.',
    created_at: ago(4, 1),
    likes: [5],
    line_start: null,
    line_end: null,
    severity: '',
    is_resolved: false,
    is_accepted: false,
  },
]

const subscriptions = [
  { subscriberId: 1, authorId: 3 },
  { subscriberId: 1, authorId: 4 },
  { subscriberId: 1, authorId: 6 },
  { subscriberId: 3, authorId: 1 },
  { subscriberId: 4, authorId: 3 },
  { subscriberId: 4, authorId: 7 },
  { subscriberId: 5, authorId: 6 },
  { subscriberId: 7, authorId: 4 },
  { subscriberId: 6, authorId: 3 },
]

const chats = [
  { id: 1, participantIds: [1, 4], created_at: ago(4), updated_at: ago(0, 1) },
  { id: 2, participantIds: [1, 2], created_at: ago(10), updated_at: ago(1, 3) },
  { id: 3, participantIds: [1, 3], created_at: ago(12), updated_at: ago(2, 5) },
]

const messages = [
  {
    id: 1,
    chatId: 1,
    senderId: 4,
    text: 'Привет! Посмотрела твой черновик — есть пара идей по структуре.',
    created_at: ago(0, 3),
    is_read: false,
  },
  {
    id: 2,
    chatId: 1,
    senderId: 1,
    text: 'Привет! Да, давай. Что показалось самым слабым?',
    created_at: ago(0, 2, 40),
    is_read: true,
  },
  {
    id: 3,
    chatId: 1,
    senderId: 4,
    text: 'Начало хорошее, но примеры лучше поставить ближе к первому экрану. И добавь вывод в конце.',
    created_at: ago(0, 2),
    is_read: false,
  },
  {
    id: 4,
    chatId: 1,
    senderId: 4,
    text: 'Если хочешь, могу завтра посмотреть ещё раз после правок.',
    created_at: ago(0, 1),
    is_read: false,
  },
  {
    id: 5,
    chatId: 2,
    senderId: 2,
    text: 'Добро пожаловать на тестовый стенд! Если найдёшь странное поведение — пиши сюда.',
    created_at: ago(1, 3),
    is_read: false,
  },
  {
    id: 6,
    chatId: 2,
    senderId: 2,
    text: 'Админка доступна под учёткой admin / admin1234.',
    created_at: ago(1, 2, 50),
    is_read: true,
  },
  {
    id: 7,
    chatId: 3,
    senderId: 1,
    text: 'Алексей, привет! Видел твою статью про DRF. Есть вопрос по пагинации.',
    created_at: ago(2, 6),
    is_read: true,
  },
  {
    id: 8,
    chatId: 3,
    senderId: 3,
    text: 'Привет! Конечно, спрашивай. Если коротко — начинай с PageNumberPagination.',
    created_at: ago(2, 5),
    is_read: true,
  },
]

const badges = [
  { id: 1, key: 'first-post', name: 'Первый шаг', description: 'Опубликовал первый материал', icon: '✍️', color: '#4ecf94' },
  { id: 2, key: 'conversation', name: 'В диалоге', description: 'Начал обсуждение под публикацией', icon: '💬', color: '#e0a15f' },
  { id: 3, key: 'reviewer', name: 'Ревьюер', description: 'Провёл первый разбор кода', icon: '🔍', color: '#e06c5f' },
  { id: 4, key: 'expert', name: 'Эксперт', description: 'Получил уровень «Эксперт»', icon: '🌳', color: '#79a7d9' },
]

const userAchievements = [
  { id: 1, userId: 1, badgeId: 1, earned_at: ago(90), reason: 'Первая публикация' },
  { id: 2, userId: 1, badgeId: 2, earned_at: ago(60), reason: 'Активное обсуждение' },
  { id: 3, userId: 1, badgeId: 3, earned_at: ago(3), reason: 'Разбор кода принят автором' },
  { id: 4, userId: 3, badgeId: 4, earned_at: ago(200), reason: 'Репутация 500+' },
  { id: 5, userId: 4, badgeId: 1, earned_at: ago(280), reason: 'Первая публикация' },
]

const notifications = [
  {
    id: 1,
    recipientId: 1,
    senderId: 4,
    notification_type: 'chat_message',
    postId: null,
    chatId: 1,
    message: 'Мария Соколова: «Если хочешь, могу завтра посмотреть ещё раз после правок.»',
    is_read: false,
    created_at: ago(0, 1),
  },
  {
    id: 2,
    recipientId: 1,
    senderId: 3,
    notification_type: 'follow',
    postId: null,
    chatId: null,
    message: 'Алексей Морозов подписался на ваши обновления',
    is_read: false,
    created_at: ago(0, 4),
  },
  {
    id: 3,
    recipientId: 1,
    senderId: 4,
    notification_type: 'like',
    postId: 2,
    chatId: null,
    message: 'Мария Соколова оценила ваш комментарий',
    is_read: true,
    created_at: ago(1, 2),
  },
  {
    id: 4,
    recipientId: 1,
    senderId: 3,
    notification_type: 'new_post',
    postId: 1,
    chatId: null,
    message: 'Новая статья: «Django REST Framework: от сериализаторов до продакшена»',
    is_read: true,
    created_at: ago(1, 2),
  },
  {
    id: 5,
    recipientId: 1,
    senderId: 7,
    notification_type: 'comment',
    postId: 16,
    chatId: null,
    message: 'Дмитрий Волков оставил замечание к вашему разбору',
    is_read: false,
    created_at: ago(0, 5),
  },
]

export function createDemoState() {
  return {
    version: DEMO_SEED_VERSION,
    currentUserId: null,
    counters: {
      user: 8,
      post: 16,
      comment: 16,
      chat: 3,
      message: 8,
      notification: 5,
      badge: 4,
      achievement: 5,
    },
    users,
    categories,
    tags,
    posts,
    comments,
    subscriptions,
    chats,
    messages,
    badges,
    userAchievements,
    notifications,
  }
}
