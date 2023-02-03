// Copyright (c) 2023, zaqfas and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Attendance"] = {
	"filters": [
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname":"att_date",
			"label": __("Attendance Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.now_date(),
			"reqd": 1
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
	    value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "status") {
			const color = data.status == __("Present") ? 'green': 'red';
			value = `<div style='color:${color}' ">${value.bold()}</span>`;
		}
		if(value == "-"){
			value = `<div style='text-align: center' ">${value}</div>`;
		}
		
		return value;
	},
};
