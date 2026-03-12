from auditlog.registry import auditlog
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from urllib.parse import quote

from .models import Course, Student, Transaction



@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ("id", "name")
auditlog.register(Course)



@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "course", "referee_name", "invoice_link", "referee_pdf_link")

	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			path(
				"<int:student_id>/invoice/",
				self.admin_site.admin_view(self.invoice_view),
				name="management_student_invoice",
			),
			path(
				"<int:student_id>/referee-commission-pdf/",
				self.admin_site.admin_view(self.referee_commission_pdf_view),
				name="management_student_referee_commission_pdf",
			),
		]
		return custom_urls + urls

	def invoice_link(self, obj):
		url = reverse("admin:management_student_invoice", args=[obj.pk])
		return format_html('<a class="button" href="{}" target="_blank">Invoice</a>', url)

	invoice_link.short_description = "Invoice"

	def referee_pdf_link(self, obj):
		url = reverse("admin:management_student_referee_commission_pdf", args=[obj.pk])
		return format_html('<a class="button" href="{}" target="_blank">Referee Print</a>', url)

	referee_pdf_link.short_description = "Referee Print"

	def invoice_view(self, request, student_id):
		student = self.get_object(request, student_id)
		if student is None:
			self.message_user(request, "Student not found.", level=messages.ERROR)
			return HttpResponseRedirect(reverse("admin:management_student_changelist"))

		invoice_date = timezone.localdate()
		balance_due = student.fees - student.paid_fees
		payable_amount = balance_due if balance_due > 0 else 0
		invoice_number = f"INV-{invoice_date.strftime('%Y%m%d')}-{student.id}"
		upi_id = "9542906390@ybl"
		upi_uri = (
			f"upi://pay?pa={upi_id}"
			f"&pn={quote('Prathibha Institute')}"
			f"&tn={quote(f'Fee Payment {invoice_number}')}"
		)
		if payable_amount > 0:
			upi_uri += f"&am={payable_amount:.2f}&cu=INR"
		upi_qr_url = (
			"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data="
			f"{quote(upi_uri, safe='')}"
		)
		context = {
			**self.admin_site.each_context(request),
			"title": f"Invoice - {student.name}",
			"student": student,
			"balance_due": balance_due,
			"payable_amount": payable_amount,
			"invoice_date": invoice_date,
			"invoice_number": invoice_number,
			"institute_name": "Prathibha Institute",
			"institute_mobile": "9030941099",
			"institute_address": "Beside Bank of Maharashtra, Namdevwada, Nizamabad, 503002",
			"upi_id": upi_id,
			"upi_qr_url": upi_qr_url,
		}
		return TemplateResponse(request, "admin/management/student/invoice.html", context)

	def referee_commission_pdf_view(self, request, student_id):
		student = self.get_object(request, student_id)
		if student is None:
			self.message_user(request, "Student not found.", level=messages.ERROR)
			return HttpResponseRedirect(reverse("admin:management_student_changelist"))

		doc_date = timezone.localdate()
		paid_fees = Decimal(student.paid_fees or 0)
		commission_amount = (paid_fees * Decimal("0.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
		context = {
			**self.admin_site.each_context(request),
			"title": f"Referee Commission - {student.name}",
			"student": student,
			"doc_date": doc_date,
			"doc_number": f"RC-{doc_date.strftime('%Y%m%d')}-{student.id}",
			"commission_rate": Decimal("10.00"),
			"commission_amount": commission_amount,
			"paid_fees": paid_fees,
			"institute_name": "Prathibha Institute",
			"institute_mobile": "9030941099",
			"institute_address": "Beside Bank of Maharashtra, Namdevwada, Nizamabad, 503002",
		}
		return TemplateResponse(request, "admin/management/student/referee_commission.html", context)
auditlog.register(Student)



# Transaction admin registration

from django.db.models import Sum


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ("id", "date", "transaction_type", "formatted_amount", "description")
	list_filter = ("transaction_type", "date")
	search_fields = ("description",)
	date_hierarchy = "date"
	ordering = ("-date",)
	
	def formatted_amount(self, obj):
		return f"{obj.amount:.0f}"
	formatted_amount.short_description = "Amount"

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
auditlog.register(Transaction)



