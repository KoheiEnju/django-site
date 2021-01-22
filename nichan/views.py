from django import template
from nichan.models import Comment
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

# Create your views here.
def index(request):
    text_list = Comment.objects.all().order_by('-pub_date')
    context = {'text_list': text_list}
    return render(request, "nichan/index.html", context)


def detail(request, text_id):
    try:
        text = Comment.objects.get(pk=text_id)
    except Comment.DoesNotExist:
        raise Http404("Comment doesn't eixst.")
    return render(request, "nichan/detail.html", {"text": text})


def post(request):
    text = request.POST["text"]
    name = request.POST["name"]
    Comment.objects.create(text=text, name=name)
    return HttpResponseRedirect(reverse("nichan:index"))