import os
from itertools import chain
from os import walk

from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from accounts.forms import MyUserCreate, StudentEditForm, TeacherEditForm
from accounts.models import LearnCategory, Syllabus, PriceRange, Student, Teacher, City


def base_view(request):
    return render(request, 'accounts/_base.html', {})


def index_accounts(request):
    return render(request, 'accounts/index.html', {})


def user_create(request):
    if request.method == 'POST':
        logout(request)
        user_create_form = MyUserCreate(request.POST)
        if user_create_form.is_valid:
            try:
                user = user_create_form.save(commit=False)
                # user.is_active = False

                user_saved = user
                user.save()
                login(request, user)
            except:
                user_saved = None
        else:
            user_saved = None
    else:
        user_create_form = MyUserCreate()
        user_saved = None
    context = {
        'user_create_form': user_create_form,
        'user_saved': user_saved,

    }
    return render(request, 'accounts/user_create.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.GET.get('next'):
                return HttpResponseRedirect(request.GET.get('next'))
            if hasattr(user, 'teacher'):
                return HttpResponseRedirect(reverse('accounts:teacher_edit'))
            elif hasattr(user, 'student'):
                return HttpResponseRedirect(reverse('accounts:student_edit'))
            else:
                return HttpResponse("logined but you are not saaved as a student or a teacher"
                                    "please signup with a different username!!!")

        else:
            context = {
                'username': username,
                'error': "user not found",
            }
            return render(request, 'accounts/login.html', context)
    else:
        context = {}
        return render(request, 'accounts/login.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('accounts:index_accounts'))

@login_required
def profile_edit(request):
    if hasattr(request.user, 'teacher'):
        return HttpResponseRedirect(reverse('accounts:teacher_edit'))
    if hasattr(request.user, 'student'):
        return HttpResponseRedirect(reverse('accounts:student_edit'))
    else:
        return HttpResponse("لطفا دوباره بصورت معلم یا دانش آموز ثبت نام کنید")


@login_required
@csrf_exempt
def student_edit(request):
    if request.is_ajax():
        category = request.GET.get('category',None)
        category_list = request.GET.get('category_list', None)
        if category_list:
            category_list = list(LearnCategory.objects.all().values())
            return JsonResponse(category_list, safe=False)
        syll = list(Syllabus.objects.filter(learn_category=category).values())
        return JsonResponse(syll, safe=False)

    else:

        student_edit_form = StudentEditForm()
        cities = list(City.objects.all().values())
        price_ranges = list(PriceRange.objects.all().values())
        # languages = list(Language.objects.all().values())
        categories = list(LearnCategory.objects.all().values())
        syllabuses = None
        student_profile = None
        error = None
        if hasattr(request.user, 'student'):
            student_profile = Student.objects.get(user_id=request.user.id)
            student_edit_form = StudentEditForm(instance=student_profile)
            error = str(request.user)+" "+'خوش آمدید'
            if request.method == 'POST':
                try:
                    student_edited = StudentEditForm(request.POST)
                    student_edited = student_edited.save(commit=False)
                    student_edited.user = request.user
                    student_edited.pk = student_profile.id
                    student_edited.save()
                    student_profile = request.user.student
                    error = "نمایه شما با موفقیت تغییر یافت "
                except :

                    error = 'ورودی های خود را کنترل کنید'
                    raise ValidationError( 'ورودی های خود را کنترل کنید')
            if hasattr(request.user, 'teacher'):
                return HttpResponse("شما به عنوان معلم ثبت نام کرده اید نه دانش آموز ")

        if request.method == 'POST' and hasattr(request.user, 'student') is False:
            try:
                student_edit_form = StudentEditForm(request.POST)

                if student_edit_form.is_valid():

                    student = student_edit_form.save(commit=False)
                    student.user = request.user
                    student.save()
                    error = "به عنوان دانش آموز در سیستم ثبت شدید"
                    student_profile = request.user.student
            except:
                student_profile = request.POST
                error = "لطفا ورودی های هود را کنترل کنید"


        context = {
            'student_profile' : student_profile,
            'student_edit_form': student_edit_form,
            'error': error,
            'cities': cities,
            'price_ranges' : price_ranges,
            # 'learn_types' : learn_types,
            'categories' : categories,
            'syllabuses' : syllabuses,
            # 'first_name' : first_name,
            # 'last_name' : last_name,
            }


        return render(request, 'accounts/student_edit.html', context)





@login_required
@csrf_exempt
# def teacher_edit(request):
#     if request.is_ajax():
#         category = request.GET.get('category', None)
#         category_list = request.GET.get('category_list', None)
#         if category_list:
#             category_list = list(LearnCategory.objects.all().values())
#             return JsonResponse(category_list, safe=False)
#         syll = list(Syllabus.objects.filter(learn_category=category).values())
#         return JsonResponse(syll, safe=False)
#
#     else:
#
#         teacher_edit_form = TeacherEditForm()
#         cities = list(City.objects.all().values())
#         price_ranges = list(PriceRange.objects.all().values())
#         # languages = list(Language.objects.all().values())
#         categories = list(LearnCategory.objects.all().values())
#         syllabuses = None
#         first_name = None
#         last_name = None
#         teacher_profile = None
#         error = ''
#         if hasattr(request.user, 'teacher'):
#             teacher_profile = Teacher.objects.get(user_id=request.user.id)
#             teacher_edit_form = TeacherEditForm(instance=teacher_profile)
#             error = 'welcome' + "  " + str(request.user)
#
#             if request.method == 'POST':
#                 try:
#                     teacher_edited = TeacherEditForm(request.POST, request.FILES)
#                     teacher_edited = teacher_edited.save(commit=False)
#                     teacher_edited.user = request.user
#                     teacher_edited.pk = teacher_profile.id
#                     if teacher_edited.image == "":
#                         teacher_edited.image = teacher_profile.image
#                     if teacher_edited.degree_image == "":
#                         teacher_edited.degree_image = teacher_profile.degree_image
#                     if teacher_edited.national_card_image == "":
#                         teacher_edited.national_card_image = teacher_profile.national_card_image
#                     teacher_edited.save()
#                     teacher_profile = request.user.teacher
#                     error = "profile edited successfully"
#                 except:
#                     error = 'your inputs not valid'
#         elif hasattr(request.user, 'student'):
#             return HttpResponse("You are a student please sign up with a different username as a teacher ")
#         if request.method == 'POST' and hasattr(request.user, 'teacher') is False:
#             try:
#                 teacher_edit_form = TeacherEditForm(request.POST, request.FILES)
#                 if teacher_edit_form.is_valid():
#                     teacher = teacher_edit_form.save(commit=False)
#                     teacher.user = request.user
#                     teacher.save()
#                     error = "profile saved as  a teacher successfully"
#                     teacher_profile = request.user.teacher
#             except:
#                 teacher_profile = request.POST
#                 error = "please complete inputs carefully"
#         context = {
#             'teacher_profile': teacher_profile,
#             'teacher_edit_form': teacher_edit_form,
#             'error': error,
#             'cities': cities,
#             'price_ranges': price_ranges,
#             # 'languages': languages,
#             'categories': categories,
#             'syllabuses': syllabuses,
#             'first_name': first_name,
#             'last_name': last_name,
#         }
#
#         return render(request, 'accounts/teacher_edit.html', context)
#

def teacher_edit(request):
        if request.is_ajax():
            category = request.GET.get('category',None)
            category_list = request.GET.get('category_list', None)
            if category_list:
                category_list = list(LearnCategory.objects.all().values())
                return JsonResponse(category_list, safe=False)
            syll = list(Syllabus.objects.filter(learn_category=category).values())
            return JsonResponse(syll,safe=False)

        else:

            teacher_edit_form = TeacherEditForm()
            cities = list(City.objects.all().values())
            price_ranges=list(PriceRange.objects.all().values())
            # languages=list(Language.objects.all().values())
            categories=list(LearnCategory.objects.all().values())
            syllabuses = None
            first_name = None
            last_name = None
            teacher_profile= None
            error = ''
            if hasattr(request.user, 'teacher'):
                teacher_profile = Teacher.objects.get(user_id=request.user.id)
                teacher_edit_form = TeacherEditForm(instance=teacher_profile)
                error = str(request.user)+" "+'خوش آمدید'

                if request.method == 'POST':
                    try:
                        teacher_edited = TeacherEditForm(request.POST, request.FILES)
                        teacher_edited = teacher_edited.save(commit=False)
                        teacher_edited.user = request.user
                        teacher_edited.pk = teacher_profile.id
                        if teacher_edited.sample_video == "":
                            teacher_edited.sample_video = teacher_profile.sample_video

                        if teacher_edited.image == "":
                            teacher_edited.image = teacher_profile.image
                        if teacher_edited.degree_image == "":
                            teacher_edited.degree_image = teacher_profile.degree_image
                        if teacher_edited.national_card_image == "":
                            teacher_edited.national_card_image = teacher_profile.national_card_image
                        teacher_edited.save()
                        # file_usage_check = list(list(Teacher.objects.all().values()))
                        # video_filenames = next(walk('/videos'))
                        # for i in range(0,len(video_filenames)):
                        #     if video_filenames[i] not in file_usage_check:
                        #         os.remove('media/videos/Django-Web-Development_7_1.mp4')





                        teacher_profile = request.user.teacher
                        error = "نمایه شما با موفقیت تغییر کرد. نتیجه بررسی از طریق پیامک به اطلاع شما خواهد رسید"
                    except :
                         raise ValidationError("ورودی ها دقیق نیست")
            elif hasattr(request.user, 'student'):
                return HttpResponse("مشخصات شما به عنوان دانش آموز ثبت شده لطفا با نام کاربری دیگری به عنوان معلم ثبت نام کنید ")
            if request.method == 'POST' and hasattr(request.user, 'teacher') == False:
                try:
                    teacher_edit_form = TeacherEditForm(request.POST, request.FILES)
                    if teacher_edit_form.is_valid():
                        teacher = teacher_edit_form.save(commit=False)
                        teacher.user = request.user
                        teacher.save()
                        error = "مشخصات شما ثبت شد. نتیجه بررسی از طریق پیامک به اطلاع شما خواهد رسید"
                        teacher_profile = request.user.teacher
                except:
                    teacher_profile = request.POST
                    error = "لطفا اطلاعات وارد شده را بررسی کنید"
            context = {
                'teacher_profile' : teacher_profile,
                'teacher_edit_form': teacher_edit_form,
                'error': error,
                'cities': cities,
                'price_ranges' : price_ranges,
                # 'languages' : languages,
                'categories' : categories,
                'syllabuses' : syllabuses,
                'first_name' : first_name,
                'last_name' : last_name,
                }


            return render(request, 'accounts/teacher_edit.html', context)

def search_view(request):
    results = []
    results_teachers =[]
    search_message = None
    if request.method == "GET":
        search_query = request.GET.get('search_text',None)

        if search_query:

            result1 = Syllabus.objects.filter(syllabus__icontains= search_query)
            result1_teachers = Teacher.objects.filter(syllabus__syllabus_name__contains=search_query)
            result2 = LearnCategory.objects.filter(category_name__icontains=search_query)
            result2_teachers = Teacher.objects.filter(category__category__contains=search_query)

            result3_teachers = Teacher.objects.filter(Q(last_name__icontains=search_query)|Q(first_name__icontains=search_query))
            results = list(chain(result1, result2, ))
            results_teachers = list(chain(result1_teachers,result2_teachers,result3_teachers ))

            if  results_teachers :
                search_message = str(len(results_teachers)) + "معلم پیدا شد"

            else:
                search_message = "موردی یافت نشد"

        return render(request, 'accounts/index.html', {'results': results, 'search_message': search_message,'results_teachers': results_teachers})




