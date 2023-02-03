# Copyright (c) 2023, zaqfas and contributors
# For license information, please see license.txt

from datetime import timedelta

import frappe

from frappe.model.document import Document
from frappe import _
from frappe.utils import (
    time_diff_in_seconds,
    time_diff_in_hours,
    cint,
    flt,
    get_time_str,
    to_timedelta,
)


class Attendance(Document):
    def validate(self):
        self.validate_check_time()
        self.vaildate_employee_attendance()
        self.calculate_attendance_hours(is_validate=True)

    def on_submit(self):
        self.validate_check_time()
        self.vaildate_employee_attendance()
        self.calculate_attendance_hours()

    def vaildate_employee_attendance(self):
        if (
            len(
                frappe.get_list(
                    "Attendance",
                    filters={
                        "employee": self.employee,
                        "attendance_date": self.attendance_date,
                        "docstatus": 1,
                        "name": ["!=", self.name],
                    },
                )
            )
            > 0
        ):
            frappe.throw(_("Employee is already attending this date"))

    def validate_check_time(self):
        # Validate Check In/Out Time
        if time_diff_in_seconds(self.check_out, self.check_in) < 0:
            frappe.throw(_("Check Out time must be greater than Check In time"))

    def calculate_attendance_hours(self, is_validate=False):
        status = "Present"
        req_hours = late_hours = 0
        settings = frappe.get_single("Attendance Settings")
        working_hours_threshold_for_absent = flt(
            settings.working_hours_threshold_for_absent
        )
        # Add Grace period
        check_in, check_out = self.check_in, self.check_out
        if (
            cint(settings.late_entry_grace_period) == 0
            and cint(settings.early_exit_grace_period) == 0
        ):
            check_in = self.check_in
            check_out = self.check_out
        elif (
            cint(settings.late_entry_grace_period) > 0
            and cint(settings.early_exit_grace_period) == 0
        ):
            check_in = get_time_str(
                to_timedelta(self.check_in)
                + timedelta(minutes=cint(settings.late_entry_grace_period))
            )
        elif (
            cint(settings.late_entry_grace_period) == 0
            and cint(settings.early_exit_grace_period) > 0
        ):
            check_in = get_time_str(
                to_timedelta(self.check_in)
                + timedelta(minutes=cint(settings.early_exit_grace_period))
            )
            check_out = get_time_str(
                to_timedelta(self.check_out)
                - timedelta(minutes=cint(settings.early_exit_grace_period))
            )
        else:
            check_in = get_time_str(
                to_timedelta(self.check_in)
                - timedelta(minutes=cint(settings.late_entry_grace_period))
            )
            check_out = get_time_str(
                to_timedelta(self.check_out)
                + timedelta(minutes=cint(settings.early_exit_grace_period))
            )

        working_hours = time_diff_in_hours(check_out, check_in)
        if settings.start_time and settings.end_time:
            req_hours = time_diff_in_hours(settings.end_time, settings.start_time)

        if req_hours > 0 and req_hours > working_hours:
            late_hours = req_hours - working_hours

        if working_hours < working_hours_threshold_for_absent:
            status = "Absent"
        if is_validate:
            self.work_hours, self.late_hours, self.status = (
                working_hours,
                late_hours,
                status,
            )
        else:
            self.db_set("work_hours", working_hours)
            self.db_set("late_hours", late_hours)
            self.db_set("status", status)
