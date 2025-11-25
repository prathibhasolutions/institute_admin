
from django.contrib import admin

from .models import Course, Student, Transaction


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ("id", "name")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "mobile_no", "guardian_name", "guardian_mobile_no", "course", "joining_date", "course_completion_date", "fees", "student_photo")



# Transaction admin registration

from django.db.models import Sum

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ("id", "date", "transaction_type", "amount", "description")
	list_filter = ("transaction_type", "date")
	search_fields = ("description",)
	date_hierarchy = "date"
	ordering = ("-date",)

	def changelist_view(self, request, extra_context=None):
		from django.utils.timezone import now
		today = now()
		month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		credits = Transaction.objects.filter(transaction_type="CREDIT").aggregate(total=Sum("amount"))['total'] or 0
		debits = Transaction.objects.filter(transaction_type="DEBIT").aggregate(total=Sum("amount"))['total'] or 0
		current_balance = credits - debits

		month_credits = Transaction.objects.filter(
			transaction_type="CREDIT",
			date__gte=month_start,
			date__lte=today
		).aggregate(total=Sum("amount"))['total'] or 0
		month_debits = Transaction.objects.filter(
			transaction_type="DEBIT",
			date__gte=month_start,
			date__lte=today
		).aggregate(total=Sum("amount"))['total'] or 0

		if extra_context is None:
			extra_context = {}
		extra_context['current_balance'] = current_balance
		extra_context['month_credits'] = month_credits
		extra_context['month_debits'] = month_debits
		return super().changelist_view(request, extra_context=extra_context)



