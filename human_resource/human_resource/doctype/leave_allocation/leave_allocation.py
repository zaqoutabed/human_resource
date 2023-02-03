# Copyright (c) 2023, zaqfas and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff
from frappe.model.document import Document

class LeaveAllocation(Document):
	def validate(self):
		if self.from_date > self.to_date:
			frappe.throw("From Date should be less than To Date")
		days = date_diff(self.to_date, self.from_date)
		if self.total_leaves_allocated > days:
			frappe.throw("Total Leaves Allocated {} should be less than Total Leave Days ({})".format(self.total_leaves_allocated, days))
		

