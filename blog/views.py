from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag

# Create your views here.
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request, tag_slug = None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3)    #trzy posty na stronie
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger: #jezeli zmienna page nie jest l. calkowita, pobierana jest pirewsza strona
        posts = paginator.page(1)
    except EmptyPage:   #jezeli strona jest pusta (za duzy nr), pobiera sie ostatnia strona
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page':page,'posts':posts, 'tag':tag})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    #lista aktywnych komentarzy dla danego posta
    comments = post.comments.filter(active=True)
    if request.method == "POST":
        #komentarz został opublikowany
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            #utworzenie obiektu Comment ale jeszcze nie zapisujemy go w bazie danych
            new_comment = comment_form.save(commit=False)
            #przypisanie komentarza do biezacego posta
            new_comment.post = post
            #zapisanie komentarza w bazie danych
            new_comment.save()

    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post':post, 'comments':comments, "comment_form":comment_form})

def post_share(request, post_id):
    #pobranie posta na podstawie jego id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        #formularz zostal wyslany
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #weryfikacja pól zakonczyla sie powodzeniem
            cd = form.cleaned_data
            #wiec wysyla email
            post_url = request.build_absolute_url(post.get_absolute_url())
            subject = '{} ({}) zacheca do przeczyatania "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Przeczytaj post "{}" na stronie {}\n\n Komentarz dodany przez{}: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            send = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post':post, 'form': form, 'sent': sent})