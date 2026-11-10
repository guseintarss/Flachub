// Учётные записи демо-стенда. Отдельный маленький модуль, чтобы страница
// входа не тянула в production-бандл весь seed демо-данных.
export const DEMO_CREDENTIALS = {
  user: { username: 'demo', password: 'demo1234' },
  admin: { username: 'admin', password: 'admin1234' },
}
