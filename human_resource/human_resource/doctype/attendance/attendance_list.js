frappe.listview_settings['Attendance'] = {
	add_fields: ["status", "name"],
	get_indicator: function (doc) {
		if (doc.status === "Present") {
			// Present
			return [__("Present"), "green", "status,=,Present"];
		} else if (doc.status === "Absent") {
			// Absent
			return [__("Absent"), "red", "status,=,Absent"];
		}
		return [__(doc.status), "orange", `status,=,${doc.status}`];
	},
	hide_name_column: true
};
