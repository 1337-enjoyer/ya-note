from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

from notes.forms import WARNING

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
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        nots_count = Note.objects.count()
        self.assertEqual(nots_count, 2)

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        nots_count = Note.objects.count()
        self.assertEqual(nots_count, 3)
        new_note = Note.objects.latest('id')
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_cant_create_some_same_slugs(self):
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertFormError(
            response.context['form'],
            'slug',
            self.note.slug + WARNING
            )
        nots_count = Note.objects.count()
        self.assertEqual(nots_count, 2)

    def test_auto_add_slug_for_empty_field(self):
        self.client.force_login(self.author)
        self.client.post(reverse('notes:add'),
                         data=self.form_data_without_slug)
        nots_count = Note.objects.count()
        self.assertEqual(nots_count, 3)
        note = Note.objects.get(title=self.form_data_without_slug['title'])
        self.assertEqual(note.slug, 'test-title')

    def test_author_can_edit_and_delete_own_note(self):
        self.client.force_login(self.author)
        initial_count = Note.objects.count()
        edit_url = reverse('notes:edit', args=[self.note.slug])
        response = self.client.post(edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        delete_url = reverse('notes:delete', args=[self.note.slug])
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), initial_count - 1)
        with self.assertRaises(Note.DoesNotExist):
            self.note.refresh_from_db()

    def test_user_cannot_edit_or_delete_foreign_note(self):
        self.client.force_login(self.author)
        initial_count = Note.objects.count()
        original_title = self.another_note.title
        original_text = self.another_note.text
        edit_url = reverse('notes:edit', args=[self.another_note.slug])
        response = self.client.post(edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.another_note.refresh_from_db()
        self.assertEqual(self.another_note.title, original_title)
        self.assertEqual(self.another_note.text, original_text)
        delete_url = reverse('notes:delete', args=[self.another_note.slug])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertTrue(Note.objects.filter(
            slug=self.another_note.slug).exists())
