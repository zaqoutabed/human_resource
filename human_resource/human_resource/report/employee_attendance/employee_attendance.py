# Copyright (c) 2023, zaqfas and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    # if not filters.get("att_date"):
    # 	frappe.msgprint(_("Please select attendance date"))
    # 	data = []
    return columns, data


def get_data(filters=None):
    conds = [" at.docstatus=1 "]
    if filters.get("att_date"):
        conds.append(" at.attendance_date= '{}' ".format(filters.get("att_date")))
    if filters.get("employee"):
        conds.append(" at.employee='{0}' ".format(filters.get("employee")))
    conds = "WHERE {}".format(" AND ".join(conds))

    att_data = frappe.db.sql(
        """
		SELECT at.employee as employee, emp.full_name as employee_name, emp.department as department,
		       at.attendance_date as attendance_date, at.check_in as check_in, at.check_out as check_out,
			   at.work_hours as work_hours, at.late_hours as late_hours, at.status as status
		FROM `tabEmployee` emp
		LEFT JOIN `tabAttendance` at ON emp.name = at.employee
		{}
	""".format(
            conds
        ),
        as_dict=1,
    )

    att_employees = [f" '{d.employee}' " for d in att_data]
    if len(att_employees) == 0:
        att_employees_as_list = "''"
    else:
        att_employees_as_list = ", ".join(att_employees)

    non_att_employees = frappe.db.sql(
        """
		SELECT name as employee, full_name as employee_name, department,
		       '-' as attendance_date, '-' as check_in, '-' as check_out,
			   '-' as work_hours, '-' as late_hours, 'Not Attend' as status
		FROM `tabEmployee`
		WHERE name NOT IN ({})
	""".format(
            att_employees_as_list
        ),
        as_dict=1,
    )
    return att_data + non_att_employees


def get_columns():
    return [
        {
            "fieldname": "employee",
            "fieldtype": "Link",
            "label": _("Employee"),
            "options": "Employee",
        },
        {
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "label": _("Employee Name"),
            "width": 250,
        },
        {
            "fieldname": "department",
            "fieldtype": "Link",
            "label": _("Department"),
            "options": "Department",
        },
        {
            "fieldname": "attendance_date",
            "fieldtype": "Data",
            "label": _("Attendance Date"),
        },
        {"fieldname": "check_in", "fieldtype": "Data", "label": _("Check In")},
        {"fieldname": "check_out", "fieldtype": "Data", "label": _("Check Out")},
        {
            "fieldname": "work_hours",
            "fieldtype": "Data",
            "label": _("Work Hours"),
        },
        {
            "fieldname": "late_hours",
            "fieldtype": "Data",
            "label": _("Late Hours"),
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 150,
        },
    ]
