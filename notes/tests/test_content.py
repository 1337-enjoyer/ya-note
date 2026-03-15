from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Author')
        cls.another_author = User.objects.create(username='Non Author')
        cls.note = Note.objects.create(
            title='Title',
            text='text',
            slug='slug',
            author=cls.author
        )
        cls.another_note = Note.objects.create(
            title='Another title',
            text='Another text',
            slug='Another-slug',
            author=cls.another_author
        )

    def test_note_in_obj_list_context(self):
        self.client.force_login(self.author)
        url = reverse('notes:list', args=None)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_only_for_author(self):
        for user, expected, unexpected in [
            (self.author, self.note, self.another_note),
            (self.another_author, self.another_note, self.note),
        ]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                notes = self.client.get(
                    reverse('notes:list')).context['object_list']

                self.assertIn(expected, notes)
                self.assertNotIn(unexpected, notes)
                self.assertEqual(notes.count(), 1)

    def test_forms_creating(self):
        self.client.force_login(self.author)
        urls = [
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
