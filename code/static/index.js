$("form").submit(function(evt){
	evt.preventDefault();
	var formData = $('input[name="hotel_name"]').val();
	var action = document.activeElement.getAttribute('value');
	if (action === null) {
		action = 'Overview'; 
	}
	$('#result_body').html("Loading ...");
	$.ajax({
		url: `/${action}/`,
		type: 'POST',
		data: formData,
		async: false,
		cache: false,
		contentType: false,
		enctype: 'multipart/form-data',
		processData: false,
		success: function (response) {
			$('#result_body').html(response);
		}
	});
	return false;
});