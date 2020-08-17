from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm

# Create your views here.
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)    #trzy posty na stronie
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger: #jezeli zmienna page nie jest l. calkowita, pobierana jest pirewsza strona
        posts = paginator.page(1)
    except EmptyPage:   #jezeli strona jest pusta (za duzy nr), pobiera sie ostatnia strona
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page':page,'posts':posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    return render(request, 'blog/post/detail.html', {'post':post})

def post_share(request, post_id):
    #pobranie posta na podstawie jego id
    post = get_object_or_404(Post, id=post_id, status='published')
    if request.method == 'POST':
        #formularz zostal wyslany
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #weryfikacja pól zakonczyla sie powodzeniem
            cd = form.cleaned_data
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post':post, 'form': form})