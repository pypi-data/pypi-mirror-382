from django.db import connection, models
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import include, path

from pfx.pfxcore import register_views
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.models import OrderedModelMixin, PFXModelMixin
from pfx.pfxcore.test import APIClient, TestAssertMixin
from pfx.pfxcore.views import OrderedRestViewMixin, RestView
from tests.models import Author, User
from tests.views import FakeViewMixin


class OrderedModel(PFXModelMixin, OrderedModelMixin, models.Model):
    name = models.CharField("Name", max_length=30)

    class Meta:
        verbose_name = "OrderedModel"
        verbose_name_plural = "OrderedModels"
        ordering = ['seq', 'pk']

    def __str__(self):
        return self.name


class OrderedByNameModel(PFXModelMixin, OrderedModelMixin, models.Model):
    ordered_by = ['name']

    name = models.CharField("Name", max_length=30)

    class Meta:
        verbose_name = "OrderedByNameModel"
        verbose_name_plural = "OrderedByNameModels"
        ordering = ['name', 'seq', 'pk']

    def __str__(self):
        return f"{self.name} / {self.seq}"


class OrderedByNameFirstModel(PFXModelMixin, OrderedModelMixin, models.Model):
    ordered_default = 'first'
    ordered_by = ['name']

    name = models.CharField("Name", max_length=30)

    class Meta:
        verbose_name = "OrderedByNameModel"
        verbose_name_plural = "OrderedByNameModels"
        ordering = ['name', 'seq', 'pk']

    def __str__(self):
        return f"{self.name} / {self.seq}"


class OrderedByFkModel(PFXModelMixin, OrderedModelMixin, models.Model):
    ordered_by = ['ref']

    ref = models.ForeignKey(
        OrderedModel, verbose_name="OrderedModel",
        related_name='+', on_delete=models.RESTRICT)

    class Meta:
        verbose_name = "OrderedByFkModel"
        verbose_name_plural = "OrderedByFkModels"
        ordering = ['ref', 'seq', 'pk']

    def __str__(self):
        return f"{self.ref.name} / {self.seq}"


@rest_view("/ordered")
class OrderedModelRestView(FakeViewMixin, OrderedRestViewMixin, RestView):
    default_public = True
    model = OrderedModel
    fields = ['name', 'seq']


@rest_view("/ordered-by-name")
class OrderedByNameModelRestView(
        FakeViewMixin, OrderedRestViewMixin, RestView):
    default_public = True
    model = OrderedByNameModel
    fields = ['name', 'seq']


@rest_view("/ordered-by-fk")
class OrderedByFkModelRestView(FakeViewMixin, OrderedRestViewMixin, RestView):
    default_public = True
    model = OrderedByFkModel
    fields = ['ref', 'seq']


@rest_view("/ordered-authors")
class OrderedAuthorRestView(FakeViewMixin, OrderedRestViewMixin, RestView):
    default_public = True
    model = Author


class conf:
    urlpatterns = [
        path('api/', include(register_views(
            OrderedModelRestView,
            OrderedByNameModelRestView,
            OrderedByFkModelRestView,
        ))),
        path('api/', include('pfx.pfxcore.urls'))
    ]


class conf_failed:
    urlpatterns = [
        path('api/', include(register_views(
            OrderedAuthorRestView,
        ))),
        path('api/', include('pfx.pfxcore.urls'))
    ]


def order(model):
    return list(model.objects.all().values_list('pk', flat=True))


@override_settings(ROOT_URLCONF=conf)
class TestOrderedRestViewMixin(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(OrderedModel)
            schema_editor.create_model(OrderedByNameModel)
            schema_editor.create_model(OrderedByNameFirstModel)
            schema_editor.create_model(OrderedByFkModel)
        cls.user = User.objects.create_user(
            username='jrr.tolkien',
            email="jrr.tolkien@oxford.com",
            password='RIGHT PASSWORD',
            first_name='John Ronald Reuel',
            last_name='Tolkien',
        )
        cls.o1 = OrderedModel.objects.create(name='A')
        cls.o2 = OrderedModel.objects.create(name='A')
        cls.o3 = OrderedModel.objects.create(name='A')
        cls.obn1 = OrderedByNameModel.objects.create(name='AAA')
        cls.obn2 = OrderedByNameModel.objects.create(name='BBB')
        cls.obn3 = OrderedByNameModel.objects.create(name='BBB')
        cls.obnf1 = OrderedByNameFirstModel.objects.create(name='AAA')
        cls.obnf2 = OrderedByNameFirstModel.objects.create(name='BBB')
        cls.obnf3 = OrderedByNameFirstModel.objects.create(name='BBB')
        cls.obfk1 = OrderedByFkModel.objects.create(ref=cls.o1)
        cls.obfk2 = OrderedByFkModel.objects.create(ref=cls.o2)
        cls.obfk3 = OrderedByFkModel.objects.create(ref=cls.o2)

    def test_default_values(self):
        response = self.client.get('/api/ordered?items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)
        self.assertJE(response, 'items.@0.pk', self.o1.pk)
        self.assertJE(response, 'items.@1.pk', self.o2.pk)
        self.assertJE(response, 'items.@2.pk', self.o3.pk)
        self.assertJE(response, 'items.@0.seq', 1)
        self.assertJE(response, 'items.@1.seq', 2)
        self.assertJE(response, 'items.@2.seq', 3)

    def test_default_values_by_name(self):
        response = self.client.get('/api/ordered-by-name?items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)
        self.assertJE(response, 'items.@0.pk', self.obn1.pk)
        self.assertJE(response, 'items.@1.pk', self.obn2.pk)
        self.assertJE(response, 'items.@2.pk', self.obn3.pk)
        self.assertJE(response, 'items.@0.seq', 1)
        self.assertJE(response, 'items.@1.seq', 1)
        self.assertJE(response, 'items.@2.seq', 2)

    def test_default_values_by_fk(self):
        response = self.client.get('/api/ordered-by-fk?items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)
        self.assertJE(response, 'items.@0.pk', self.obfk1.pk)
        self.assertJE(response, 'items.@1.pk', self.obfk2.pk)
        self.assertJE(response, 'items.@2.pk', self.obfk3.pk)
        self.assertJE(response, 'items.@0.seq', 1)
        self.assertJE(response, 'items.@1.seq', 1)
        self.assertJE(response, 'items.@2.seq', 2)

    def test_up(self):
        response = self.client.put(
            f'/api/ordered/{self.o3.pk}?move=up', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedModel),
            [self.o1.pk, self.o3.pk, self.o2.pk])

        # Check do nothings if first
        response = self.client.put(
            f'/api/ordered/{self.o1.pk}?move=up', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedModel),
            [self.o1.pk, self.o3.pk, self.o2.pk])

    def test_up_by_name(self):
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn3.pk}?move=up', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByNameModel),
            [self.obn1.pk, self.obn3.pk, self.obn2.pk])

        # Check do nothings if first
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn3.pk}?move=up', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByNameModel),
            [self.obn1.pk, self.obn3.pk, self.obn2.pk])

    def test_up_by_fk(self):
        response = self.client.put(
            f'/api/ordered-by-fk/{self.obfk3.pk}?move=up', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByFkModel),
            [self.obfk1.pk, self.obfk3.pk, self.obfk2.pk])

        # Check do nothings if first
        response = self.client.put(
            f'/api/ordered-by-fk/{self.obfk3.pk}?move=up', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByFkModel),
            [self.obfk1.pk, self.obfk3.pk, self.obfk2.pk])

    def test_down(self):
        response = self.client.put(
            f'/api/ordered/{self.o2.pk}?move=down', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedModel),
            [self.o1.pk, self.o3.pk, self.o2.pk])

        # Check do nothings if last
        response = self.client.put(
            f'/api/ordered/{self.o2.pk}?move=down', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedModel),
            [self.o1.pk, self.o3.pk, self.o2.pk])

    def test_down_by_name(self):
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn2.pk}?move=down', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByNameModel),
            [self.obn1.pk, self.obn3.pk, self.obn2.pk])

        # Check do nothings if last
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn2.pk}?move=down', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByNameModel),
            [self.obn1.pk, self.obn3.pk, self.obn2.pk])

    def test_down_by_fk(self):
        response = self.client.put(
            f'/api/ordered-by-fk/{self.obfk2.pk}?move=down', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByFkModel),
            [self.obfk1.pk, self.obfk3.pk, self.obfk2.pk])

        # Check do nothings if last
        response = self.client.put(
            f'/api/ordered-by-fk/{self.obfk2.pk}?move=down', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByFkModel),
            [self.obfk1.pk, self.obfk3.pk, self.obfk2.pk])

    def test_top(self):
        response = self.client.put(
            f'/api/ordered/{self.o3.pk}?move=top', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedModel),
            [self.o3.pk, self.o1.pk, self.o2.pk])

        # Check do nothings if first
        response = self.client.put(
            f'/api/ordered/{self.o3.pk}?move=top', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedModel),
            [self.o3.pk, self.o1.pk, self.o2.pk])

    def test_top_by_name(self):
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn3.pk}?move=top', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByNameModel),
            [self.obn1.pk, self.obn3.pk, self.obn2.pk])

        # Check do nothings if first
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn3.pk}?move=top', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByNameModel),
            [self.obn1.pk, self.obn3.pk, self.obn2.pk])

    def test_top_by_fk(self):
        response = self.client.put(
            f'/api/ordered-by-fk/{self.obfk3.pk}?move=top', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByFkModel),
            [self.obfk1.pk, self.obfk3.pk, self.obfk2.pk])

        # Check do nothings if first
        response = self.client.put(
            f'/api/ordered-by-fk/{self.obfk3.pk}?move=top', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByFkModel),
            [self.obfk1.pk, self.obfk3.pk, self.obfk2.pk])

    def test_bottom(self):
        response = self.client.put(
            f'/api/ordered/{self.o1.pk}?move=bottom', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedModel),
            [self.o2.pk, self.o3.pk, self.o1.pk])

        # Check do nothings if last
        response = self.client.put(
            f'/api/ordered/{self.o1.pk}?move=bottom', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedModel),
            [self.o2.pk, self.o3.pk, self.o1.pk])

    def test_bottom_by_name(self):
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn2.pk}?move=bottom', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByNameModel),
            [self.obn1.pk, self.obn3.pk, self.obn2.pk])

        # Check do nothings if last
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn2.pk}?move=bottom', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByNameModel),
            [self.obn1.pk, self.obn3.pk, self.obn2.pk])

    def test_bottom_by_fk(self):
        response = self.client.put(
            f'/api/ordered-by-fk/{self.obfk2.pk}?move=bottom', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByFkModel),
            [self.obfk1.pk, self.obfk3.pk, self.obfk2.pk])

        # Check do nothings if last
        response = self.client.put(
            f'/api/ordered-by-fk/{self.obfk2.pk}?move=bottom', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByFkModel),
            [self.obfk1.pk, self.obfk3.pk, self.obfk2.pk])

    def test_above(self):
        response = self.client.put(
            f'/api/ordered/{self.o3.pk}?move=above&object={self.o2.pk}', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedModel),
            [self.o1.pk, self.o3.pk, self.o2.pk])

    def test_above_by_name(self):
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn3.pk}'
            f'?move=above&object={self.obn2.pk}', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByNameModel),
            [self.obn1.pk, self.obn3.pk, self.obn2.pk])

    def test_above_by_fk(self):
        response = self.client.put(
            f'/api/ordered-by-fk/{self.obfk3.pk}'
            f'?move=above&object={self.obfk2.pk}', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByFkModel),
            [self.obfk1.pk, self.obfk3.pk, self.obfk2.pk])

    def test_below(self):
        response = self.client.put(
            f'/api/ordered/{self.o1.pk}?move=below&object={self.o2.pk}', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedModel),
            [self.o2.pk, self.o1.pk, self.o3.pk])

    def test_below_by_name(self):
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn2.pk}'
            f'?move=below&object={self.obn3.pk}', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByNameModel),
            [self.obn1.pk, self.obn3.pk, self.obn2.pk])

    def test_below_by_fk(self):
        response = self.client.put(
            f'/api/ordered-by-fk/{self.obfk2.pk}'
            f'?move=below&object={self.obfk3.pk}', {})
        self.assertRC(response, 200)

        self.assertEqual(
            order(OrderedByFkModel),
            [self.obfk1.pk, self.obfk3.pk, self.obfk2.pk])

    @override_settings(ROOT_URLCONF=conf_failed)
    def test_no_ordered_mode_mixin_view(self):
        with self.assertRaises(TypeError):
            self.client.get('/api/ordered-authors')

    def test_missing_object_param(self):
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn3.pk}?move=above', {})
        self.assertRC(response, 400)

    def test_object_other_order_parent(self):
        response = self.client.put(
            f'/api/ordered-by-name/{self.obn3.pk}'
            f'?move=above&object={self.obn1.pk}', {})
        self.assertRC(response, 400)

    def test_create_default(self):
        response = self.client.post(
            '/api/ordered-by-name', dict(name='BBB'))
        self.assertRC(response, 200)
        self.assertJE(response, 'seq', 3)

    def test_model_ordered_default(self):
        self.obn3.name = self.obn1.name
        self.obn3.save()
        self.obn3.refresh_from_db()
        self.assertEqual(self.obn3.seq, 2)

        self.obnf3.name = self.obnf1.name
        self.obnf3.save()
        self.obnf3.refresh_from_db()
        self.assertEqual(self.obnf3.seq, 1)
