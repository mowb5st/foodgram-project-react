from django.test import Client, TestCase
from http import HTTPStatus
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(email='testcase@test.com',
                                       usenrame='testname',
                                       first_name='test_first_name',
                                       last_name='test_last_name',
                                       password='testpass')

    def test_user_creation(self):
        """Проверяем что юзер успешно создан"""
        obj_user = User.objects.filter(username='testname')
        print(obj_user)
        # self.assertEqual()
