// Copyright (c) 2023, zaqfas and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee', {
	first_name: function (frm) { frm.trigger("set_full_name"); },
	middle_name: function (frm) { frm.trigger("set_full_name"); },
	last_name: function (frm) { frm.trigger("set_full_name"); },
	set_full_name: function (frm) {
		const full_name = [
			frm.doc.first_name,
			frm.doc.middle_name,
			frm.doc.last_name
		].filter((val) => val && val).join(' ');
		frm.set_value('full_name', full_name||'');
	},
	date_of_birth: function (frm) {
		if (frm.doc.date_of_birth) {
			var ageMS = Date.parse(Date()) - Date.parse(frm.doc.date_of_birth || Date());
			var age = new Date();
			age.setTime(ageMS);
			var years = age.getFullYear() - 1970;
			frm.set_value('employee_age', `${years} Year(s), ${age.getMonth()} Month(s), ${age.getDate()} Day(s)`||'');
		}
	}
});
