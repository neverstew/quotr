from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.urls import reverse_lazy
from django.views import generic

from .models import Quote, Book
from .forms import QuoteSearchForm


class IndexView(generic.base.TemplateView):
    template_name = 'quotr/index.html'

class ListQuoteView(LoginRequiredMixin, generic.ListView):
    paginate_by = 20

    def get_queryset(self):
        quotes = Quote.objects.filter(created_by=self.request.user).order_by('-modified')
        if 'search' in self.request.GET and self.request.GET['search']:
            query = SearchQuery(self.request.GET['search'])
            vector = SearchVector('text', 'book__title', 'book__author')
            quotes = quotes.annotate(search=vector, rank=SearchRank(vector, query)).filter(search=self.request.GET['search']).order_by('-rank')

        return quotes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = QuoteSearchForm(self.request.GET)
        return context
    
class DetailQuoteView(LoginRequiredMixin, generic.DetailView):
    def get_queryset(self):
        return Quote.objects.filter(created_by=self.request.user)

class NewQuoteView(LoginRequiredMixin, generic.CreateView):
    model = Quote
    fields = ['book', 'text', 'page']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class UpdateQuoteView(LoginRequiredMixin, generic.UpdateView):
    fields = ['book', 'text', 'page']
    
    def get_queryset(self):
        return Quote.objects.filter(created_by=self.request.user)

class DeleteQuoteView(LoginRequiredMixin, generic.DeleteView):
    success_url = reverse_lazy('quotes:list-quote')

    def get_queryset(self):
        return Quote.objects.filter(created_by=self.request.user)



class ListBookView(LoginRequiredMixin, generic.ListView):
    paginate_by = 20
    ordering = '-modified'

    def get_queryset(self):
        return Book.objects.filter(created_by=self.request.user)
    
class DetailBookView(LoginRequiredMixin, generic.DetailView):
    def get_queryset(self):
        return Book.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quotes'] = Quote.objects.filter(book=self.get_object())
        return context

class NewBookView(LoginRequiredMixin, generic.CreateView):
    model = Book
    fields = ['title', 'author']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class UpdateBookView(LoginRequiredMixin, generic.UpdateView):
    fields = ['title', 'author']

    def get_queryset(self):
        return Book.objects.filter(created_by=self.request.user)

class DeleteBookView(LoginRequiredMixin, generic.DeleteView):
    success_url = reverse_lazy('quotes:list-book')

    def get_queryset(self):
        return Book.objects.filter(created_by=self.request.user)
