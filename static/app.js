function signInCallback(authResult) {
    if (authResult['code']) {
        /* Send the one-time-use code to the server, if the server responds,
        write a 'login successful' message to the web page and redirect
        back to the main restaurants page */
        $.ajax({
            type: 'POST',
            url: '/gconnect?state={{STATE}}',
            processData: false,
            contentType: 'application/octet-stream; charset=utf-8',
            data: authResult['code'],
            success: function(result) {
                if (result) {
                    setTimeout(function() {
                        window.location.href = "{{ NEXT }}";
                    }, 2000);
                } else if (authResult['error']) {
                    console.log('There was an error: ' + authResult['error']);
                } else {
                    $('#result').html('Failed to make a server-side call. Check your configuration and console.');
                }
            }
        });
    }
}

/*
 *  Facebook login code
 */

window.fbAsyncInit = function() {
    FB.init({
        appId      : '1291799177618510',
        cookie     : true,
        xfbml      : true,
        version    : 'v2.12'
    });
};

// Load the SDK ansynchronously
(function(d, s, id){
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {return;}
    js = d.createElement(s);
    js.id = id;
    js.src = "https://connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

function checkLoginState() {
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
}

function statusChangeCallback(response) {
    if (response.status === 'connected') {
        sendTokenToServer(response.authResponse)
    }
}

function sendTokenToServer(response) {
    var flaskData = $('#js-data').data();
    var accessToken = response['accessToken'];
    $.ajax({
        type: 'POST',
        url: '/fbconnect?state=' + flaskData.state,
        data: accessToken,
        contentType: 'application/octet-stream; charset=UTF-8'
    }).done(function(result) {
        console.log('login succeeded')
        setTimeout(function() {
            window.location.href = flaskData.next;
        }, 1000);
        $('#feedback').text('Facebook login success! Redirecting...')
    }).fail(function() {
        console.log('login failed');
        setTimeout(function() {
            window.location.href = flaskData.home;
        }, 1000);
        $('#feedback').text('Server-side call failed. Redirecting to home page...');
    });
}
