#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Textual меню.
"""

print("=" * 70)
print("ЗАПУСК TEXTUAL КОНФИГУРАЦИОННОГО МЕНЮ")
print("=" * 70)
print()
print("✅ Что вы ДОЛЖНЫ увидеть:")
print()
print("  1. Вверху: Header с заголовком '🐧 Penguin Tamer - Конфигурация'")
print("  2. Ряд вкладок:")
print("     - 🤖 Управление LLM")
print("     - 🎛️ Параметры")
print("     - 📝 Контент")
print("     - 🔧 Система")
print("     - 🌐 Язык/Тема")
print("     - ℹ️ Инфо")
print()
print("  3. В первой вкладке '🤖 Управление LLM':")
print("     - Заголовок 'Управление моделями и выбор текущей'")
print("     - Текст 'Текущая LLM: <название>'")
print("     - Таблица со всеми LLM (4 колонки: ✓, Название, Модель, API URL)")
print("     - Кнопки: '✅ Выбрать как текущую', '➕ Добавить', '✏️ Изменить',")
print("               '🗑️ Удалить', '🔄 Обновить'")
print()
print("  4. Внизу: Footer с подсказками клавиш")
print()
print("  5. Уведомление: '📊 Загружено 4 LLM' и '✅ Меню загружено'")
print()
print("=" * 70)
print("⌨️  УПРАВЛЕНИЕ:")
print("=" * 70)
print()
print("  Tab        - Переключение между вкладками")
print("  ↑/↓        - Навигация по таблицам")
print("  Enter      - Выбор элемента / Нажатие кнопки")
print("  Q          - Выход")
print("  Ctrl+C     - Выход")
print()
print("=" * 70)
print()
print("🚀 Запускаю приложение...")
print("   (Если вы видите пустой экран - нажмите Ctrl+C и сообщите об этом)")
print()

import sys
sys.path.insert(0, 'src')

from penguin_tamer.config_menu import ConfigMenu

app = ConfigMenu()
app.run()
