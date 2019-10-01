from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils.html import escape

from .models import Quote

User = get_user_model()

QUOTES_URLS = {
    'new': lambda: reverse_lazy('quotes:new'),
    'list': lambda: reverse_lazy('quotes:list'),
    'update': lambda pk: reverse_lazy('quotes:update', kwargs={ 'pk': pk }),
    'delete': lambda pk: reverse_lazy('quotes:delete', kwargs={ 'pk': pk }),
    'detail': lambda pk: reverse_lazy('quotes:detail', kwargs={ 'pk': pk }),
}

class TestQuoteJourneys(TestCase):
    fixtures = ['quotes', 'users']

    def test_must_log_in_to_access_quotes(self):
        tiny = User.objects.get(username="tiny")

        res_list = [
            self.client.get(QUOTES_URLS['new'](), follow=True),
            self.client.get(QUOTES_URLS['list'](), follow=True),
            self.client.get(QUOTES_URLS['update'](1), follow=True),
            self.client.get(QUOTES_URLS['delete'](1), follow=True),
            self.client.get(QUOTES_URLS['detail'](1), follow=True),
        ]
        for res in res_list:
            self.assertContains(res, "<h1>Sign In</h1>")

        self.client.force_login(tiny)
        res_list = [
            self.client.get(QUOTES_URLS['new']()),
            self.client.get(QUOTES_URLS['list']()),
            self.client.get(QUOTES_URLS['update'](1)),
            self.client.get(QUOTES_URLS['delete'](1)),
            self.client.get(QUOTES_URLS['detail'](1)),
        ]
        for res in res_list:
            self.assertEqual(200, res.status_code)

    def test_quotes_list_shows_all_quotes(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(QUOTES_URLS['list']())
        for quote in Quote.objects.all():
            self.assertInHTML(escape(quote.text), res.rendered_content)

    def test_can_create_new_quote(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(QUOTES_URLS['new'](), data={'book': 1, 'text': "A new quote", 'page': 567}, follow=True)
        
        # raises a DoesNotExist exception if this query fails
        Quote.objects.get(text='A new quote', page=567)
        self.assertInHTML('<h1>Quotes</h1>', res.rendered_content)
        self.assertInHTML('A new quote', res.rendered_content)

    def test_quotes_detail_shows_quote(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.get(QUOTES_URLS['detail'](1))
        self.assertInHTML(escape("There's a thing that they said"), res.rendered_content)
        res = self.client.get(QUOTES_URLS['detail'](2))
        self.assertInHTML(escape("There's another thing that they said"), res.rendered_content)

    def test_can_update_quote(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(QUOTES_URLS['update'](1), data={'book': 1, 'text': "An updated quote", 'page': 567}, follow=True)
        
        quote = Quote.objects.get(pk=1)
        self.assertEqual('An updated quote', quote.text)
        self.assertInHTML('An updated quote', res.rendered_content)

    def test_can_delete_quote(self):
        tiny = User.objects.get(username="tiny")
        self.client.force_login(tiny)

        res = self.client.post(QUOTES_URLS['delete'](1), follow=True)
        
        quotes = Quote.objects.filter(pk=1)
        self.assertEqual(0, len(quotes))
        self.assertInHTML('<h1>Quotes</h1>', res.rendered_content)
        self.assertNotContains(res, escape("There's a thing that they said"))