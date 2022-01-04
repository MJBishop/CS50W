import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt #best way??

from .models import User, Post, Follow, MAX_POST_LENGTH


def index(request):

    # fetch all posts
    posts = Post.objects.posts_from_all_users()

    # page_obj (Paginator)
    page = request.GET.get('page', 1)
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page)

    return render(request, "network/index.html", {
        "page_obj": page_obj,
    })

@login_required
def following(request):

    if request.method == "GET":
        # fetch all posts from users follwed by user
        posts = Post.objects.posts_from_users_followed_by_user(user=request.user)#pass in the user?

        # page_obj (Paginator)
        page = request.GET.get('page', 1)
        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(page)

        return render(request, "network/index.html", {
            "page_obj": page_obj,
        })
    else:
        return HttpResponseRedirect(reverse("index"))


def profile(request, user_id):

    if request.method == "GET":
        # Query for requested User
        profile = get_object_or_404(User, pk=user_id)

        # fetch all posts from user
        posts = Post.objects.posts_from_user(user=profile)

        # page_obj (Paginator)
        page = request.GET.get('page', 1)
        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(page)

        return render(request, "network/index.html", {
            "page_obj": page_obj,
            "profile":profile
        })
    else:
        return HttpResponseRedirect(reverse("index"))

@csrf_exempt
@login_required
def new_post(request):

    # Creating a new post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Unpack Post text from request.body
    data = json.loads(request.body)
    post_text = data.get("text", "")

    # Create the Post
    try:
        Post.objects.create_post(request.user, post_text)
    except ValidationError:
        return JsonResponse({"validation_error": f"Post should be {MAX_POST_LENGTH} characters or less"}, status=400)
    else:
        return JsonResponse({"message": "New Post successful."}, status=201)


@csrf_exempt
@login_required
def update_post(request, post_id):

    # Query for requested Post
    try:
        post = Post.objects.get(user=request.user, pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "PUT":
        # Unpack Post text from request.body
        data = json.loads(request.body)
        post_text = data.get("text", "")

        # Update the Post
        try:
            post.update(request.user, post_text)
        except ValidationError:
            return JsonResponse({"validation_error": f"Post should be {MAX_POST_LENGTH} characters or less"}, status=400)
        else:
            return JsonResponse({"message": "Post update successful."}, status=201)
    
    # Update must be via PUT
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


@csrf_exempt
@login_required
def like_post(request, post_id):
    
    # Query for requested Post
    try:
        post = Post.objects.get(user=request.user, pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # toggle post like for user
    if request.method == "PUT":
        like_count = post.toggle_like(user=request.user)
        return JsonResponse({"message": "Post update successful.", "likes": like_count}, status=201)

    # Update must be via PUT
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


@login_required
def follow(request, user_id):

    # Creating a new follow must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Query for requested User
    try:
        user_to_follow = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    # Create follow
    try:
        Follow.objects.create_follow(from_user=request.user, to_user=user_to_follow)
    except:
        return JsonResponse({"error": f'{request.user} is already following {user_to_follow}'}, status=400)
    else:
        return JsonResponse({"message": "New Follow successful."}, status=201)


@login_required
def unfollow(request, user_id):
    
    # Deleting a follow must be via DELETE
    if request.method != "DELETE":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Query for requested User
    try:
        user_to_unfollow = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    # Delete follow
    try:
        Follow.objects.delete_follow(from_user=request.user, to_user=user_to_unfollow)
    except:
        return JsonResponse({"error": f'{request.user} is not following {user_to_unfollow}'}, status=400)
    else:
        return JsonResponse({"message": "Unfollow successful."}, status=201)


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
