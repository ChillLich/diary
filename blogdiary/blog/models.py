from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class MostCommonFieldsModel(models.Model):
    """Абстрактная модель. Добвляет:
    флаг is_published,
    дату создания записи created_at,
    """

    is_published = models.BooleanField(
        verbose_name="Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)

    class Meta:
        abstract = True


class Location(MostCommonFieldsModel):
    name = models.CharField(
        verbose_name="Название места",
        max_length=256,
        default="Планета Земля",
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Category(MostCommonFieldsModel):
    title = models.CharField(verbose_name="Название категории", max_length=256)
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        verbose_name="Идентификатор",
        max_length=64,
        unique=True,
        help_text=(
            "Идентификатор страницы для URL; "
            "разрешены символы латиницы, цифры, дефис и подчёркивание."
        ),
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Post(MostCommonFieldsModel):
    title = models.CharField(verbose_name="Заголовок", max_length=256)
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text="Если установить дату и время в будущем — можно делать отложенные публикации.",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="post",
        verbose_name="Категория",
        null=True,
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        related_name="post",
        verbose_name="Местоположение",
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post",
        verbose_name="Автор публикации",
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ("-pub_date", "title")

    def __str__(self):
        return self.title
