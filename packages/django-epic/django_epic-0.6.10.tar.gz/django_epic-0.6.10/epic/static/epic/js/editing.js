$(function () {

    function is_empty (el) {
	if (el.length == 0)
	    return true;
	return el.val () == "";
    }

    function update_line_cost (prefix) {
	var qty = $("#" + prefix + "qty").val ();
       var part_cost = $("#" + prefix + "part_cost").val ();
       var line_cost = $("#" + prefix + "line_cost");
       if (!($.isNumeric (qty) && $.isNumeric (part_cost))) {
	   line_cost.val ("");
	   return;
       }
       line_cost.val ((qty * part_cost).toFixed (2));
    }

    function get_part_info (query, callback) {
	var url = "/epic/part/info?" + query;
	$.getJSON (url, "", function (obj) {
	    callback (obj);
	});
    }

    function set_vendor_pn (obj, val) {
	obj.val (val);
	obj.attr ("readonly", val != "");
    }

    function part_changed (obj) {
	var prefix = obj.attr("id").replace (/(part|comp)$/, "");
	var vendor_pn = $("#" + prefix + "vendor_pn");
	var part_cost = $("#" + prefix + "part_cost");

	var part_id = obj.val ();
	var vendor_id = $("#id_vendor").val ()
	if (!part_id)
	    return;
	var query = "pid=" + part_id;
	if (vendor_id)
	    query += "&vid=" + vendor_id;
	get_part_info (query,
		       function (part_info) {
			   if (!(part_id in part_info)) {
			       part_cost.val ("");
			       set_vendor_pn (vendor_pn, "");
			       update_line_cost (prefix);
			       return;
			   }
			   obj = part_info[part_id];
			   part_cost.val (obj["price"]);
			   update_line_cost (prefix);
			   if ("vendor_pn" in obj)
			       set_vendor_pn (vendor_pn, obj["vendor_pn"]);
			   else
			       set_vendor_pn (vendor_pn, "");
		       });
    }

    function update_vendor_pn (obj) {
	var new_vendor_id = obj.val ();

	/* get list of parts with non-empty part #s: */
	parts = $("select[name$=-part]").map(
	    function () {
		return is_empty ($(this)) ? null : $(this);
	    });
	if (parts.length <= 0)
	    return;

	var query = "vid=" + new_vendor_id + "&pid=";
	var part_numbers = parts.map (function () { return $(this).val (); });
	query += $.makeArray (part_numbers).join (",");

	/* clear all vendor part-numbers: */
	$("input[name$=-vendor_pn]").each (
	    function () { set_vendor_pn ($(this), ""); });

	get_part_info (query,
		       function (part_info) {
			   for (var i=0; i < parts.length; ++i) {
			       var p = parts[i]
			       var pn = p.val ();
			       if (pn in part_info &&
				   ("vendor_pn" in part_info[pn]))
			       {
				   var pfx = p.attr("id").replace (/part$/, "");
				   var vendor_pn = $("#" + pfx + "vendor_pn");
				   set_vendor_pn (vendor_pn,
						  part_info[pn]["vendor_pn"]);
			       }
			   }
		       });
    }

    var disabled_fields_for_inter_warehouse = [ "vendor_pn", "part_cost",
						"line_cost" ];

    function selector_for_disabled_fields (prefix, postfix) {
	var r = [];
	for (i in disabled_fields_for_inter_warehouse) {
	    el = disabled_fields_for_inter_warehouse[i];
	    r.push (prefix + el + postfix);
	}
	return r.join (",");
    }

    function set_price_and_amount_visible (is_visible) {
	sel = (selector_for_disabled_fields ("th[for$=", "]") + "," +
	       selector_for_disabled_fields ("th[id$=", "]"));
	if (is_visible)
	    $(sel).show ();
	else
	    $(sel).hide ();
    }

    function from_warehouse () {
	return $("select[name=from_warehouse]");
    }

    /* Update the "from_warehouse"/"order #" editability on the ship-form.  */
    function update_from_warehouse_and_order () {
	var order_num = $("input[name=ordr]");
	var from = from_warehouse ();

	order_num.attr ("disabled", false);
	from.attr ("disabled", false);

	set_price_and_amount_visible (is_empty (from));

	if (!is_empty (order_num)) {
	    from.attr ("disabled", true);
	    from.val (null);
	} else if (!is_empty (from)) {
	    order_num.attr ("disabled", true);
	    order_num.val (null);
	}
    }

    function prepare_for_submit (form) {
	var from = from_warehouse ();
	if (!is_empty (from)) {
	    /*
	     * Set dummy-values for disabled elements so they pass
	     * Django form-validation.  Their values aren't used.
	     */
	    sel = selector_for_disabled_fields ("input[name$=", "]");
	    $(sel).each (function () {
		var qty = $(this).closest ("tr").find ("input[name$=qty]");
		if (!is_empty (qty))
		    $(this).val ("0");
	    });
	}
    }

    function add_delete_all_toggle () {
	/* Add a checkbox to the "Delete" table-header such that this
	   checkbox sets the value of the delete checkboxes in all
	   rows.  */
	$("th[for$=-DELETE]").each (
	    function () {
		$(this).html ("<input type='checkbox'> Delete");
		$(this).on ("change",
			    function () {
				new_value = $(this).find ("input:checkbox")
				    .prop ("checked")
				$(this).closest ("table")
				    .find ("input[name$=-DELETE]")
				    .prop ("checked", new_value)
				    .trigger ('change')
			    });
	    });
    }


    $(document).ready(function() {
	add_delete_all_toggle ();

	/* On Part # change, update Vendor Part # and Part cost: */
	$("body").on ("change",
		      "select.modelselect2[name$=-part]",
		      function () { part_changed ($(this)) });
	/* In Assembly-Item editor, part is called "comp": */
	$("body").on ("change",
		      "select.modelselect2[name$=-comp]",
		      function () { part_changed ($(this)) });
	/* On qty change, update line_cost: */
	$("body").on ("change",
		      "input[name$=-qty]",
		      function () {
			  var prefix = $(this).attr ("id").replace (/qty$/, "");
			  update_line_cost (prefix);
		      });
	/* On part_cost change, update line_cost: */
	$("body").on ("change",
		      "input[name$=-part_cost]",
		      function () {
			  var prefix = $(this).attr ("id")
			      .replace (/part_cost$/, "");
			  update_line_cost (prefix);
		      });
	/* On line_cost change, update price: */
	$("body").on ("change",
		      "input[name$=-line_cost]",
		      function () {
			  var prefix = $(this).attr ("id")
			      .replace (/line_cost$/, "");
			  var qty = $("#" + prefix + "qty");
			  var part_cost = $("#" + prefix + "part_cost");
			  part_cost.val (($(this).val () / qty.val ())
					 .toFixed (6))
		      });
	/* On changing the DELETE checkbox, toggle the "epic_deleted" class.  */
	$("body").on ("change",
		      "input[name$=-DELETE]",
		      function () {
			  $(this).closest ("tr")
			      .toggleClass ("epic_deleted",
					    $(this).prop ("checked"));
		      })
	/* On vendor change, update vendor part #s: */
	$("#id_vendor").on ("change",
			    function () {
				update_vendor_pn ($(this));
			    });

	var from = from_warehouse ();
	$("input[name=ordr]")
	    .on ("input", update_from_warehouse_and_order);
	from.on ("input", update_from_warehouse_and_order);
	update_from_warehouse_and_order ();

	from.closest ("form").submit (
	    function (event) {
		prepare_for_submit ($(this));
	    })

	// to save space, we only display help-block when an input element
	// has is double-clicked
	$("p[class=help-block]").hide ()
	$("label").click (function () {
	    var id = $(this).attr ("for");
	    $("p[id=hint_" + id + "]").toggle ()
	});

	// last but not least: focus on first empty required input field:
	$("input,select").each (function () {
	    var id = $(this).attr ("id");
	    if (!id || !is_empty ($(this)) || $(this).attr ("readonly"))
		return true;
	    var m = id.match (/^id_(.+)_set-\d+-(.+)/);
	    if (m)
		label_name = "id_" + m[1] + "_set-0-" + m[2];
	    else
		label_name = id;
	    var label = $("[for=" + label_name + "]");
	    if (label.length == 1 && label.hasClass ("requiredField")) {
		$(this).focus ();
		$(this)[0].scrollIntoView ();
		return false;	// return false to stop iterating any further
	    }
	    return true;
	});
    })
});
