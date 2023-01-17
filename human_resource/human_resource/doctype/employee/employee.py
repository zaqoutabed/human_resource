# Copyright (c) 2023, zaqfas and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from dateutil.relativedelta import relativedelta
from frappe.utils import getdate, add_days, date_diff

class Employee(Document):
	def validate(self):
		self.set_full_name()
		self.set_age()
		self.validate_mobile()
		self.validate_education()
	
	def set_full_name(self):
		full_name = [
			self.first_name,
			self.middle_name,
			self.last_name
		]
		full_name = " ".join(list(filter(lambda x: isinstance(x, str) and len(x) > 0, full_name)))
		self.full_name = full_name or ''

	def set_age(self):
		age_str = ""
		if self.date_of_birth:
			born = getdate(add_days(self.date_of_birth, -1))
			now_date = getdate()
			if date_diff(now_date, getdate(self.date_of_birth)) < 0:
				frappe.throw("Birth date cannot be in the future.")

			age = relativedelta(getdate(), born)
			self.validate_age(age)
			age_str = f"{str(age.years)} Year(s), {str(age.months)} Month(s), {str(age.days)} Day(s)"
		self.employee_age = age_str
	
	def validate_age(self, age):
		if age.years > 60 and self.status == "Active":
			frappe.throw("Active Employee age cannot be more than 60 years")
	
	def validate_mobile(self):
		is_valid = False
		if self.mobile:
			if isinstance(self.mobile, str) and len(self.mobile) == 10 and self.mobile.isnumeric() and self.mobile.startswith('059'):
				is_valid = True
		if not is_valid:
			frappe.throw("Invalid Mobile Number")
	
	def validate_education(self):
		if len(self.employee_education) < 2:
			frappe.throw("Atleast 2 education levels are required")