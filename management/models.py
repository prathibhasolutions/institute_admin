from django.db import models


class Course(models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)

	def __str__(self):
		return self.name or "(No Name)"



class Student(models.Model):
	name = models.CharField(max_length=255)
	mobile_no = models.CharField(max_length=20)
	guardian_name = models.CharField(max_length=255, null=True, blank=True)
	guardian_mobile_no = models.CharField(max_length=20, null=True, blank=True)
	course = models.ForeignKey(Course, on_delete=models.PROTECT)
	joining_date = models.DateField(null=True, blank=True)
	course_completion_date = models.DateField(null=True, blank=True)
	fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	paid_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # New field, cannot be null
	student_photo = models.FileField(upload_to='student_photos/', null=True, blank=True)
	address = models.TextField(null=True, blank=True)
	admission_form = models.FileField(upload_to='admission_forms/', null=True, blank=True)
	note = models.TextField(null=True, blank=True)  # New field, can be null

	def __str__(self):
		return self.name

class Transaction(models.Model):
	TRANSACTION_TYPES = [
		("CREDIT", "Credit"),
		("DEBIT", "Debit"),
	]
	date = models.DateTimeField(null=True, blank=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
	description = models.CharField(max_length=255, null=True, blank=True)

	def __str__(self):
		return f"{self.date.date()} {self.transaction_type} {self.amount}"
