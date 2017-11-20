# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from models import NFCUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


from models import NFCUser, LectureSlot, Course

# Create your views here.
def new(request):
    return render(request, 'app/createdUser.html')

@csrf_exempt
def homepage(request):
    """
    Display the dashboard if user is logged in,
    or the login page is displayed.
    """
    if request.user.is_authenticated:
        return redirect('/dashboard')
    elif request.GET.get('next', None) is not None:
        return render(request, 'app/login.html', {'msg': 'You need to login to see your attendance!'})
    else:
        return render(request, 'app/login.html')

@csrf_exempt
def loginUser(request):
    """
    Login the user if the credentials are correct.
    """
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/dashboard')
        
        else:
            return render(request, 'app/login.html')
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    print user
    if user is not None:
        login(request, user)
        return redirect('/dashboard')
    else:
        return render(request, 'app/login.html',
                      {'email': username, 'password': password,
                       'msg': 'Invalid email or Password'})


@csrf_exempt
def createUser(request):
    # if request.user.type != "Admin":
    #     return HttpResponse("You need to be Admin to access this content")
    # else:
    if request.method == "GET":
        courses = Course.objects.all()
        return render(request, 'app/createUser.html', {'courses': courses})
    else:
        name = request.POST['name']
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        utype = request.POST['type']
        lastClass = {}
        if utype == 'Student':
            clist = {}
            for ccode in request.POST.getlist('ccode'):
                course = Course.objects.get(courseCode=ccode)
                course.studentList['studentList'].append(username)
                course.save()
                clist[ccode] = 0
                lastClass[ccode] = timezone.localtime(timezone.now())
        elif utype == 'Faculty':
            clist = {'clist': []}
            for ccode in request.POST.getlist('ccode'):
                clist['clist'].append(ccode)
        try:
            if utype == 'Admin':
                user = NFCUser.objects.create_user(
                    username=username, password=password,
                    email=email, type=utype, name=name)
                user.save()
            else:
                user = NFCUser.objects.create_user(
                    username=username, password=password,
                    email=email, type=utype, clist=clist,
                    lastClass=lastClass, name=name)
                user.save()
        except:
            return render(request, 'app/createUser.html', {'msg': 'Username already exists!'})

        return render(request, 'app/createdUser.html')

# @csrf_exempt
# def createUser(request):
#     if request.user.type != "Admin":
#         return HttpResponse("You need to be Admin to access this content")
#     else:
#         if request.method == "GET":
#             courses = Course.objects.all()
#             return render(request, 'app/createUser.html', {'courses': courses})
#         else:
#             name = request.POST['name']
#             username = request.POST['username']
#             password = request.POST['password']
#             email = request.POST['email']
#             utype = request.POST['type']
#             clist = {}
#             lastClass = {}
#             for ccode in request.POST.getlist('ccode'):
#                 clist[ccode] = 0
#                 lastClass[ccode] = timezone.localtime(timezone.now())
#             try:
#                 user = NFCUser.objects.create_user(
#                     username=username, password=password,
#                     email=email, type=utype, clist=clist,
#                     lastClass=lastClass, name=name)
#                 user.save()
#             except:
#                 return render(request, 'app/createUser.html', {'msg': 'Username already exists!'})
#             return HttpResponse("User Created!")

@csrf_exempt
def addLecture(request):
    if request.user.type != "Faculty":
        return HttpResponse("You need to be Faculty to access this content")
    else:
        if request.method == "GET":
            courses = Course.objects.all()
            return render(request, 'app/addClass.html', {'courses': courses})
        else:
            date = request.POST['date']
            time = request.POST['time']
            lt = request.POST['lt']
            courseCode = request.POST['ccode']
            course = Course.objects.get(courseCode=courseCode)
            course.numClasses += 1
            course.save()
            slot = LectureSlot(date=date, time=time, lt=lt, courseCode=courseCode)
            slot.save()
            return HttpResponse("Slot Saved")

def roundTime(time):
    hr = time.hour
    minute = time.minute
    if minute >= 45:
        time = datetime.time(hour=time.hour + 1, minute=0)
    elif minute <= 10:
        time = datetime.time(hour=time.hour, minute=0)
    else:
        time = datetime.time(hour=23, minute=0)
    return time

@csrf_exempt
def markAttendance(request):
    if request.method == "GET":
        return render(request, 'app/markattendance.html')
    else:
        lt = request.POST['lt']
        username = request.POST['username']
        uid = request.POST['uid']
        user = NFCUser.objects.get(username=username)
        clist = user.clist
        lastClass = user.lastClass
        date = timezone.localtime(timezone.now()).date()
        time = timezone.localtime(timezone.now()).time()
        time = roundTime(time)
        dt = datetime.datetime.combine(date, time)
        if time.hour == 23:
            return HttpResponse("Late")
        if len(LectureSlot.objects.filter(lt=lt, date=date, time=time)) == 0:
            return HttpResponse("No class")
        ccode = LectureSlot.objects.filter(lt=lt, date=date, time=time)[0].courseCode
        if ccode in clist:
            lc = lastClass[ccode].replace('T', ' ')
            print lc, dt
            if lc != str(dt):
                clist[ccode] += 1
                lastClass[ccode] = dt
                user.clist = clist
                user.lastClass = lastClass
                user.save()
                return HttpResponse("attendance Marked")
            else:
                return HttpResponse("Already Marked")
        else:
            return HttpResponse("No class")

@csrf_exempt
def addCourse(request):
    # if request.user.type != "Admin":
    #     return HttpResponse("You need to be Admin to access this content")
    # else:
    if request.method == "GET":
        return render(request, 'app/addCourse.html')
    else:
        courseCode = request.POST['ccode']
        course = Course(courseCode=courseCode, studentList={'studentList': []})
        course.save()
        return HttpResponse("Course Added")

@csrf_exempt
@login_required(login_url='/')
def dashboard(request):
    """
    Display the dashboard if user is logged in,
    or the login page is displayed.
    """
    user = NFCUser.objects.get(username=request.user.username)
    if user.type == 'Faculty':
        clist = user.clist
        if 'ccode' in request.GET:
            ccode = request.GET['ccode']
            attendance = {'attendance': {}}
            course = Course.objects.get(courseCode=ccode)
            studentList = course.studentList['studentList']
            attendance['attendance'] = []
            for s in studentList:
                student = NFCUser.objects.get(username=s)
                absent = course.numClasses-student.clist[ccode]
                if course.numClasses == 0:
                    percent = 0
                else:
                    percent = (float(student.clist[ccode])/float(course.numClasses))*100
                attendance['attendance'].append([student.name, [student.clist[ccode], course.numClasses, absent, percent]])
                print attendance['attendance']
            return render(request, 'app/dashboardFaculty.html', {'name': user.name, 'selcourse': ccode, 'clist': clist, 'attendance': attendance})
        else:
            return render(request, 'app/dashboardFaculty.html', {'name': user.name, 'clist': clist})
    elif user.type == 'Student':
        clist = user.clist
        attendance = []
        for ccode in clist:
            course = Course.objects.get(courseCode=ccode)
            absent = course.numClasses-clist[ccode]
            if course.numClasses == 0:
                percent = 0
            else:
                percent = (float(clist[ccode])/float(course.numClasses))*100
            attendance.append({
                'ccode': ccode,
                'present': clist[ccode],
                'total': course.numClasses, 
                'absent': absent,
                'percent': int(percent)
            })
        return render(request, 'app/dashboardStudent.html', {'name': user.name, 'attendance': attendance})
    else:
        totalStudents = len(NFCUser.objects.filter(type="Student")[:])
        totalFaculty = len(NFCUser.objects.filter(type="Faculty")[:])
        return render(request, 'app/dashboardAdmin.html', {'name': user.name, 'totalFaculty': totalFaculty, 'totalStudents': totalStudents})

@csrf_exempt
def logoutUser(request):
    logout(request)
    return redirect('/')

def resetdb(request):
    users = NFCUser.objects.all()
    for u in users:
        u.delete()
    lectures = LectureSlot.objects.all()
    for l in lectures:
        l.delete()
    courses = Course.objects.all()
    for c in courses:
        c.delete()
    courses = ['M1', 'PHY1', 'AUTOSAR', 'MLR']
    for c in courses:
        course = Course(courseCode=c)
        course.save()
    users = [{'name': 'user1', 'username': 'user1', 'type': 'Student', 'year': '1', 'branch': 'CCE', 'clist':"{'M1': 0, 'PHY1': 0}", 'lastClass': "{'M1': '0000', 'PHY1': '00000'}", 'password': 'saurav'},
             {'name': 'user2', 'username': 'user2', 'type': 'Student', 'year': '1', 'branch': 'CCE', 'clist':"{'M1': 0, 'PHY1': 0}", 'lastClass': "{'M1': '0000', 'PHY1': '00000'}", 'password': 'saurav'},
             {'name': 'user3', 'username': 'user3', 'type': 'Student', 'year': '1', 'branch': 'CCE', 'clist':"{'M1': 0, 'PHY1': 0}", 'lastClass': "{'M1': '0000', 'PHY1': '00000'}", 'password': 'saurav'},
             {'name': 'user4', 'username': 'user4', 'type': 'Student', 'year': '1', 'branch': 'CCE', 'clist':"{'M1': 0, 'PHY1': 0}", 'lastClass': "{'M1': '0000', 'PHY1': '00000'}", 'password': 'saurav'},
             {'name': 'user5', 'username': 'user5', 'type': 'Faculty', 'year': '1', 'branch': 'CCE', 'clist':"{'clist': ['M1', 'PHY1']}", 'lastClass': "{'M1': '0000', 'PHY1': '00000'}", 'password': 'saurav'},
             {'name': 'user6', 'username': 'user6', 'type': 'Admin', 'year': '1', 'branch': 'CCE', 'clist':"{'M1': 0, 'PHY1': 0}", 'lastClass': "{'M1': '0000', 'PHY1': '00000'}", 'password': 'saurav'},
             {'name': 'user7', 'username': 'user7', 'type': 'Student', 'year': '1', 'branch': 'CCE', 'clist':"{'M1': 0, 'PHY1': 0}", 'lastClass': "{'M1': '0000', 'PHY1': '00000'}", 'password': 'saurav'},
             {'name': 'user8', 'username': 'user8', 'type': 'Student', 'year': '1', 'branch': 'CCE', 'clist':"{'M1': 0, 'PHY1': 0}", 'lastClass': "{'M1': '0000', 'PHY1': '00000'}", 'password': 'saurav'}]
    for u in users:
        user = NFCUser.objects.create_user(
                username=u['username'], password=u['password'],
                email=u['username'], type=u['type'], clist=u['clist'],
                lastClass=u['lastClass'], name=u['name'])
        user.save()
@csrf_exempt
def saveuid(request):
    print request.POST
    return HttpResponse("OK")