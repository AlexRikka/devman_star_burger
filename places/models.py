from django.db import models


class Place(models.Model):
    name = models.CharField(
        'Название',
        max_length=50
    )
    address = models.CharField(
        'Адрес',
        max_length=100,
    )

    lat = models.FloatField(verbose_name='Широта')
    lon = models.FloatField(verbose_name='Долгота')

    last_updated_at = models.DateField(verbose_name="Дата запроса к геокодеру",
                                       db_index=True)

    class Meta:
        verbose_name = 'Место на карте'
        verbose_name_plural = 'Места на карте'

    def __str__(self):
        return self.name
