# Copyright (c) 2023, zaqfas and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from frappe.utils import time_diff_in_seconds


class AttendanceSettings(Document):
    def validate(self):
        if time_diff_in_seconds(self.end_time, self.start_time) < 0:
            frappe.throw(_("End time must be greater than start time"))
