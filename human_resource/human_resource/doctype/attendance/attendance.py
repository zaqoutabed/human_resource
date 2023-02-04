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
    add_days,
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
        if settings.start_time and settings.end_time:
            req_hours = time_diff_in_hours(settings.end_time, settings.start_time)

        working_hours_threshold_for_absent = flt(
            settings.working_hours_threshold_for_absent
        )
        # Add Grace period
        check_in, check_out = self.check_in, self.check_out
        if time_diff_in_seconds(check_out, settings.start_time) < 0 or time_diff_in_seconds(check_in, settings.end_time) > 0:
            working_hours = 0
            late_hours = req_hours
        else:
            # Check if check in is before start time
            if time_diff_in_seconds(check_in, settings.start_time) < 0:
                check_in = settings.start_time
            else:
                start_time_with_grace = get_time_str(
                    to_timedelta(settings.start_time)
                    + timedelta(minutes=cint(settings.late_entry_grace_period))
                )
                if time_diff_in_seconds(check_in, start_time_with_grace) < 0:
                    check_in = settings.start_time

            if time_diff_in_seconds(check_out, settings.end_time) > 0:
                check_out = settings.end_time
            else:
                end_time_with_grace = get_time_str(
                    to_timedelta(settings.end_time)
                    - timedelta(minutes=cint(settings.early_exit_grace_period))
                )
                if time_diff_in_seconds(check_out, end_time_with_grace) > 0:
                    check_out = settings.end_time
            working_hours = time_diff_in_hours(check_out, check_in)
            
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


@frappe.whitelist()
def create_attendance(attendance_date, check_in, check_out):
    from frappe.utils import get_user_date_format, get_user_time_format
    from dateutil import parser

    employee = frappe.db.exists("Employee", {"user": frappe.session.user})
    if not employee:
        prepare_response(404, "faild", "User not Linked to Employee")
        return
    try:
        attendance_date = parser.parse(attendance_date)
    except:
        prepare_response(
            400,
            "faild",
            "Check Attendance Date, Format Error User {} Format".format(
                get_user_date_format()
            ),
        )
        return
    try:
        time_diff_in_seconds(check_out, check_in) < 0
    except:
        prepare_response(
            400,
            "faild",
            "Check In/Out times, Format Error User {} Format".format(
                get_user_time_format()
            ),
        )
        return

    has_attendance = frappe.db.exists(
        "Attendance",
        {"attendance_date": attendance_date, "employee": employee, "docstatus": 1},
    )
    if has_attendance:
        prepare_response(409, "faild", "Employee is already attending this date")
        return

    if time_diff_in_seconds(check_out, check_in) < 0:
        prepare_response(
            409, "faild", "Check Out time must be greater than Check In time"
        )
        return

    att = frappe.new_doc("Attendance")
    att.attendance_date = attendance_date
    att.check_in = check_in
    att.check_out = check_out
    att.employee = employee
    att.save(ignore_permissions=True)
    att.reload()
    att.submit()
    data = {}
    for k, v in att.as_dict().items():
        if k in (
            "employee",
            "employee_name",
            "department",
            "attendance_date",
            "check_in",
            "check_out",
            "work_hours",
            "late_hours",
        ):
            data.update({k: v})
    prepare_response(200, "sccess", "Addendance Successfully added", data)


def prepare_response(status_code, _type, message, data={}):
    frappe.local.response["http_status_code"] = status_code
    frappe.local.response["api_status"] = {
        "type": _type,
        "message": message,
    }
    frappe.local.response["data"] = data
