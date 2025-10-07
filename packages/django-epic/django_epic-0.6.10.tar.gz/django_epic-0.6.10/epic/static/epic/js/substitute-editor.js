// Hack alert: the default getValue() function in text_widget.js returns
// the auto-completion label rather than the value, which is just broken.
// Additionally, for the substitute widget we want to add the selected value
// to the substitute-list and then clear the input's value field again.
if ("yourlabs" in window) {
    yourlabs.TextWidget.prototype.getValue = function (choice) {
	var val = choice.attr ("data-value");
	if (this.input.attr ("class").match(/(^| )substitutewidget( |$)/)) {
	    substitute_add (this.input[0].obj, val);
	    return "";
	}
	return val;
    }
}

$(function () {
    function pad (integer, num_digits) {
	var result = integer + "";
	while (result.length < num_digits)
	    result = "00" + result;
	return result.substr (result.length - num_digits);
    }

    function format_part_number (part) {
	return "EP" + pad (part, 5);
    }

    function part_html_link (part) {
	return "<a href='/epic/part/" + part + "'>" +
	    format_part_number (part) + "</a>";
    }

    function substitute_add (obj, value_str) {
	part = parseInt (value_str);
	if (isNaN (part))
	    return false;
	if (part == obj.part) {
		alert ("Cannot add part to its own substitute-list.");
		return false;
	}
	for (var i in obj.data_list) {
	    if (part == obj.data_list[i]) {
		alert ("Part " + part + " is already listed as a substitute.");
		return false;
	    }
	}
	obj.data_list.push (part);
	substitute_render (obj);
	return false;
    }

    function substitute_add_event (event) {
	var obj = event.currentTarget.obj;
	var ret = substitute_add (obj, obj.input.value);
	obj.input.value = "";
	return ret;
    }

    function substitute_remove (event) {
	var obj = event.currentTarget.obj;
	var part = event.currentTarget.getAttribute ("part");
	for (var i in obj.data_list) {
	    if (obj.data_list[i] == part) {
		obj.data_list.splice (i, 1);
		substitute_render (obj);
		break;
	    }
	}
	return false;
    }

    function substitute_remove_html (part) {
	return "&nbsp;<a class='epic_substitute_remove' part='" + part + "'>" +
	    "<i class='glyphicon glyphicon-remove'></i></a>";
    }

    var btn_cls = "btn btn-default";

    function substitute_render (obj) {
	var html = "";
	var sep = "";
	if (obj.data_list.length > 0) {
	    for (var i in obj.data_list) {
		part = obj.data_list[i];
		html += sep
		    + "<span class='epic_substitute_element btn btn-default'>"
		    + part_html_link (part) + substitute_remove_html (part)
		    + "</span>";
		sep = " ";
	    }
	} else
	    html = '<em>&mdash; None &mdash;</em>'
	obj.html_list_el.innerHTML = html + "&nbsp;";
	$("a[class=epic_substitute_remove]").each (function () {
	    var el = $(this)[0];
	    el.obj = obj;
	    el.addEventListener ("click", substitute_remove);
	});
    }

    function prepare_for_submit (obj) {
	name = obj.input.getAttribute ("id").substr (3);
	$("input[name=" + name + "]").val (obj.data_list.join (","));
    }

    function substitute_init (sel) {
	var obj = sel[0];
	obj.input = obj.firstElementChild;
	obj.input.obj = obj;

	sel.closest ("form").submit (
	    function (event) {
		prepare_for_submit (obj);
	    });

	var add_el = document.createElement ("a");
	add_el.addEventListener ("click", substitute_add_event);
	add_el.innerHTML = "<i class='glyphicon glyphicon-plus'></i>";
	add_el.obj = obj;
	obj.appendChild (add_el);

	obj.data_list_el = sel.parent ()
	    .find ("span[class='epic_substitute_list']")[0];
	obj.data_list = [];
	obj.part = obj.data_list_el.getAttribute ("part");

	obj.html_list_el = document.createElement ("span");
	obj.data_list_el.parentElement.insertBefore (obj.html_list_el,
						     obj.data_list_el);

	var dl = obj.data_list_el.innerText.trim ().split (",");
	for (var i in dl) {
	    if (dl[i].length == 0)
		continue;
	    obj.data_list.push (parseInt (dl[i]));
	}
	substitute_render (obj);
    }

    $(document).ready( function() {
	$("span[class^=epic_substitute_add]").each (
	    function () { substitute_init ($(this)); });
    });

    window["substitute_add"] = substitute_add;
});
