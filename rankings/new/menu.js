$('.dropdown-el').click(function (e) {
	e.preventDefault();
	e.stopPropagation();
	$(this).toggleClass('expanded');
	$('#' + $(e.target).attr('for')).prop('checked', true);
	if (!$( this ).is(".expanded")){
		var variant = $("input[name='Variant']:checked").val();
		var event = $("input[name='Event']:checked").val();
		var page = $("input[name='Page']:checked").val();
		var type = $("input[name='Type']:checked").val();
		/*alert("Loading ".concat(variant, "/", event, "/", page, "_", type, ".html"));*/
		window.location.href = "../../".concat(variant, "/", event, "/", type, "_", page, ".html");
	}
});
$(document).click(function () {
	$('.dropdown-el').removeClass('expanded');
});