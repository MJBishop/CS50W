import markdown2
import random 
from django import forms
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from . import util

#Form Class
class TextAreaForm(forms.Form):
    entryField = forms.CharField(widget=forms.Textarea, label='')
class TitleAndTextAreaForm(forms.Form):
    titleField = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Title'}), label = '')
    entryField = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Entry'}), label='')


def search(request):
    search_string = request.GET.get("q")
    if len(search_string) > 0:
        partial_matches = []
        for title in util.list_entries():
            if title == search_string:
                return render(request, "encyclopedia/entry.html", {
                    "entry": markdown2.markdown(util.get_entry(title)),
                    "title": title
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
        return HttpResponseRedirect(reverse("encyclopedia:index"))


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
        "entry": markdown2.markdown(entry),
        "title": title
    })

def randomEntry(request):
    entryList = random.sample(util.list_entries(), 1)
    title = entryList[0]
    if title == None:
        raise Http404("Entry not found")
    entry = util.get_entry(title)
    return render(request, "encyclopedia/entry.html", {
        "entry": markdown2.markdown(entry),
        "title": title
    })

def edit(request, title):
    if request.method == "POST":
        form = TextAreaForm(request.POST)
        if form.is_valid():
            # Save the edited Entry
            entry = form.cleaned_data["entryField"]
            util.save_entry(title, entry)
            # Redirect back to entry page
            # return HttpResponseRedirect(reverse("encyclopedia:entry", args=(title,)))
        # else:
            # Throw exception?
        return HttpResponseRedirect(reverse("encyclopedia:entry", args=(title,)))

    entry = util.get_entry(title)
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": TextAreaForm(initial={'entryField': entry})
    })

def add(request):
    if request.method == "POST":
        form = TitleAndTextAreaForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["titleField"]
            entry = util.get_entry(title)
            if entry != None:
                raise Http404("Entry not found")
            else:
                entry = form.cleaned_data["entryField"]
                util.save_entry(title, entry) 
                return HttpResponseRedirect(reverse("encyclopedia:entry", args=(title,)))
        return HttpResponseRedirect(reverse("encyclopedia:add"))

    return render(request, "encyclopedia/new.html", {
        "title": "",
        "form": TitleAndTextAreaForm()
    })
