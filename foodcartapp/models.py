from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)

    def available_restaurants(self):
        return self.menu_items.filter(availability=True).restaurant.all()


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def price(self):
        return self.annotate(price=Sum(F('order_items__quantity')
                                       * F('order_items__price_fixed')))


class Order(models.Model):
    STATUS_CHOICES = [
        ('proc', 'В обработке'),
        ('cook', 'Готовится'),
        ('dlvr', 'Передан в доставку'),
        ('end', 'Завершен'),
    ]

    PAYMENT_CHOICES = [
        ('epay', 'Электронно'),
        ('cash', 'Наличностью'),
    ]

    firstname = models.CharField(
        max_length=100,
        blank=False,
        verbose_name='Имя',
    )

    lastname = models.CharField(
        max_length=100,
        blank=False,
        verbose_name='Фамилия',
    )

    phonenumber = PhoneNumberField(blank=False,
                                   verbose_name='Телефон')

    address = models.CharField(blank=False,
                               max_length=200,
                               verbose_name='Адрес доставки')

    created_at = models.DateTimeField(verbose_name="Дата и время создания",
                                      auto_now_add=True,
                                      db_index=True)

    called_at = models.DateTimeField(verbose_name="Дата и время звонка",
                                     null=True,
                                     blank=True)

    delivered_at = models.DateTimeField(verbose_name="Дата и время доставки",
                                        null=True,
                                        blank=True)

    status = models.CharField(max_length=4,
                              choices=STATUS_CHOICES,
                              verbose_name='Статус')

    comment = models.TextField(blank=True,
                               default='',
                               verbose_name='Комментарий')

    payment_type = models.CharField(max_length=4,
                                    default='cash',
                                    choices=PAYMENT_CHOICES,
                                    verbose_name='Способ оплаты')

    restaurant = models.ForeignKey(Restaurant,
                                   blank=True,
                                   null=True,
                                   related_name='order',
                                   verbose_name="Ресторан",
                                   on_delete=models.SET_NULL,
                                   )

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        indexes = [
            models.Index(fields=['status', 'payment_type']),
        ]

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.address} #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='order_items',
                              verbose_name='заказ')
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='order_items',
                                verbose_name='товар')
    quantity = models.IntegerField(default=1,
                                   verbose_name='количество')
    price_fixed = models.DecimalField(max_digits=8,
                                      decimal_places=2,
                                      blank=False,
                                      default=0,
                                      verbose_name='цена товара в заказе',
                                      validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.product.name}"
