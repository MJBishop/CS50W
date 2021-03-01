import markdown2
from django.http import HttpResponse, Http404
# from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from . import util


def search(request):
    search_string = request.GET.get("q")
    if len(search_string) > 0:
        # print("search string: " + search_string)
        partial_matches = []
        for title in util.list_entries():
            if title == search_string:
                return render(request, "encyclopedia/entry.html", {
                    "entry": markdown2.markdown(util.get_entry(title))
            })
            elif search_string in title:
                partial_matches += [title]
        if len(partial_matches) > 0:
            return render(request, "encyclopedia/search.html", {
                "entries": partial_matches,
                "search": search_string
            })
        else:
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries()
        })
    else:
        return HttpResponseRedirect(reverse("index"))
        # return render(request, "encyclopedia/index.html", {
        #     "entries": util.list_entries()
        # })


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


# Entry View
# Returns the entry of a given title
def entry(request, title):
    entry = util.get_entry(title)
    if entry == None:
        raise Http404("Entry not found")
    return render(request, "encyclopedia/entry.html", {
        "entry": markdown2.markdown(entry)
    })

