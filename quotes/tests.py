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
        bigboii = User.objects.get(username="bigboii")

        res_list = [
            self.client.get(QUOTES_URLS['new-quote'](), follow=True),
            self.client.get(QUOTES_URLS['list-quote'](), follow=True),
            self.client.get(QUOTES_URLS['update-quote'](1), follow=True),
            self.client.get(QUOTES_URLS['delete-quote'](1), follow=True),
            self.client.get(QUOTES_URLS['detail-quote'](1), follow=True),
        ]
        for res in res_list:
            self.assertContains(res, "<h1>Sign In</h1>")

        self.client.force_login(bigboii)
        res_list = [
            self.client.get(QUOTES_URLS['new-quote']()),
            self.client.get(QUOTES_URLS['list-quote']()),
            self.client.get(QUOTES_URLS['update-quote'](1)),
            self.client.get(QUOTES_URLS['delete-quote'](1)),
            self.client.get(QUOTES_URLS['detail-quote'](1)),
        ]
        for res in res_list:
            self.assertEqual(200, res.status_code)

    def test_quotes_list_shows_placeholder_when_no_quotes(self):
        new_user = User(username='fresh')
        new_user.save()

        self.client.force_login(new_user)
        res = self.client.get(QUOTES_URLS['list-quote']())

        self.assertInHTML("<p>You don't seem to have any quotes saved yet! Add some using the button below.</p>", res.rendered_content)

    def test_quotes_list_shows_20_last_modified_quotes(self):
        tiny = User.objects.get(username="tiny")
        for i in range(10, 30):
            with freeze_time(f"2030-01-{i}"):
                new_quote = Quote(
                    book=Book.objects.get(pk=1),
                    page=i,
                    text=f"This is the quote on page {i}",
                    created_by=tiny
                )
                new_quote.save()

        bigboii = User.objects.get(username='bigboii')
        with freeze_time(f"2030-02-01"):
            new_quote = Quote(
                book=Book.objects.get(pk=1),
                page=24,
                text=f"This is the quote by bigboii",
                created_by=bigboii
            )
            new_quote.save()

        self.client.force_login(tiny)
        res = self.client.get(QUOTES_URLS['list-quote']())
        for i in range(10 ,30):
            self.assertInHTML(f"This is the quote on page {i}", res.rendered_content)
        
        self.assertNotContains(res, escape("This is the quote on page 9"))
        self.assertNotContains(res, escape("This is the quote by bigboii"))

    def test_quotes_list_can_be_searched(self):
        bigboii = User.objects.get(username='bigboii')
        self.client.force_login(bigboii)

        # search by quote text
        res = self.client.get(QUOTES_URLS['list-quote']()+'?search=another')
        self.assertNotContains(res, '<blockquote>This is a quote</blockquote>')
        self.assertInHTML('<blockquote>This is another quote</blockquote>', res.rendered_content)
        self.assertInHTML('<input type="text" name="search" value="another" placeholder="Search" maxlength="200" id="id_search">', res.rendered_content)

        #search by book title
        res = self.client.get(QUOTES_URLS['list-quote']()+'?search=Sprint')
        self.assertInHTML('<blockquote>This is a quote</blockquote>', res.rendered_content)
        self.assertInHTML('<blockquote>This is another quote</blockquote>', res.rendered_content)

        #search by book author
        res = self.client.get(QUOTES_URLS['list-quote']()+'?search=Jake%20Knapp')
        self.assertInHTML('<blockquote>This is a quote</blockquote>', res.rendered_content)
        self.assertInHTML('<blockquote>This is another quote</blockquote>', res.rendered_content)

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
        self.assertEqual(tiny, quote.created_by)
        self.assertInHTML('A new quote', res.rendered_content)
    
    def test_quotes_detail_shows_quote(self):
        bigboii = User.objects.get(username="bigboii")
        self.client.force_login(bigboii)

        res = self.client.get(QUOTES_URLS['detail-quote'](1))
        self.assertInHTML(escape("This is a quote"), res.rendered_content)
        res = self.client.get(QUOTES_URLS['detail-quote'](2))
        self.assertInHTML(escape("This is another quote"), res.rendered_content)

        # related book information
        self.assertInHTML("<dt>Title</dt>", res.rendered_content)
        self.assertInHTML(f"<dd><a class=\"link\" href=\"{reverse_lazy('quotes:detail-book', kwargs={'pk': 1})}\">Sprint</a></dd>", res.rendered_content)
        self.assertInHTML("<dt>Author</dt>", res.rendered_content)
        self.assertInHTML("<dd>Jake Knapp</dd>", res.rendered_content)

    def test_cannot_see_quote_detail_for_another_user(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(QUOTES_URLS['detail-quote'](1))
        self.assertEqual(404, res.status_code)        

    def test_can_update_quote(self):
        bigboii = User.objects.get(username="bigboii")
        with freeze_time('2020-01-10'):
            self.client.force_login(bigboii)
            res = self.client.post(QUOTES_URLS['update-quote'](1), data={'book': 1, 'text': "A modified quote", 'page': 567}, follow=True)
        
        expected_timestamp = datetime.datetime(2020, 1, 10, 0, 0, 0)
        quote = Quote.objects.get(pk=1)
        self.assertTrue(all([
            quote.modified.year == expected_timestamp.year,
            quote.modified.month == expected_timestamp.month,
            quote.modified.day == expected_timestamp.day,
            quote.modified.hour == expected_timestamp.hour,
            quote.modified.minute == expected_timestamp.minute,
        ]))
        self.assertEqual('A modified quote', quote.text)
        self.assertInHTML('A modified quote', res.rendered_content)

    def test_cannot_update_quote_for_another_user(self):
        tiny = User.objects.get(username="tiny")
        with freeze_time('2020-01-10'):
            self.client.force_login(tiny)
            res = self.client.post(QUOTES_URLS['update-quote'](1), data={'book': 1, 'text': "A modified quote", 'page': 567}, follow=True)
        
        self.assertEqual(404, res.status_code)

    def test_can_delete_quote(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(QUOTES_URLS['delete-quote'](3), follow=True)
        
        quotes = Quote.objects.filter(pk=3)
        self.assertEqual(0, len(quotes))
        self.assertInHTML('<h1>Quotes</h1>', res.rendered_content)
        self.assertNotContains(res, escape("There's a thing that they said"))

    def test_cannot_delete_quote_for_another_user(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)
        res = self.client.post(QUOTES_URLS['delete-quote'](1), follow=True)
        
        self.assertEqual(404, res.status_code)

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
        bigboii = User.objects.get(username="bigboii")

        res_list = [
            self.client.get(BOOKS_URLS['new-book'](), follow=True),
            self.client.get(BOOKS_URLS['list-book'](), follow=True),
            self.client.get(BOOKS_URLS['update-book'](1), follow=True),
            self.client.get(BOOKS_URLS['delete-book'](1), follow=True),
            self.client.get(BOOKS_URLS['detail-book'](1), follow=True),
        ]
        for res in res_list:
            self.assertContains(res, "<h1>Sign In</h1>")

        self.client.force_login(bigboii)
        res_list = [
            self.client.get(BOOKS_URLS['new-book']()),
            self.client.get(BOOKS_URLS['list-book']()),
            self.client.get(BOOKS_URLS['update-book'](1)),
            self.client.get(BOOKS_URLS['delete-book'](1)),
            self.client.get(BOOKS_URLS['detail-book'](1)),
        ]
        for res in res_list:
            self.assertEqual(200, res.status_code)

    def test_books_list_shows_placeholder_when_no_quotes(self):
        new_user = User(username='fresh')
        new_user.save()

        self.client.force_login(new_user)
        res = self.client.get(BOOKS_URLS['list-book']())

        self.assertInHTML("<p>You don't seem to have any books saved yet! Add some using the button below.</p>", res.rendered_content)

    def test_books_list_shows_20_last_modified_books(self):
        tiny = User.objects.get(username="tiny")
        for i in range(10, 31):
            with freeze_time(f"2030-01-{i}"):
                new_book = Book(
                    title=f"Book {i}",
                    author=f"Ms. Writer",
                    created_by=tiny
                )
                new_book.save()

        bigboii = User.objects.get(username='bigboii')
        with freeze_time(f"2030-02-01"):
            new_book = Book(
                title=f"Big life",
                author=f"Big Boii",
                created_by=bigboii
            )
            new_book.save()

        self.client.force_login(tiny)
        res = self.client.get(BOOKS_URLS['list-book']())
        for i in range(30, 10, -1):
            self.assertInHTML(f"Book {i}", res.rendered_content)
        self.assertNotContains(res, escape("Book 10"))
        self.assertNotContains(res, escape("Big Life"))
        
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
        self.assertEqual(tiny, book.created_by)
        self.assertInHTML('Mr Writer', res.rendered_content)

    def test_books_detail_contains_all_book_information(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(BOOKS_URLS['detail-book'](3))
        self.assertInHTML(escape("Brand new book"), res.rendered_content)
        res = self.client.get(BOOKS_URLS['detail-book'](2))
        self.assertInHTML(escape("Another book"), res.rendered_content)

        # all related quotes
        self.assertInHTML(escape("This book sucks"), res.rendered_content)
        self.assertInHTML(escape("Actually it's quite good"), res.rendered_content)
        self.assertInHTML(escape("No wait, it definitely sucks"), res.rendered_content)

    def test_cannot_get_detail_on_another_users_book(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(BOOKS_URLS['detail-book'](1))
        self.assertEqual(404, res.status_code)
    
    def test_can_update_book(self):
        tiny = User.objects.get(username="tiny")
        with freeze_time('2020-01-10'):
            self.client.force_login(tiny)
            res = self.client.post(BOOKS_URLS['update-book'](2), data={'title': "Big Guns", 'author': 'Arnold Schwarzenegger'}, follow=True)
        
        book = Book.objects.get(pk=2)
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

    def test_cannot_update_another_users_book(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(BOOKS_URLS['update-book'](1), data={'title': "Big Guns", 'author': 'Arnold Schwarzenegger'}, follow=True)
        self.assertEqual(404, res.status_code)
    
    def test_can_delete_book(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(BOOKS_URLS['delete-book'](2), follow=True)
        
        books = Book.objects.filter(pk=2)
        self.assertEqual(0, len(books))
        self.assertInHTML('<h1>Books</h1>', res.rendered_content)
        self.assertNotContains(res, escape("Sprint"))

    def test_cannot_delete_another_users_book(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(BOOKS_URLS['delete-book'](1), follow=True)
        self.assertEqual(404, res.status_code)