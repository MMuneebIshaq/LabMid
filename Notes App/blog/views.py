from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .forms import CreateViewForm, UpdateViewForm

# enabling case-insensitive search in MySQL databases
from django.db.models import Q, TextField
from django.db.models.functions import Lower
TextField.register_lookup(Lower, "lower")


# if users are allowed to view anyone's posts, not only theirs, then leave this and the next class uncommented
class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts' # the name of a context variable with the queryset results
    ordering = ['-date_posted']
    paginate_by = 20

    # modifying the function for returning posts
    def get_queryset(self):
        # if there is a search query in the URL parameter, then use it to filter the results
        search_query = self.request.GET.get('search', '')
        # using Q for case-insensitive search in a MySQL database
        queryset = Post.objects.filter(Q(content__lower__contains=search_query)).order_by('-date_posted')
        return queryset


class PostDetailView(DetailView):
    model = Post



class PostCreateView(CreateView):
    model = Post
    form_class = CreateViewForm # making the class use an existing form with pre-defined validation rules
    template_name = 'blog/post_create.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# if users are allowed to update or delete anyone's posts, not only theirs, then leave this and the next class uncommented
class PostUpdateView(UpdateView):
    model = Post
    template_name = 'blog/post_update.html'
    form_class = UpdateViewForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_delete.html'


def csrf_failure(request, reason=""):
    current_page = request.path
    try:
        if '/post/new' in current_page:
            return PostCreateView.as_view()(request)
        elif '/update' in current_page:
            return PostUpdateView.as_view()(request)
        elif '/delete' in current_page:
            return PostDeleteView.as_view()(request)
        # redirect to the homepage in any other case, e.g. after login
        else:
            return HttpResponseRedirect('/')
    # if there was any error in calling the respective function, then redirect to the homepage
    except:
        return HttpResponseRedirect('/')
