# --- IMPORTS
# -------------------------------------------------------------------------

# --- basic
from django.shortcuts import render, redirect, get_object_or_404

# --- authentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages

# --- forms and models
from .forms import *
from .models import *
from django.forms import inlineformset_factory

# --- dates
from datetime import datetime

# --- queries
from django.db.models import Q
import operator
from functools import reduce

# extra info
now = datetime.now()
today = now.strftime("%Y-%m-%d")


# --- AUTHENTICATION
# ----------------------------------------------------------------------------------------------------------------------

def login_page(request):

    # handle login attempt
    if request.method == 'POST' and 'log-user' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            redirect_url = request.GET.get('next', 'dashboard')  # next URL or default to 'uploads'
            return redirect(redirect_url)
        else:
            messages.info(request, 'Usuario o Contraseña Incorrectos')

    # return to login page by default
    context = {}
    return render(request, 'app_trucks/login.html', context)


def logout_page(request):
    logout(request)
    return redirect('login')


# --- DASHBOARD
# ----------------------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def dashboard(request):
    user = request.user

    context = {

    }

    return render(request, 'app_trucks/dashboard.html', context)


# --- WORKDAYS
# ----------------------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def workdays(request):

    # constants
    total_records = 100

    # get workday records
    w = WorkDay.objects.filter(user=request.user).order_by('-date')[:total_records]

    # return template with data
    context = {
        'w': w,
    }

    return render(request, 'app_trucks/workdays.html', context)


@login_required(login_url='login')
def workday_today(request):

    # check if workday already exists for today and current user
    workday = WorkDay.objects.workday_exists(_user=request.user, _date=today)

    # workday already exists -> edit workday
    if workday:

        return redirect('workday_edit', workday_id=workday.id)

    # workday doesn't exist -> create workday
    else:
        return redirect('workday_create', _date=today)


@login_required(login_url='login')
def workday_add_new(request):

    # handle select date
    if request.method == 'POST' and 'select-date' in request.POST:

        # load data and validate
        f = DateForm(request.POST)
        if f.is_valid():

            # check if workday already exists for _date and current user
            workday = WorkDay.objects.workday_exists(_user=request.user, _date=f.cleaned_data['date'])

            # workday doesn't exist -> create workday
            if not workday:
                return redirect('workday_create', _date=str(f.cleaned_data['date']))

            # workday exists -> duplicated error
            else:
                messages.success(request, 'form-duplicated')

        # invalid data -> form error
        else:
            messages.success(request, 'form-errors')

    # handle empty form request
    else:
        f = DateForm()

    context = {
        'f': f,
    }

    return render(request, 'app_trucks/select_date.html', context)


@login_required(login_url='login')
def workday_create(request, _date=today):

    # get company data for deliveries forms
    # (deliveries are presented as formset in workday form)
    companies = Company.objects.all()
    total = companies.count()

    # HANDLE CREATE-WORKDAY
    if request.method == 'POST' and 'create-workday' in request.POST:

        # load data from WorkdayFrom
        f = WorkDayForm(request.POST)
        new_workday = f.instance
        new_workday.user = request.user

        # load data from DeliveryFormSet
        fs = inlineformset_factory(WorkDay, Delivery, form=DeliveryForm, extra=total)
        fs = fs(request.POST, instance=new_workday)

        # validate WorkDayForm and DeliveryFormSet
        if f.is_valid() and fs.is_valid():

            # there is already a workday for this user and date -> error message
            a = WorkDay.objects.workday_exists(_user=request.user, _date=new_workday.date)
            if a:
                messages.success(request, 'form-duplicated')

            # no workday duplication -> create new workday with its deliveries
            else:

                # update income using list of deliveries
                new_workday = f.save(commit=False)
                new_deliveries = fs.save(commit=False)
                new_workday.update_income(deliveries=new_deliveries)

                # save
                new_workday = f.save()
                for new_delivery in new_deliveries:
                    new_delivery.save()

                # go to edit_workday with success message
                messages.success(request, 'form-saved')
                return redirect('workday_edit', workday_id=new_workday.id)

        # errors in DeliveryForm -> return error message
        else:
            messages.success(request, 'form-errors')

    # HANDLE EMPTY FORM REQUEST
    else:

        # get initial_data for deliveries (details for every available company)
        deliveries_ini = []
        for company in companies:
            pay_rate = Company.objects.select_pay_rate(company_id=company.id, _date=_date)
            company_ini = {
                'company': company.id,
                'pay_rate': pay_rate,
            }
            deliveries_ini.append(company_ini)

        f = WorkDayForm(initial={'date': _date})
        fs = inlineformset_factory(WorkDay, Delivery, form=DeliveryForm, extra=total)
        fs = fs(initial=deliveries_ini)

    # COMMON FINAL STEPS

    # return template with data
    context = {
        'f': f,
        'fs': fs,
        'date': _date,
        'task': 'create_workday',  # the templates changes its content according to the task
    }

    return render(request, 'app_trucks/workday.html', context)


@login_required(login_url='login')
def workday_edit(request, workday_id):
    w = WorkDay.objects.get(pk=workday_id)

    # restrict user access to his own records only
    if w.user != request.user:
        messages.success(request, 'edit-forbidden')
        return redirect('dashboard')

    # handle modify-workday
    if request.method == 'POST' and 'edit-workday' in request.POST:

        # load data
        f = WorkDayForm(request.POST, instance=w)
        fs = inlineformset_factory(WorkDay, Delivery, form=DeliveryForm, extra=0)
        fs = fs(request.POST, instance=w)

        if f.is_valid() and fs.is_valid():

            # save
            new_workday = f.save(commit=False)
            fs.save()
            income = new_workday.update_income(deliveries=new_workday.deliveries.all())
            f.save()

            # success message
            messages.success(request, 'form-saved')

        # errors in DeliveryForm -> return error message
        else:
            messages.success(request, 'form-errors')
            income = f.instance.income

    # handle view-workday
    else:
        f = WorkDayForm(instance=w)

        fs = inlineformset_factory(WorkDay, Delivery, form=DeliveryForm, extra=0)
        fs = fs(instance=w)

        for form in fs:
            data = form.instance
            a = 1

        income = f.instance.income

    # return template with data
    context = {
        'f': f,
        'fs': fs,
        'date': str(f.instance.date),
        'task': 'edit_workday',  # the templates changes its content according to the task
        'income': income,
    }

    return render(request, 'app_trucks/workday.html', context)


@login_required(login_url='login')
def workday_delete(request, workday_id):
    workday_to_delete = get_object_or_404(WorkDay, id=workday_id)

    if request.method == 'POST' and 'delete-workday' in request.POST:
        workday_to_delete.delete()
        messages.success(request, 'workday-deleted')

    return redirect('workdays')


# --- REPORTS
# ----------------------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def reports(request):

    # constants
    total_records = 300

    # handle report-list
    if request.method == 'POST' and 'make_report' in request.POST:

        f = ReportForm(request.POST)
        if f.is_valid():

            query_list = []

            # filter desired trucks
            truck_id = f.cleaned_data['truck']
            if truck_id:
                query_list.append(Q(truck_id__exact=truck_id))

            # filter desired users
            user_id = f.cleaned_data['user']
            if user_id:
                query_list.append(Q(user_id__exact=user_id))

            # filter desired ini date
            date_from = f.cleaned_data['date_ini']
            if date_from:
                query_list.append(Q(date__gte=date_from))  # greater to equal

            # filter desired end date
            date_to = f.cleaned_data['date_end']
            if date_to:
                query_list.append(Q(date__lte=date_to))  # lower to equal

            # at least one search field in report -> search
            if query_list:
                w = WorkDay.objects.filter(reduce(operator.and_, query_list))[:total_records]

            # no search field in report -> show all reports
            else:
                w = WorkDay.objects.all().order_by('-date')[:total_records]

            # return template with data
            context = {
                'w': w,
            }

            return render(request, 'app_trucks/reports.html', context)

    # handle show report-selection-fields
    else:
        f = ReportForm()

    # return template with data
    context = {
        'f': f,
    }

    return render(request, 'app_trucks/select_report.html', context)
