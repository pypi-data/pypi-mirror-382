# django-basemodels-rest

Лёгкая интеграция `django-basemodels` с Django REST Framework. Предоставляет готовый `BaseModelSerializer`, который корректно сериализует ключевые поля базовой модели: `pk`, `created_at`, `updated_at`, `active_start`, `active_end`, а также дополнительные вычисляемые поля `is_active` и `polymorphic_ctype`.

## Установка
```bash
# в том же окружении, где установлен django-basemodels и DRF
poetry add django-basemodels-rest
poetry add djangorestframework
```

## Требования
- `django-basemodels`
- `djangorestframework`

## Что даёт пакет
- `BaseModelSerializer` — `ModelSerializer`, который:
  - возвращает `is_active` по свойству `is_active_real` (учёт временных границ и состояния Celery),
  - возвращает `polymorphic_ctype` (`id` типа полиморфной модели),
  - предоставляет базовый набор полей для всех моделей-наследников `BaseModel`.

## Быстрое использование
```python
# serializers.py
from rest_framework import viewsets
from django_basemodels_rest.serializers import BaseModelSerializer
from .models import Article  # Article наследует BaseModel


class ArticleSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Article
        fields = BaseModelSerializer.Meta.fields + ("title", "body")
        writable_fields = ("title", "body")
```

```python
# views.py
from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```

## Расширение / Кастомизация
- Для добавления полей — унаследуйте `BaseModelSerializer` и добавьте нужные поля в `Meta.fields`.
- Для записи указывайте `writable_fields` в `Meta` — по умолчанию сериализатор делает все стандартные поля (`pk`, `created_at`, `updated_at`) только для чтения.


## Примечания по тестированию
- При тестах учитывайте, что `is_active` сериализуется из `is_active_real`. Для моков патчьте ту функцию, которую использует код сериализатора (в зависимости от того, как реализован импорт в `django_basemodels`).
- Подключение пакета в проект не создаёт миграций — используйте миграции ваших моделей-наследников.

## Лицензия
MIT