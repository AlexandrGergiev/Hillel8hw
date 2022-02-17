from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import Book, Author, BookInstance, Genre
from .forms import ReserveBookForm
from typing import Any

import datetime


# Create your views here.


class AuthorCreateView(generic.CreateView):
    model = Author
    fields = "__all__"
    initial = {
        "date_of_death": "11/03/2009",
    }


class AuthorUpdateView(generic.UpdateView):
    model = Author
    fields = "__all__"
    initial = {
        "date_of_death": "11/03/2009",
    }


class AuthorDeleteView(generic.DeleteView):
    model = Author

    def delete_author(request, author_id):
        model = Author(request)
        author = get_object_or_404(Author, id=author_id)
        model.remove(author)
        return HttpResponseRedirect("/")


# def delete(self, request):
#     if request.method == 'POST':
#         form = AuthorDeleteForm(request.POST)
#         if form.is_valid():
#             form.save()
#             redirect('authors')


class BookListView(generic.ListView):
    model = Book
    context_object_name = "book_list"
    queryset = Book.objects.all()
    template_name = "book/list.html"

    # def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
    #     return super().get_context_data(**kwargs) | {"book_list": Book.objects.all()}


class BookDetailView(generic.DetailView):
    model = Book
    template_name = "book/detail.html"


class AuthorListView(generic.ListView):
    model = Author
    context_object_name = "author_list"
    queryset = Author.objects.all()
    template_name = "author/list.html"


class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = "author/detail.html"


VISITS_KEY = "visits"


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()
    num_authors = Author.objects.all().count()

    num_visits = request.session.get(VISITS_KEY, 0)
    request.session[VISITS_KEY] = num_visits + 1

    return render(
        request,
        "index.html",
        context={
            "num_books": num_books,
            "num_instances": num_instances,
            "num_instances_available": num_instances_available,
            "num_authors": num_authors,
            "num_visits": num_visits,
        },
    )


def reserve_book_form(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == "POST":
        form = ReserveBookForm(request.POST)

        if form.is_valid():
            # Perform action
            book_instance.status = "r"
            book_instance.due_back = form.cleaned_data["return_date"]

            book_instance.save()

            # Redirect to success url
            return HttpResponseRedirect("/")

    else:
        proposed_return_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = ReserveBookForm(initial={"return_date": proposed_return_date})

    return render(
        request,
        "book/reserve.html",
        {"form": form, "book_instance": book_instance},
    )
