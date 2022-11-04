#!-*-coding:utf-8-*-
import base64
import json
import tempfile

from PIL import Image
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import Ingredient, Tag, Recipe, Subscription
from users.models import User


class CommonTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='admin',
            password='admin',
            first_name='egor',
            last_name='letov',
        )
        cls.api_client = APIClient()
        cls.token = Token.objects.create(user=cls.user)

    def setUp(self) -> None:
        self.api_client.force_authenticate(user=self.user, token=self.token)


class ReciepeViewTestCase(CommonTestCase):
    """Тест api рецептов."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('api:recipes-list')

    def setUp(self) -> None:
        super().setUp()

        self.amount = 22
        self.ing_salt = Ingredient.objects.create(
            name='salt',
            measurement_unit='g'
        )
        self.tag1 = Tag.objects.create(
            name='tag1',
            color='red',
            slug='tag1',
        )
        self.tag2 = Tag.objects.create(
            name='tag2',
            color='blue',
            slug='tag2',
        )

        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image = Image.new('RGB', (100, 100))
        image.save(self.tmp_file.name)

        # self.api_client.force_authenticate(user=self.user, token=self.token)

    def create_recipe(self, **kw):
        data = {
            'name': 'salat',
            'text': 'text',
            'cooking_time': 4,
            'author': self.user,
        }
        data.update(kw)

        recipe = Recipe.objects.create(**data)

        recipe.tags.add(self.tag1)
        recipe.ingredients.add(
            self.ing_salt,
            through_defaults={'amount': self.amount}
        )
        return recipe