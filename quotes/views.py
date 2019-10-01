from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from .models import Quote, Book

class IndexView(generic.base.TemplateView):
    template_name = 'quotr/index.html'

class ListQuoteView(LoginRequiredMixin, generic.ListView):
    model = Quote
    paginate_by = 20
    ordering = '-modified'
    
class DetailQuoteView(LoginRequiredMixin, generic.DetailView):
    model = Quote

class NewQuoteView(LoginRequiredMixin, generic.CreateView):
    model = Quote
    fields = ['book', 'text', 'page']
    success_url = reverse_lazy('quotes:list-quote')

class UpdateQuoteView(LoginRequiredMixin, generic.UpdateView):
    model = Quote
    fields = ['book', 'text', 'page']

class DeleteQuoteView(LoginRequiredMixin, generic.DeleteView):
    model = Quote
    success_url = reverse_lazy('quotes:list-quote')


class ListBookView(LoginRequiredMixin, generic.ListView):
    model = Book
    paginate_by = 20
    
class DetailBookView(LoginRequiredMixin, generic.DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quotes'] = Quote.objects.filter(book=self.get_object())
        return context

class NewBookView(LoginRequiredMixin, generic.CreateView):
    model = Book
    fields = ['title', 'author']
    success_url = reverse_lazy('quotes:list-book')

class UpdateBookView(LoginRequiredMixin, generic.UpdateView):
    model = Book
    fields = ['title', 'author']

class DeleteBookView(LoginRequiredMixin, generic.DeleteView):
    model = Book
    success_url = reverse_lazy('quotes:list-book')
