#!/bin/bash

# Скрипт для создания аннотированных git тегов и отправки их на GitHub
# Использование: ./create_tag.sh <название_тега> <описание>
# Пример: ./create_tag.sh v1.2.0 "Добавлена админская система"

set -e  # Прерывать выполнение при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода цветного текста
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Функция для вывода справки
show_help() {
    echo "🏷️  Скрипт создания git тегов"
    echo ""
    echo "Использование:"
    echo "  ./create_tag.sh <название_тега> <описание>"
    echo ""
    echo "Примеры:"
    echo "  ./create_tag.sh v1.0.0 'Первый релиз'"
    echo "  ./create_tag.sh v1.2.0 'Добавлена админская система'"
    echo "  ./create_tag.sh hotfix-1.1.1 'Исправлена критическая ошибка'"
    echo ""
    echo "Параметры:"
    echo "  название_тега  - Имя тега (например: v1.0.0, release-2024-01)"
    echo "  описание       - Описание изменений в кавычках"
    echo ""
    echo "Опции:"
    echo "  -h, --help     - Показать эту справку"
}

# Проверка параметров командной строки
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

if [[ $# -ne 2 ]]; then
    print_color $RED "❌ Ошибка: Требуется 2 параметра"
    echo ""
    show_help
    exit 1
fi

TAG_NAME="$1"
TAG_DESCRIPTION="$2"

print_color $BLUE "🏷️  Создание тега для проекта"
print_color $BLUE "================================"

# Проверяем, что мы в git репозитории
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_color $RED "❌ Ошибка: Текущая директория не является git репозиторием"
    exit 1
fi

# Проверяем, что тег не существует
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
    print_color $RED "❌ Ошибка: Тег '$TAG_NAME' уже существует"
    echo "Существующие теги:"
    git tag -l | grep -E "^$TAG_NAME" || echo "Нет похожих тегов"
    exit 1
fi

# Показываем информацию о текущем состоянии
print_color $YELLOW "📋 Информация о проекте:"
echo "   Директория: $(pwd)"
echo "   Текущая ветка: $(git branch --show-current)"
echo "   Последний коммит: $(git log -1 --oneline)"
echo "   Статус: $(git status --porcelain | wc -l) измененных файлов"

# Проверяем есть ли неподтвержденные изменения
if [[ -n $(git status --porcelain) ]]; then
    print_color $YELLOW "⚠️  Внимание: Есть неподтвержденные изменения"
    git status --short
    echo ""
    read -p "Продолжить создание тега? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_color $YELLOW "Создание тега отменено пользователем"
        exit 0
    fi
fi

# Показываем что будем делать
print_color $BLUE "🎯 Планируемые действия:"
echo "   1. Создать аннотированный тег '$TAG_NAME'"
echo "   2. Добавить описание: '$TAG_DESCRIPTION'"
echo "   3. Отправить тег на GitHub"
echo ""

# Подтверждение
read -p "Продолжить? (Y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Nn]$ ]]; then
    print_color $YELLOW "Создание тега отменено пользователем"
    exit 0
fi

print_color $BLUE "🚀 Создание тега..."

# Создаем аннотированный тег
print_color $GREEN "📝 Создание аннотированного тега '$TAG_NAME'..."
if git tag -a "$TAG_NAME" -m "$TAG_DESCRIPTION"; then
    print_color $GREEN "✅ Тег '$TAG_NAME' успешно создан"
else
    print_color $RED "❌ Ошибка при создании тега"
    exit 1
fi

# Отправляем тег на GitHub
print_color $GREEN "📤 Отправка тега на GitHub..."
if git push origin "$TAG_NAME"; then
    print_color $GREEN "✅ Тег успешно отправлен на GitHub"
else
    print_color $RED "❌ Ошибка при отправке тега на GitHub"
    print_color $YELLOW "💡 Тег создан локально, но не отправлен на GitHub"
    print_color $YELLOW "    Попробуйте отправить вручную: git push origin $TAG_NAME"
    exit 1
fi

# Показываем информацию о созданном теге
print_color $BLUE "📊 Информация о созданном теге:"
git show "$TAG_NAME" --no-patch --format="   Тег: %D%n   Автор: %an <%ae>%n   Дата: %ad%n   Сообщение: %s%n   Описание: %(trailers)"

print_color $GREEN "🎉 Готово!"
print_color $GREEN "✅ Тег '$TAG_NAME' создан и отправлен на GitHub"
echo ""
print_color $BLUE "🔗 Полезные команды:"
echo "   Просмотр всех тегов: git tag -l"
echo "   Просмотр тега: git show $TAG_NAME"
echo "   Удаление тега (если нужно): git tag -d $TAG_NAME && git push origin :refs/tags/$TAG_NAME"