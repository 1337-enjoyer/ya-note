from http import HTTPStatus
from turtle import title

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Author')
        cls.non_author = User.objects.create(username='Non Author')
        cls.note = Note.objects.create(
            title='Title',
            text='text',
            slug='slug',
            author=cls.author
        )

    def test_main_page_availability(self):
        url = reverse('notes:home', args=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_note_add_edit_delete(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.non_author, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)