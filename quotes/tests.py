from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils.html import escape
from freezegun import freeze_time

import datetime

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

    def test_quotes_list_shows_20_last_modified_quotes(self):
        for i in range(10, 30):
            with freeze_time(f"2030-01-{i}"):
                new_quote = Quote(
                    book=Book.objects.get(pk=1),
                    page=i,
                    text=f"This is the quote on page {i}"
                )
                new_quote.save()

        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(QUOTES_URLS['list-quote']())
        for i in range(10 ,30):
            self.assertInHTML(f"This is the quote on page {i}", res.rendered_content)
        for quote in Quote.objects.order_by('-modified')[20:]:
            self.assertNotContains(res, escape(quote.text))

    def test_can_create_new_quote(self):
        tiny = User.objects.get(username="tiny")
        with freeze_time('2020-01-01'):
            self.client.force_login(tiny)
            res = self.client.post(QUOTES_URLS['new-quote'](), data={'book': 1, 'text': "A new quote", 'page': 567}, follow=True)
        
        # raises a DoesNotExist exception if this query fails
        quote = Quote.objects.get(text='A new quote', page=567)
        expected_timestamp = datetime.datetime(2020, 1, 1, 0, 0, 0)
        self.assertTrue(all([
            quote.created.year == expected_timestamp.year,
            quote.created.month == expected_timestamp.month,
            quote.created.day == expected_timestamp.day,
            quote.created.hour == expected_timestamp.hour,
            quote.created.minute == expected_timestamp.minute,
        ]))
        self.assertInHTML('<h1>Quotes</h1>', res.rendered_content)
        self.assertInHTML('A new quote', res.rendered_content)

    def test_quotes_detail_shows_quote(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(QUOTES_URLS['detail-quote'](1))
        self.assertInHTML(escape("This is a quote"), res.rendered_content)
        res = self.client.get(QUOTES_URLS['detail-quote'](2))
        self.assertInHTML(escape("This is another quote"), res.rendered_content)

        # related book information
        self.assertInHTML("<dt>Title</dt>", res.rendered_content)
        self.assertInHTML(f"<dd><a class=\"link\" href=\"{reverse_lazy('quotes:detail-book', kwargs={'pk': 1})}\">Sprint</a></dd>", res.rendered_content)
        self.assertInHTML("<dt>Author</dt>", res.rendered_content)
        self.assertInHTML("<dd>Jake Knapp</dd>", res.rendered_content)

    def test_can_update_quote(self):
        tiny = User.objects.get(username="tiny")
        with freeze_time('2020-01-10'):
            self.client.force_login(tiny)
            res = self.client.post(QUOTES_URLS['update-quote'](1), data={'book': 1, 'text': "An modified quote", 'page': 567}, follow=True)
        
        expected_timestamp = datetime.datetime(2020, 1, 10, 0, 0, 0)
        quote = Quote.objects.get(pk=1)
        self.assertTrue(all([
            quote.modified.year == expected_timestamp.year,
            quote.modified.month == expected_timestamp.month,
            quote.modified.day == expected_timestamp.day,
            quote.modified.hour == expected_timestamp.hour,
            quote.modified.minute == expected_timestamp.minute,
        ]))
        self.assertEqual('An modified quote', quote.text)
        self.assertInHTML('An modified quote', res.rendered_content)

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
        with freeze_time('2020-01-01'):
            self.client.force_login(tiny)
            res = self.client.post(BOOKS_URLS['new-book'](), data={'title': "Mr Writer", 'author': 'Ms Writer'}, follow=True)
        
        # raises a DoesNotExist exception if this query fails
        book = Book.objects.get(title='Mr Writer', author='Ms Writer')
        expected_timestamp = datetime.datetime(2020, 1, 1, 0, 0, 0)
        self.assertTrue(all([
            book.created.year == expected_timestamp.year,
            book.created.month == expected_timestamp.month,
            book.created.day == expected_timestamp.day,
            book.created.hour == expected_timestamp.hour,
            book.created.minute == expected_timestamp.minute,
        ]))
        self.assertInHTML('<h1>Books</h1>', res.rendered_content)
        self.assertInHTML('Mr Writer', res.rendered_content)

    def test_books_detail_contains_all_book_information(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(BOOKS_URLS['detail-book'](1))
        self.assertInHTML(escape("Sprint"), res.rendered_content)
        res = self.client.get(BOOKS_URLS['detail-book'](2))
        self.assertInHTML(escape("Another book"), res.rendered_content)

        # all related quotes
        self.assertInHTML(escape("This book sucks"), res.rendered_content)
        self.assertInHTML(escape("Actually it's quite good"), res.rendered_content)
        self.assertInHTML(escape("No wait, it definitely sucks"), res.rendered_content)

    def test_can_update_book(self):
        tiny = User.objects.get(username="tiny")
        with freeze_time('2020-01-10'):
            self.client.force_login(tiny)
            res = self.client.post(BOOKS_URLS['update-book'](1), data={'title': "Big Guns", 'author': 'Arnold Schwarzenegger'}, follow=True)
        
        book = Book.objects.get(pk=1)
        expected_timestamp = datetime.datetime(2020, 1, 10, 0, 0, 0)
        self.assertTrue(all([
            book.modified.year == expected_timestamp.year,
            book.modified.month == expected_timestamp.month,
            book.modified.day == expected_timestamp.day,
            book.modified.hour == expected_timestamp.hour,
            book.modified.minute == expected_timestamp.minute,
        ]))
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
