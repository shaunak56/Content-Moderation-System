function getCsrfToken() {
    var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}

function showToast(message, duration=2000){
    M.toast({
        "html": message,
        "displayLength": duration,
    });
}