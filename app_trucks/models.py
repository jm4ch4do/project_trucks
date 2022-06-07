from django.db import models
from django.contrib.auth.models import User
import calendar
from datetime import datetime, date
from django.core.exceptions import ObjectDoesNotExist

now = datetime.now()
today = now.strftime("%Y-%m-%d")


class Worker(User):

    class Meta:
        proxy = True

    @staticmethod
    def get_workers_as_choices():
        workers = Worker.objects.all()

        # save users into a list with id and name (exclude superusers)
        worker_names = []
        for worker in workers:
            if not worker.is_superuser:
                user_data = (worker.id, worker.first_name + ' ' + worker.last_name)
                worker_names.append(user_data)

        # sort by name and insert 'todos' as first element
        worker_names.sort(key=lambda x: (x[1]))
        worker_names.insert(0, (0, 'todos'))

        return worker_names


class Truck(models.Model):

    #
    # -------------------- RELATIONSHIPS ------------------------------------------------------------
    # WorkDay(workdays): one truck has many workdays

    #
    # ----------------------- FIELDS ----------------------------------------------------------------

    # basic
    name = models.CharField(max_length=200)

    # truck details
    year = models.IntegerField(null=True)  # i believe it´s the year the truck was built
    mark = models.CharField(max_length=200, null=True)
    model = models.CharField(max_length=200, null=True)
    vin = models.CharField(max_length=200, null=True)
    license_plate = models.CharField(max_length=200, null=True)

    # others
    comment = models.TextField(blank=True)

    #
    # ---------------- PROPERTIES & FUNCTIONS --------------------------------------------------------
    @staticmethod
    def get_trucks_as_choices():
        trucks = Truck.objects.all()

        # save trucks into a list with id and name
        truck_names = []
        for truck in trucks:
            truck_data = (truck.id, truck.name)
            truck_names.append(truck_data)

        # sort by name and insert 'todos' as first element
        truck_names.sort(key=lambda x: (x[1]))
        truck_names.insert(0, (0, 'todos'))

        return truck_names

    #
    # ------------------------ META -----------------------------------------------------------------
    class Meta:
        ordering = ['-year']
        verbose_name = "Truck"
        verbose_name_plural = "Trucks"

    #
    # ---------------------- STRING NAME -------------------------------------------------------------
    # string name for the class
    def __str__(self):
        return self.name if self.name else 'no_name'


class WorkDayManager(models.Manager):

    def workday_exists(self, _user, _date=today):

        # import queryset (always goes at the start of any Manager function)
        queryset = self.get_queryset()

        # if _date provided as string -> force to date object
        if type(_date) is not date:
            _date = datetime.strptime(_date, "%Y-%m-%d").date()

        # find workday
        try:
            workday = queryset.get(user=_user, date=_date)

        # workday doesn't exist -> return None
        except ObjectDoesNotExist:
            return None  # workday doesn't exist

        # workday exist -> return workday
        return workday


class WorkDay(models.Model):
    #
    # -------------------- RELATIONSHIPS ------------------------------------------------------------
    # User: one user has many workdays
    user = models.ForeignKey(User, related_name='workdays', on_delete=models.CASCADE)

    # Truck: one truck has many workdays
    truck = models.ForeignKey(Truck, related_name='workdays', on_delete=models.CASCADE)

    #
    # ----------------------- FIELDS ----------------------------------------------------------------

    # date
    date_created = models.DateTimeField(auto_now_add=True)
    date = models.DateField(default=date.today, null=True, blank=True)

    # mileage
    ini_mileage = models.IntegerField(null=True)
    end_mileage = models.IntegerField(null=True, blank=True)

    # mileage
    income = models.FloatField(null=True, blank=True, default=0)  # is only updated using method update_income

    # others
    comment = models.TextField(null=True, blank=True)

    #
    # ---------------- PROPERTIES & FUNCTIONS --------------------------------------------------------
    @property
    def name(self):
        weekday = calendar.day_name[self.date_created.weekday()]
        date_as_string = str(self.date_created).partition(' ')[0]
        return str(self.user) + ' on ' + str(self.truck) + ' ' + weekday + ' ' + date_as_string

    @property
    def name_for_user(self):
        weekday = calendar.day_name[self.date_created.weekday()]
        date_as_string = str(self.date_created).partition(' ')[0]
        return str(self.truck) + ' ' + weekday + ' ' + date_as_string

    def update_income(self, deliveries):

        # summarize payment from every delivery
        self.income = 0
        for delivery in deliveries:
            self.income += delivery.pay
        return self.income

    objects = WorkDayManager()

    #
    # ------------------------- META -----------------------------------------------------------------
    class Meta:
        ordering = ['-date']
        verbose_name = "Workday"
        verbose_name_plural = "Workdays"

    #
    # ---------------------- STRING NAME -------------------------------------------------------------
    # string name for the class
    def __str__(self):
        return self.name if self.name else 'no_name'


class CompanyManager(models.Manager):

    def select_pay_rate(self, company_id, _date=today):

        # import queryset (always goes at the start of any Manager function)
        queryset = self.get_queryset()

        # if _date provided as string -> force to date object
        if type(_date) is not date:
            _date = datetime.strptime(_date, "%Y-%m-%d").date()

        # find company
        try:
            _company = queryset.get(pk=company_id)
        except ObjectDoesNotExist:
            return None  # company doesn't exist -> No pay_rate to select

        # find pay_rates for the company
        try:
            _pay_rates = _company.pay_rates.all()
        except ObjectDoesNotExist:
            return _company.default_pay_rate  # no pay_rates for the company -> use default

        # verify if any pay_rate has a date_interval including the current_date
        for _pay_rate in _pay_rates:

            # date_interval is good -> use this pay_rate
            if _pay_rate.ini_date <= _date <= _pay_rate.end_date:
                return _pay_rate.amount

        # no date_interval was good -> use default
        else:
            return _company.default_pay_rate


class Company(models.Model):

    #
    # -------------------- RELATIONSHIPS ------------------------------------------------------------
    # Delivery(deliveries): one company has many deliveries
    # PayRate(pay_rates)  : one company has many pay_rates

    #
    # ----------------------- FIELDS ----------------------------------------------------------------

    # basic
    name = models.CharField(max_length=200)
    default_pay_rate = models.FloatField()

    # others
    comment = models.TextField(blank=True)

    #
    # ---------------- PROPERTIES & FUNCTIONS --------------------------------------------------------
    objects = CompanyManager()

    #
    # ------------------------- META -----------------------------------------------------------------
    class Meta:
        ordering = ['name']
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    #
    # ---------------------- STRING NAME -------------------------------------------------------------
    # string name for the class
    def __str__(self):
        return self.name if self.name else 'no_name'


class Delivery(models.Model):
    #
    # -------------------- RELATIONSHIPS ------------------------------------------------------------
    # Company: one company has many deliveries
    company = models.ForeignKey(Company, related_name='deliveries', on_delete=models.CASCADE)

    # WorkDay: one workday has many deliveries
    workday = models.ForeignKey(WorkDay, related_name='deliveries', on_delete=models.CASCADE)

    #
    # ----------------------- FIELDS ----------------------------------------------------------------

    # basic
    pay_rate = models.IntegerField()  # copied from Company or PayRate on record creation
    amount = models.IntegerField(default=0)  # number of deliveries made

    #
    # ---------------- PROPERTIES & FUNCTIONS --------------------------------------------------------
    @property
    def name(self):
        d_id = str(self.id)
        company = str(self.company)
        user = str(self.workday.user)
        truck = str(self.workday.truck)
        d_date = str(self.workday.date_created).partition(' ')[0]
        return 'delivery id ' + d_id + ' for ' + company + ' by ' + user + ' using ' + truck + ' at ' + d_date

    @property
    def pay(self):
        return self.pay_rate * self.amount

    #
    # ------------------------- META -----------------------------------------------------------------
    class Meta:
        verbose_name = "Delivery"
        verbose_name_plural = "Deliveries"

    #
    # ---------------------- STRING NAME -------------------------------------------------------------
    # string name for the class
    def __str__(self):
        return self.name if self.name else 'no_name'


class PayRate(models.Model):

    #
    # -------------------- RELATIONSHIPS ------------------------------------------------------------
    # Company: one company has many PayRates
    company = models.ForeignKey(Company, related_name='pay_rates', on_delete=models.CASCADE)

    #
    # ----------------------- FIELDS ----------------------------------------------------------------

    # basic
    amount = models.FloatField()

    # dates
    ini_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    #
    # ---------------- PROPERTIES & FUNCTIONS --------------------------------------------------------
    @property
    def name(self):
        return 'pay rate id ' + str(self.id) + ' for ' + str(self.company)

    #
    # ------------------------- META -----------------------------------------------------------------
    class Meta:
        ordering = ['ini_date', 'id']
        verbose_name = "Payrate"
        verbose_name_plural = "Payrates"

    #
    # ---------------------- STRING NAME -------------------------------------------------------------
    # string name for the class
    def __str__(self):
        return self.name if self.name else 'no_name'
