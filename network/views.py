import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, Follow, MAX_POST_LENGTH


def index(request):
    return render(request, "network/index.html", {
        
    })

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
        return JsonResponse({"error": "Post should be {MAX_POST_LENGTH} characters or less"}, status=400)
    else:
        return JsonResponse({"message": "New Post successful."}, status=201)
    
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
            return JsonResponse({"error": "Post should be {MAX_POST_LENGTH} characters or less"}, status=400)
        else:
            return JsonResponse({"message": "Post update successful."}, status=201)
    
    # Update must be via PUT
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


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
