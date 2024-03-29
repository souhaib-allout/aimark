import datetime

import cv2
from django.contrib.auth.models import User
from django.core.files.storage import Storage
from django.core.mail import send_mail
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.templatetags.static import static
from rest_framework.response import Response

from marks.forms import MarkForm
from marks.models import *

import cv2 as cv


def home(request):
    if request.user.is_authenticated == True:
        # print(cv.__version__)
        lastmarks = Mark.objects.filter(created_at=datetime.today())
        nbmarks = Mark.objects.all().count()
        nbusers = User.objects.all().count()
        nbpoints = Point.objects.all().count()
        greenmarks = Mark.objects.filter(Q(gravity__lte=30) & Q(created_at=datetime.today())).count()
        yellowmarks = Mark.objects.filter(
            Q(gravity__gt=30) & Q(gravity__lt=70) & Q(created_at=datetime.today())).count()
        redmarks = Mark.objects.filter(Q(gravity__gte=70) & Q(created_at=datetime.today())).count()

        todaygravities = {'greenmarks': greenmarks, 'yellowmarks': yellowmarks, 'redmarks': redmarks}

        greenmarks = Mark.objects.filter(gravity__lte=30).count()
        yellowmarks = Mark.objects.filter(Q(gravity__gt=30) & Q(gravity__lt=70)).count()
        redmarks = Mark.objects.filter(gravity__gte=70).count()
        gravitieschart = {'greenmarks': greenmarks, 'yellowmarks': yellowmarks, 'redmarks': redmarks}

        userchart = User.objects.select_related().annotate(nb=Count('marks'))
        data = {'lastmarks': lastmarks, 'nbmarks': nbmarks, 'gravitieschart': gravitieschart,
                'nbusers': nbusers, 'nbpoints': nbpoints, 'todaygravities': todaygravities,
                'userchart':userchart}

        return render(request, 'index.html', data)
    else:
        return redirect('/admins/login')


def index(request):
    if request.user.is_authenticated == False:
        return redirect('/admins/login')

    data = Mark.objects.all()
    return render(request, 'mark/index.html', {'data': data})


def add(request):
    if request.user.is_authenticated == False:
        return redirect('/admins/login')

    if request.method == 'POST':
        form = MarkForm(request.POST, request.FILES)
        # form.user=request.user.id
        # form.created_at=datetime.date.today()
        if form.is_valid():
            mark = Mark(user=User.objects.get(id=request.user.id), name=form.cleaned_data['title']
                        , desctiption=form.cleaned_data['desctiption'], image=form.cleaned_data['image']
                        , gravity=form.cleaned_data['gravity'] * 10, created_at=datetime.today())
            mark.save()
            mailmessage = request.user.username + " added a mark thats have the id " + str(mark.id)
            mail(request, 'Mark added', mailmessage)

            return redirect('/admins/marks/edit/' + str(mark.id))
        else:
            return render(request, 'mark/add.html', {'form': form})

    else:
        form = MarkForm()
        return render(request, 'mark/add.html', {'form': form})


def edit(request, id):
    if request.user.is_authenticated == False:
        return redirect('/admins/login')

    mark = Mark.objects.get(id=id)
    if request.method == 'POST':
        form = MarkForm(request.POST, request.FILES)
        if form.is_valid():

            # mark.user = request.user.id
            mark.name = form.cleaned_data['title']
            mark.desctiption = form.cleaned_data['desctiption']
            if form.cleaned_data['image']:
                mark.image = form.cleaned_data['image']

            mark.gravity = form.cleaned_data['gravity'] * 10
            mark.descx = form.cleaned_data['descx']
            mark.descy = form.cleaned_data['descy']
            mailmessage = request.user.username + " edited a mark thats have the id " + str(id)

            mail(request, 'Mark edited', mailmessage)

            mark.save()

            return redirect('/admins/marks/edit/' + str(id))
        else:
            return render(request, 'mark/edit.html', {'form': form})

    else:
        form = MarkForm(initial={
            'id': mark.id,
            'user': mark.user,
            'title': mark.name,
            'desctiption': mark.desctiption,
            'image': mark.image,
            'gravity': mark.gravity / 10,
            'descx': mark.descx,
            'descy': mark.descy,
            'created_at': mark.created_at,
        })
        points = Point.objects.filter(mark=id)

        return render(request, 'mark/edit.html', {'form': form, 'points': points})


def delete(request):
    if request.user.is_authenticated == False:
        return redirect('/admins/login')

    if request.method == 'POST':
        mark = Mark.objects.get(id=request.POST['markid'])
        mark.delete()
        mailmessage = request.user.username + " deleted a mark thats have the id " + request.POST['markid']
        mail(request, 'Mark deleted', mailmessage)

    return redirect('/admins/marks/')


def search(request):
    if request.user.is_authenticated == False:
        return redirect('/admins/login')

    data = Mark.objects.filter(
        Q(name__contains=request.GET['searchtext']) | Q(desctiption__contains=request.GET['searchtext']))
    return render(request, 'mark/index.html', {'data': data})


def addpoint(request, id):
    if request.user.is_authenticated == False:
        return redirect('/admins/login')

    if request.method == 'POST':
        # HttpResponse(request.POST['x'])
        point = Point(mark=Mark.objects.get(id=id), num=request.POST['count'], x=request.POST['x']
                      , y=request.POST['y'])
        point.save()
        return HttpResponse('good')
    else:
        return redirect('/admins/marks/')


def deletepoint(request, id):
    if request.user.is_authenticated == False:
        return redirect('/admins/login')

    if request.method == 'POST':
        # HttpResponse(request.POST['x'])
        Point.objects.filter(mark=id).delete()
        mailmessage = request.user.username + " deleted points of the mark thats have the id " + str(id)

        mail(request, 'Points deleted', mailmessage)
        return redirect('/admins/marks/edit/' + str(id))


def mail(request, subject, message):
    send_mail(
        subject,
        message,
        'info@aimark.com',
        ['del.souhaib@gmail.com', request.user.email],
    )
