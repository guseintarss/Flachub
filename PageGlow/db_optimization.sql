-- ============================================================================
-- ОПТИМИЗАЦИЯ БАЗЫ ДАННЫХ PAGEGLOW
-- Индексы для улучшения производительности
-- ============================================================================

-- ============================================================================
-- 1. ИНДЕКСЫ ДЛЯ POST
-- ============================================================================

-- Индекс для ускорения фильтрации по статусу публикации и дате
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_published_created 
ON main_post(is_published, time_create DESC);

-- Индекс для ускорения сортировки по просмотрам
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_views 
ON main_post(views DESC);

-- Индекс для ускорения поиска по автору
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_author 
ON main_post(author_id);

-- Индекс для ускорения фильтрации по категории
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_category 
ON main_post(cat_id);

-- Индекс для ускорения поиска по slug (уникальный)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_slug 
ON main_post(slug);

-- Индекс для ускорения фильтрации по дате создания
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_time_create 
ON main_post(time_create DESC);

-- Индекс для ускорения фильтрации по дате обновления
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_time_update 
ON main_post(time_update DESC);

-- Составной индекс для популярных постов
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_popular 
ON main_post(is_published, views DESC, time_create DESC);

-- ============================================================================
-- 2. ИНДЕКСЫ ДЛЯ COMMENT
-- ============================================================================

-- Индекс для ускорения фильтрации по посту
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_post 
ON main_comment(post_id);

-- Индекс для ускорения фильтрации по автору
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_author 
ON main_comment(author_id);

-- Индекс для ускорения сортировки по дате создания
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_created 
ON main_comment(created_at DESC);

-- Индекс для фильтрации активных комментариев
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_active 
ON main_comment(is_active, created_at DESC);

-- Индекс для ускорения поиска ответов (родительский комментарий)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_parent 
ON main_comment(parent_id);

-- Составной индекс для комментариев поста
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_post_created 
ON main_comment(post_id, created_at DESC);

-- ============================================================================
-- 3. ИНДЕКСЫ ДЛЯ USER
-- ============================================================================

-- Индекс для ускорения фильтрации по активности
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_active 
ON users_user(is_active);

-- Индекс для ускорения поиска по дате регистрации
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_joined 
ON users_user(date_joined DESC);

-- Индекс для ускорения поиска по username
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_username 
ON users_user(username);

-- Индекс для ускорения поиска по email
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_email 
ON users_user(email);

-- ============================================================================
-- 4. ИНДЕКСЫ ДЛЯ CATEGORY
-- ============================================================================

-- Индекс для ускорения поиска по slug
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_category_slug 
ON main_category(slug);

-- ============================================================================
-- 5. ИНДЕКСЫ ДЛЯ TAG
-- ============================================================================

-- Индекс для ускорения поиска по slug
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tag_slug 
ON main_tagpost(slug);

-- ============================================================================
-- 6. ИНДЕКСЫ ДЛЯ SUBSCRIPTION
-- ============================================================================

-- Индекс для ускорения поиска подписок пользователя
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_subscription_subscriber 
ON main_subscription(subscriber_id);

-- Индекс для ускорения поиска подписчиков автора
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_subscription_author 
ON main_subscription(author_id);

-- Уникальный индекс для предотвращения дублей
CREATE UNIQUE INDEX IF NOT EXISTS idx_subscription_unique 
ON main_subscription(subscriber_id, author_id);

-- ============================================================================
-- 7. ИНДЕКСЫ ДЛЯ NOTIFICATION
-- ============================================================================

-- Индекс для ускорения поиска уведомлений пользователя
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notification_recipient 
ON main_notification(recipient_id);

-- Индекс для ускорения фильтрации непрочитанных
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notification_unread 
ON main_notification(recipient_id, is_read);

-- Индекс для ускорения сортировки по дате
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notification_created 
ON main_notification(created_at DESC);

-- Составной индекс для непрочитанных уведомлений
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notification_unread_created 
ON main_notification(recipient_id, is_read, created_at DESC);

-- ============================================================================
-- 8. ИНДЕКСЫ ДЛЯ BOOKMARK
-- ============================================================================

-- Индекс для ускорения поиска закладок пользователя
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookmark_user 
ON main_bookmark(user_id);

-- Индекс для ускорения поиска закладок поста
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookmark_post 
ON main_bookmark(post_id);

-- Уникальный индекс для предотвращения дублей
CREATE UNIQUE INDEX IF NOT EXISTS idx_bookmark_unique 
ON main_bookmark(user_id, post_id);

-- ============================================================================
-- 9. FULL-TEXT SEARCH ИНДЕКСЫ
-- ============================================================================

-- Индекс для полнотекстового поиска по заголовку
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_title_search 
ON main_post USING gin(to_tsvector('russian', title));

-- Индекс для полнотекстового поиска по контенту
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_content_search 
ON main_post USING gin(to_tsvector('russian', 
    COALESCE(content, '')
));

-- Индекс для комбинированного поиска (заголовок + контент)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_combined_search 
ON main_post USING gin(to_tsvector('russian', 
    COALESCE(title, '') || ' ' || COALESCE(content, '')
));

-- ============================================================================
-- 10. ИНДЕКСЫ ДЛЯ M2M СВЯЗЕЙ
-- ============================================================================

-- Индекс для связи пост-теги
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_tags_post 
ON main_post_tags(post_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_tags_tag 
ON main_post_tags(tagpost_id);

-- ============================================================================
-- 11. АНАЛИЗ И ОБНОВЛЕНИЕ СТАТИСТИКИ
-- ============================================================================

-- Обновление статистики таблиц для оптимизатора запросов
ANALYZE main_post;
ANALYZE main_comment;
ANALYZE users_user;
ANALYZE main_category;
ANALYZE main_tagpost;
ANALYZE main_subscription;
ANALYZE main_notification;
ANALYZE main_bookmark;
ANALYZE main_post_tags;

-- ============================================================================
-- 12. ПРОВЕРКА ИНДЕКСОВ
-- ============================================================================

-- Запрос для проверки всех индексов таблицы
-- SELECT 
--     indexname,
--     indexdef
-- FROM pg_indexes
-- WHERE tablename = 'main_post'
-- ORDER BY indexname;

-- Запрос для проверки размера индексов
-- SELECT 
--     indexname,
--     pg_size_pretty(pg_relation_size(indexname::text)) as size
-- FROM pg_indexes
-- WHERE schemaname = 'public'
-- ORDER BY pg_relation_size(indexname::text) DESC;

-- ============================================================================
-- 13. VACUUM И OPTIMIZE
-- ============================================================================

-- Очистка мертвых кортежей
VACUUM ANALYZE main_post;
VACUUM ANALYZE main_comment;
VACUUM ANALYZE users_user;

-- ============================================================================
-- ПРИМЕЧАНИЯ
-- ============================================================================

-- 1. CONCURRENTLY используется для создания индексов без блокировки таблицы
-- 2. Индексы уже помечены как IF NOT EXISTS для безопасного повторного запуска
-- 3. После создания индексов выполните ANALYZE для обновления статистики
-- 4. Для больших таблиц (>1M записей) рассмотрите партиционирование
-- 5. Мониторьте использование индексов через pg_stat_user_indexes

-- ============================================================================
-- МОНИТОРИНГ ПРОИЗВОДИТЕЛЬНОСТИ
-- ============================================================================

-- Проверка использования индексов:
-- SELECT 
--     schemaname,
--     relname as table_name,
--     indexrelname as index_name,
--     idx_scan as index_scans,
--     pg_size_pretty(pg_relation_size(indexrelid)) as size
-- FROM pg_stat_user_indexes
-- WHERE schemaname = 'public'
-- ORDER BY idx_scan ASC;

-- Поиск медленных запросов:
-- SELECT 
--     query,
--     mean_exec_time,
--     calls
-- FROM pg_stat_statements
-- ORDER BY mean_exec_time DESC
-- LIMIT 10;
