from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils.html import escape

from .models import Quote, Book

User = get_user_model()

QUOTES_URLS = {
    'new-quote': lambda: reverse_lazy('quotes:new-quote'),
    'list-quote': lambda: reverse_lazy('quotes:list-quote'),
    'update-quote': lambda pk: reverse_lazy('quotes:update-quote', kwargs={ 'pk': pk }),
    'delete-quote': lambda pk: reverse_lazy('quotes:delete-quote', kwargs={ 'pk': pk }),
    'detail-quote': lambda pk: reverse_lazy('quotes:detail-quote', kwargs={ 'pk': pk }),
}

class TestQuoteJourneys(TestCase):
    fixtures = ['quotes', 'users']

    def test_must_log_in_to_access_quotes(self):
        tiny = User.objects.get(username="tiny")

        res_list = [
            self.client.get(QUOTES_URLS['new-quote'](), follow=True),
            self.client.get(QUOTES_URLS['list-quote'](), follow=True),
            self.client.get(QUOTES_URLS['update-quote'](1), follow=True),
            self.client.get(QUOTES_URLS['delete-quote'](1), follow=True),
            self.client.get(QUOTES_URLS['detail-quote'](1), follow=True),
        ]
        for res in res_list:
            self.assertContains(res, "<h1>Sign In</h1>")

        self.client.force_login(tiny)
        res_list = [
            self.client.get(QUOTES_URLS['new-quote']()),
            self.client.get(QUOTES_URLS['list-quote']()),
            self.client.get(QUOTES_URLS['update-quote'](1)),
            self.client.get(QUOTES_URLS['delete-quote'](1)),
            self.client.get(QUOTES_URLS['detail-quote'](1)),
        ]
        for res in res_list:
            self.assertEqual(200, res.status_code)

    def test_quotes_list_shows_all_quotes(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(QUOTES_URLS['list-quote']())
        for quote in Quote.objects.all():
            self.assertInHTML(escape(quote.text), res.rendered_content)

    def test_can_create_new_quote(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(QUOTES_URLS['new-quote'](), data={'book': 1, 'text': "A new quote", 'page': 567}, follow=True)
        
        # raises a DoesNotExist exception if this query fails
        Quote.objects.get(text='A new quote', page=567)
        self.assertInHTML('<h1>Quotes</h1>', res.rendered_content)
        self.assertInHTML('A new quote', res.rendered_content)

    def test_quotes_detail_shows_quote(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(QUOTES_URLS['detail-quote'](1))
        self.assertInHTML(escape("There's a thing that they said"), res.rendered_content)
        res = self.client.get(QUOTES_URLS['detail-quote'](2))
        self.assertInHTML(escape("There's another thing that they said"), res.rendered_content)

    def test_can_update_quote(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(QUOTES_URLS['update-quote'](1), data={'book': 1, 'text': "An updated quote", 'page': 567}, follow=True)
        
        quote = Quote.objects.get(pk=1)
        self.assertEqual('An updated quote', quote.text)
        self.assertInHTML('An updated quote', res.rendered_content)

    def test_can_delete_quote(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(QUOTES_URLS['delete-quote'](1), follow=True)
        
        quotes = Quote.objects.filter(pk=1)
        self.assertEqual(0, len(quotes))
        self.assertInHTML('<h1>Quotes</h1>', res.rendered_content)
        self.assertNotContains(res, escape("There's a thing that they said"))

BOOKS_URLS = {
    'new-book': lambda: reverse_lazy('quotes:new-book'),
    'list-book': lambda: reverse_lazy('quotes:list-book'),
    'update-book': lambda pk: reverse_lazy('quotes:update-book', kwargs={ 'pk': pk }),
    'delete-book': lambda pk: reverse_lazy('quotes:delete-book', kwargs={ 'pk': pk }),
    'detail-book': lambda pk: reverse_lazy('quotes:detail-book', kwargs={ 'pk': pk }),
}

class TestBookJourneys(TestCase):
    fixtures = ['quotes', 'users']

    def test_must_log_in_to_access_books(self):
        tiny = User.objects.get(username="tiny")

        res_list = [
            self.client.get(BOOKS_URLS['new-book'](), follow=True),
            self.client.get(BOOKS_URLS['list-book'](), follow=True),
            self.client.get(BOOKS_URLS['update-book'](1), follow=True),
            self.client.get(BOOKS_URLS['delete-book'](1), follow=True),
            self.client.get(BOOKS_URLS['detail-book'](1), follow=True),
        ]
        for res in res_list:
            self.assertContains(res, "<h1>Sign In</h1>")

        self.client.force_login(tiny)
        res_list = [
            self.client.get(BOOKS_URLS['new-book']()),
            self.client.get(BOOKS_URLS['list-book']()),
            self.client.get(BOOKS_URLS['update-book'](1)),
            self.client.get(BOOKS_URLS['delete-book'](1)),
            self.client.get(BOOKS_URLS['detail-book'](1)),
        ]
        for res in res_list:
            self.assertEqual(200, res.status_code)

    def test_books_list_shows_all_books(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(BOOKS_URLS['list-book']())
        for book in Book.objects.all():
            self.assertInHTML(escape(book.title), res.rendered_content)

    def test_can_create_new_book(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(BOOKS_URLS['new-book'](), data={'title': "Mr Writer", 'author': 'Ms Writer'}, follow=True)
        
        # raises a DoesNotExist exception if this query fails
        Book.objects.get(title='Mr Writer', author='Ms Writer')
        self.assertInHTML('<h1>Books</h1>', res.rendered_content)
        self.assertInHTML('Mr Writer', res.rendered_content)

    def test_books_detail_shows_book(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(BOOKS_URLS['detail-book'](1))
        self.assertInHTML(escape("Sprint"), res.rendered_content)
        res = self.client.get(BOOKS_URLS['detail-book'](2))
        self.assertInHTML(escape("Another book"), res.rendered_content)

    def test_can_update_book(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(BOOKS_URLS['update-book'](1), data={'title': "Big Guns", 'author': 'Arnold Schwarzenegger'}, follow=True)
        
        book = Book.objects.get(pk=1)
        self.assertEqual('Big Guns', book.title)
        self.assertInHTML('Big Guns', res.rendered_content)

    def test_can_delete_book(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(BOOKS_URLS['delete-book'](1), follow=True)
        
        books = Book.objects.filter(pk=1)
        self.assertEqual(0, len(books))
        self.assertInHTML('<h1>Books</h1>', res.rendered_content)
        self.assertNotContains(res, escape("Sprint"))
