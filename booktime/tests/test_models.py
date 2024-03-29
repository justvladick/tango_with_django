from booktime import models
from decimal import Decimal
from django.test import TestCase


class TestModel(TestCase):
    def test_create_order_works(self):
        p1 = models.Product.objects.create(
            name="The cathedral and the bazaar",
            price=Decimal("10.00"),
        )
        p2 = models.Product.objects.create(
            name="Pride and Prejudice", price=Decimal("2.00")
        )
        user1 = models.User.objects.create_user(
            "user1", "pw432joij"
        )
        billing = models.Address.objects.create(
            user=user1,
            name="John Kimball",
            address1="127 Strudel road",
            city="London",
            country="uk",
        )
        shipping = models.Address.objects.create(
            user=user1,
            name="John Kimball",
            address1="123 Deacon road",
            city="London",
            country="uk",
        )
        basket = models.Basket.objects.create(user=user1)
        models.BasketLine.objects.create(
            basket=basket, product=p1
        )
        models.BasketLine.objects.create(
            basket=basket, product=p2
        )
        with self.assertLogs("booktime.models", level="INFO") as cm:
            order = basket.create_order(billing, shipping)
        self.assertGreaterEqual(len(cm.output), 1)
        order.refresh_from_db()
        self.assertEquals(order.user, user1)
        self.assertEquals(
            order.billing_address1, "127 Strudel road"
        )
        self.assertEquals(
            order.shipping_address1, "123 Deacon road"
        )
        # add more checks here
        self.assertEquals(order.orderline_set.all().count(), 2)
        lines = order.orderline_set.all()
        self.assertEquals(lines[0].product, p1)
        self.assertEquals(lines[1].product, p2)
