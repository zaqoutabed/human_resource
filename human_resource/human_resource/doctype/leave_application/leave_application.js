// Copyright (c) 2023, zaqfas and contributors
// For license information, please see license.txt

frappe.ui.form.on('Leave Application', {
	from_date: function(frm) { frm.trigger("calculate_leave_amount"); },
	to_date: function(frm) {frm.trigger("calculate_leave_amount");},
	calculate_leave_amount: function(frm) {
		if (frm.doc.from_date && frm.doc.to_date){
			const d1 = new Date(cur_frm.doc.to_date);
			const d2 = new Date(cur_frm.doc.from_date);
			const total_leave_days = frappe.datetime.get_day_diff(d1, d2);
			if(total_leave_days <= 0){
				frm.set_value("total_leave_days", 0);
				frappe.throw("From Date should be less than To Date");
			}else{
				frm.set_value("total_leave_days",total_leave_days);
				frm.trigger("get_allocated_leaves");
			}
			frm.refresh_field("total_leave_days");
		}
	},
	leave_type: function(frm) { frm.trigger("get_allocated_leaves"); },
	employee: function(frm) { frm.trigger("get_allocated_leaves");  },
	get_allocated_leaves: function(frm) {
		if(frm.doc.employee && frm.doc.leave_type && frm.doc.from_date && frm.doc.to_date){
			frappe.call({
				method: "get_allocation",
                doc: frm.doc,
				callback: function(r) {
					if(r.message){
						frm.set_value("leave_balance_before_application", r.message);
						frm.refresh_field("leave_balance_before_application");		
					}
				},
				freeze: true,
				freeze_message: __("Please wait...")
			})
		}
	}
});
