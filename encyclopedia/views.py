from django.shortcuts import render, redirect
from django import forms
import random
from markdown import Markdown
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from . import util


class SearchForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        "class": "search",
        "placeholder": "Search MD Wiki"
    }))


class CreateForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        "placeholder": "Page Title"}))
    text = forms.CharField(label='', widget=forms.Textarea(attrs={
        "placeholder": "Enter Page Content using Github Markdown"
    }))


class EditForm(forms.Form):
    text = forms.CharField(label='', widget=forms.Textarea(attrs={
        "placeholder": "Enter Page Content using Github Markdown"
    }))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "searchForm": SearchForm(),
    })


def entry(request, title):
    entryMD = util.get_entry(title)

    if entryMD is not None:
        entryHTML = Markdown().convert(entryMD)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": entryHTML,
            "searchForm": SearchForm(),
        })
    else:
        relatedTitles = util.relatedTitles(title)

        return render(request, "encyclopedia/error.html", {
            "title": title,
            "relatedTitles": relatedTitles,
            "searchForm": SearchForm(),
        })


def search(request):
    """ Loads the requested title otherwise returns search results"""

    if request.method == "POST":
        form = SearchForm(request.POST)

    if form.is_valid():
        title = form.cleaned_data["title"]
        entryMD = util.get_entry(title)

        print('search request: ', title)

        if entryMD:
            return redirect(reverse('entry', args=[title]))
        else:
            relatedTitles = util.relatedTitles(title)

            return render(request, "encyclopedia/search.html", {
                "title": title,
                "relatedTitles": relatedTitles,
                "searchForm": SearchForm()
            })
    return redirect(reverse('index'))


def create(request):
    # If reached Create Entry via link
    if request.method == "GET":
        return render(request, "encyclopedia/create.html", {
            "createForm": CreateForm(),
            "searchForm": SearchForm()
        })
    # Else if reached Create Entry via form
    elif request.method == "POST":
        form = CreateForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
        else:
            messages.error(request, 'Entry form is not valid, please try again!')
            return render(request, "encyclopedia/create.html"), {
                "createForm": form,
                "searchForm": SearchForm()
            }

        # Check that the title does not exist
        if util.get_entry(title):
            messages.error(request, 'This page already exists!')
            return render(request, "encyclopedia/create.html", {
                "createForm": form,
                "searchForm": SearchForm()
            })


def edit(request, title):
    # If reached via editing link, return form with post to edit
    if request.method == "GET":
        text = util.get_entry(title)

        # If title does not exist already, return error
        if text is None:
            messages.error(request, f'"{title}" page does not exist and cannot be edited, please create a new page instead!')

        # Otherwise return form
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "editForm": EditForm(initial={'text': text}),
            "searchForm": SearchForm()
        })


def randomTitle(request):

    # Gets list of titles, picks one at random
    titles = util.list_entries()
    title = random.choice(titles)
    return redirect(reverse('entry', args=[title]))
