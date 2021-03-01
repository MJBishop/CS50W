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
    return render(request, "encyclopedia/entry.html", {
        "entry": markdown2.markdown(util.get_entry(title))
    })

