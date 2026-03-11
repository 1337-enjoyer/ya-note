from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestLogic(TestCase):

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
        cls.form_data = {
            'title': 'test title',
            'text': 'test text',
            'slug': 'test-slug',
        }

        cls.form_data_without_slug = {
            'title': 'test title',
            'text': 'test text',
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(reverse('notes:add'), data=self.form_data)
        nots_count = Note.objects.count()
        self.assertEqual(nots_count, 2)

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        self.client.post(reverse('notes:add'), data=self.form_data)
        nots_count = Note.objects.count()
        self.assertEqual(nots_count, 3)

    def test_cant_create_some_same_slugs(self):
        self.client.force_login(self.author)
        self.client.post(reverse('notes:add'), data=self.form_data)
        self.client.post(reverse('notes:add'), data=self.form_data)
        nots_count = Note.objects.count()
        self.assertEqual(nots_count, 3)

    def test_auto_add_slug_for_empty_field(self):
        self.client.force_login(self.author)
        self.client.post(reverse('notes:add'),
                         data=self.form_data_without_slug)
        nots_count = Note.objects.count()
        self.assertEqual(nots_count, 3)
        note = Note.objects.get(title=self.form_data_without_slug['title'])
        self.assertEqual(note.slug, 'test-title')

    def test_user_can_edit_delete_only_own_notes(self):
        self.client.force_login(self.author)
        self