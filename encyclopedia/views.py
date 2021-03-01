from django.http import HttpResponse, Http404
import markdown2
from django.shortcuts import render

from . import util


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

