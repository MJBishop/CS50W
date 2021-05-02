import markdown2
import random 
from django import forms
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from . import util

'''
TextAreaForm for editing an entry
'''
class TextAreaForm(forms.Form):
    entryField = forms.CharField(widget=forms.Textarea, label='')

'''
TitleAndTextAreaForm for adding an entry
'''
class TitleAndTextAreaForm(forms.Form):
    titleField = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Title'}), label = '')
    entryField = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Entry'}), label='')


'''
Returns the entry of an exact match, or a list of partial matches.
'''
def search(request):
    search_string = request.GET.get("q")
    if len(search_string) > 0:
        partial_matches = []
        for title in util.list_entries():
            if title == search_string:
                # return the matching entry
                return render(request, "encyclopedia/entry.html", {
                    "entry": markdown2.markdown(util.get_entry(title)),
                    "title": title
            })
            elif search_string in title:
                # add to partial matches
                partial_matches += [title]
        # return partial matches
        return render(request, "encyclopedia/search.html", {
            "entries": partial_matches,
            "search": search_string
        })
    else:
        return HttpResponseRedirect(reverse("encyclopedia:index"))


'''
Returns all entries.
'''
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


'''
Returns the entry of a given title.
Raises HTTP404 if entry not found.
'''
def entry(request, title):
    entry = util.get_entry(title)
    if entry == None:
        raise Http404("Entry not found")
    return render(request, "encyclopedia/entry.html", {
        "entry": markdown2.markdown(entry),
        "title": title
    })

'''
Returns a random entry
'''
def randomEntry(request):
    entryList = random.sample(util.list_entries(), 1)
    title = entryList[0]
    if title == None:
        raise Http404("Entry not found")
    return HttpResponseRedirect(reverse("encyclopedia:entry", args=(title,)))

'''
Returns the edit view of an entry with form populated with the entry.
POST saves the valid form
'''
def edit(request, title):
    if request.method == "POST":
        form = TextAreaForm(request.POST)
        if form.is_valid():
            # Save the edited Entry
            entry = form.cleaned_data["entryField"]
            util.save_entry(title, entry)
        return HttpResponseRedirect(reverse("encyclopedia:entry", args=(title,)))

    entry = util.get_entry(title)
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": TextAreaForm(initial={'entryField': entry})
    })

'''
Returns the edit view with an empty form.
POST saves the valid form data as an entry. Display a  message if the entry already exists.
'''
def add(request):
    if request.method == "POST":
        form = TitleAndTextAreaForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["titleField"]
            currentEntry = util.get_entry(title)
            if currentEntry != None:
                return render(request, "encyclopedia/new.html", {
                    "title": "",
                    "form": form,
                    "message": "This Page already exists!"
                })
            else:
                entry = form.cleaned_data["entryField"]
                util.save_entry(title, entry) 
                return HttpResponseRedirect(reverse("encyclopedia:entry", args=(title,)))
        return HttpResponseRedirect(reverse("encyclopedia:add"))

    return render(request, "encyclopedia/new.html", {
        "title": "",
        "form": TitleAndTextAreaForm()
    })
