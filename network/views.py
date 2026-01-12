from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from .models import Post, Follower, Like


def index(request):
    if request.method == 'POST':
        text = request.POST['new_post']
        Post.objects.create(user=request.user, text=text)
    posts = Post.objects.order_by('-date')
    return render(request, "network/index.html", {'page_obj': pages(posts, request.GET.get('page')), 'posts_likes': get_likes(request, posts)})

@login_required(login_url='login')
def get_likes(request, posts):
    posts_likes = []
    for post in posts:
        for like in post.likes.filter(post = post, user = request.user):
            posts_likes.append(like.post)
    return posts_likes

def pages(posts, page_number):
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page_number)
    return page_obj

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    
def profile(request, user_id):
    post_user = User.objects.get(id=user_id)
    if request.method == 'POST':
        if post_user != request.user and followed(request, post_user):
            followed(request, post_user).delete()
            return redirect('profile', user_id)
        else:
            Follower.objects.create(leader=post_user, follower = request.user)
            return redirect('profile', user_id)
    following = False
    if followed(request, post_user):
        following = True
    return render(request, 'network/profile.html', {'post_user': post_user, 'page_obj': pages(post_user.posts.order_by('-date'), request.GET.get('page')), 'followers': post_user.leader.count(), 'followings': post_user.follower.count(), 'following': following, 'posts_likes': get_likes(request, post_user.posts.order_by('-date'))})

def followed(request, post_user):
    for follower in post_user.leader.all():
        if follower.follower == request.user:
            return follower
    return False

@login_required(login_url='login')
def edit(request, post_id):
    post = Post.objects.get(id=post_id)
    if post.user == request.user:
        if request.method == 'POST':
            post.text = request.POST['edited_text']
            post.save()
            return redirect('profile', post.user.id)
        return render(request, 'network/edit.html', {'post': post})
    return HttpResponseNotFound('You can not edit others post')

@login_required(login_url='login')
def like(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user
    for i in range(post.likes.all().count()):
        if(post.likes.all()[i].user == user):
            Like.objects.get(post=post, user=user).delete()
            return JsonResponse({'likes': post.likes.all().count()})
    Like.objects.create(post=post, user=user, like=1)
    return JsonResponse({'likes': post.likes.all().count()})

@login_required(login_url='login')
def following_posts(request):
    posts = []
    for post in Post.objects.order_by('-date'):
        for follower in request.user.follower.all():
            if post.user == follower.leader:
                posts.append(post)
    return render(request, 'network/following_posts.html', {'page_obj': pages(posts, request.GET.get('page')), 'posts_likes': get_likes(request, posts)})