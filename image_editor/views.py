from django.shortcuts import render


def home(r):
    return render(r, "home.html")


def faq(r):
    return render(r, "faq.html")
