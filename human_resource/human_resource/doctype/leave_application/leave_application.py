# Copyright (c) 2023, zaqfas and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff
from frappe.model.document import Document

class LeaveApplication(Document):
	def validate(self):
		if self.from_date > self.to_date:
			frappe.throw("From Date should be less than To Date")
		days = date_diff(self.to_date, self.from_date)
		self.total_leave_days = days
	
		allocated_leaves = frappe.get_list("Leave Allocation", fields=["SUM(total_leaves_allocated) as total_leaves_allocated"], filters={
			"employee": self.employee,
			"leave_type": self.leave_type,
			"from_date": ["<=", self.from_date],
			"to_date": [">=", self.to_date]
		})
		if len(allocated_leaves) == 0 or allocated_leaves[0].total_leaves_allocated is None:
			frappe.throw("There is no leave allocation for this employee and leave type form data {} to Date {}".format(self.from_date, self.to_date))
		
		total_allocated = allocated_leaves[0].total_leaves_allocated
		self.leave_balance_before_application = total_allocated
		if self.total_leave_days > total_allocated:
			frappe.throw("Total Leave Days should be less than Total Allocated Leaves {}".format(total_allocated))
		
		# Get last leave application
		# all_applications = frappe.db.sql("""SELECT lap.to_date as to_date, lt.applicable_after
		#               FROM `tabLeave Application` lap
		# 			  Left Join `tabLeave Type` lt ON lap.leave_type = lt.name
		# 			  Order BY lap.to_date""", as_dict=1)
		# if len(all_applications) > 0:
		# 	last_application = all_applications[0]
		# 	days_from_last_application = date_diff(self.from_date, last_application)
		

	def on_submit(self):
		allocated_leaves = frappe.get_list("Leave Allocation", fields=["SUM(total_leaves_allocated) as total_leaves_allocated"], filters={
			"employee": self.employee,
			"leave_type": self.leave_type,
			"from_date": ["<=", self.from_date],
			"to_date": [">=", self.to_date],
			"docstatus": 1
		})
		if len(allocated_leaves) == 0 or allocated_leaves[0].total_leaves_allocated is None or allocated_leaves[0].total_leaves_allocated == 0:
			frappe.throw("There is no leave allocation for this employee and leave type form data {} to Date {}".format(self.from_date, self.to_date))
		total_allocated = allocated_leaves[0].total_leaves_allocated
		if self.total_leave_days > total_allocated:
			frappe.throw("Total Leave Days should be less than Total Allocated Leaves {}".format(total_allocated))
		allocated_leaves = frappe.get_list("Leave Allocation", filters={
			"employee": self.employee,
			"leave_type": self.leave_type,
			"from_date": ["<=", self.from_date],
			"to_date": [">=", self.to_date],
			"docstatus": 1
		})
		allocated_leaves = allocated_leaves[0]
		allocated_leaves = frappe.get_doc("Leave Allocation", allocated_leaves.name)
		allocated_leaves.db_set("total_leaves_allocated", total_allocated-self.total_leave_days)
	
	def on_cancel(self):
		allocated_leaves = frappe.get_list("Leave Allocation", fields=["SUM(total_leaves_allocated) as total_leaves_allocated"], filters={
			"employee": self.employee,
			"leave_type": self.leave_type,
			"from_date": ["<=", self.from_date],
			"to_date": [">=", self.to_date],
			"docstatus": 1
		})
		if len(allocated_leaves) == 0:
			frappe.throw("There is no leave allocation for this employee and leave type form data {} to Date {}".format(self.from_date, self.to_date))
		total_allocated = allocated_leaves[0].total_leaves_allocated
		allocated_leaves = frappe.get_list("Leave Allocation", filters={
			"employee": self.employee,
			"leave_type": self.leave_type,
			"from_date": ["<=", self.from_date],
			"to_date": [">=", self.to_date],
			"docstatus": 1
		})
		allocated_leaves = allocated_leaves[0]
		allocated_leaves = frappe.get_doc("Leave Allocation", allocated_leaves.name)
		allocated_leaves.db_set("total_leaves_allocated", total_allocated+self.total_leave_days)
	
	@frappe.whitelist()
	def get_allocation(self):
		allocated_leaves = frappe.get_list("Leave Allocation", fields=["SUM(total_leaves_allocated) as total_leaves_allocated"], filters={
			"employee": self.employee,
			"leave_type": self.leave_type,
			"from_date": ["<=", self.from_date],
			"to_date": [">=", self.to_date],
			"docstatus": 1
		})
		if len(allocated_leaves) == 0:
			frappe.throw("There is no leave allocation for this employee and leave type form data {} to Date {}".format(self.from_date, self.to_date))
		return allocated_leaves[0].total_leaves_allocated or 0


		