from django.test import TestCase
from booktime import models
from django.core.files.images import ImageFile
from decimal import Decimal


class TestSignal(TestCase):
    def test_thumbnails_are_generated_on_save(self):
        product = models.Product(
            name="The cathedral and the bazaar",
            price=Decimal("10.00"),
        )
        product.save()
        with open(
                "booktime/fixtures/the-cathedral-the-bazaar.jpg", "rb"
        ) as f:
            image = models.ProductImage(
                product=product,
                image=ImageFile(f, name="tctb.jpg"),
            )
            with self.assertLogs("booktime", level="INFO") as cm:
                image.save()
                self.assertGreaterEqual(len(cm.output), 1)
                image.refresh_from_db()
        with open(
                "booktime/fixtures/the-cathedral-the-bazaar.thumb.jpg",
                "rb",
        ) as f:
            expected_content = f.read()
            assert image.thumbnail.read() == expected_content
        image.thumbnail.delete(save=False)
        image.image.delete(save=False)


class TestModel(TestCase):
    def test_active_manager_works(self):
        models.Product.objects.create(
            name="The cathedral and the bazaar",
            price=Decimal("10.00"))
        models.Product.objects.create(
            name="Pride and Prejudice",
            price=Decimal("2.00"))
        models.Product.objects.create(
            name="A Tale of Two Cities",
            price=Decimal("2.00"),
            active=False)
        self.assertEqual(len(models.Product.objects.active()), 2)
