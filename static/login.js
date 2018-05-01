/*
 *  Google sign-in code
 */

// Sign-in button event listener
$('#g-signin2').click( function() {
    auth2.grantOfflineAccess().then(signInCallback)
});

// Sign-in callback
function signInCallback(authResult) {
    var flaskData = $('#js-data').data();
    if (authResult['code']) {
        // Send the one-time-use code to the server and redirect if successful
        $.ajax({
            type: 'POST',
            url: '/gconnect?state=' + flaskData.state,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            contentType: 'application/octet-stream; charset=utf-8',
            processData: false,
            data: authResult['code'],
            success: function(result) {
                if (result) {
                    setTimeout(function() {
                        window.location.href = flaskData.next;
                    }, 1500);
                    $('#feedback').text('Google login success!');
                    $('#feedback').css('visibility', 'visible');
                } else if (authResult['error']) {
                    setTimeout(function() {
                        window.location.href = flaskData.home;
                    }, 1500);
                    $('#feedback').text('Authentication error. Redirecting to home page...');
                    $('#feedback').css('visibility', 'visible');
                    console.log('There was an error: ' + authResult['error']);
                } else {
                    setTimeout(function() {
                        window.location.href = flaskData.home;
                    }, 1500);
                    $('#feedback').text('Server-side call failed. Redirecting to home page...');
                    $('#feedback').css('visibility', 'visible');
                }
            }
        });
    } else {
        setTimeout(function() {
            window.location.href = flaskData.home;
        }, 1500);
        $('#feedback').text('No response from Google. Redirecting to home page...');
        $('#feedback').css('visibility', 'visible');
    }
}


/*
 *  Facebook login code
 */

// Facebook init
window.fbAsyncInit = function() {
    FB.init({
        appId      : '1291799177618510',
        cookie     : true,
        xfbml      : true,
        version    : 'v2.12'
    });
};

// Load the SDK ansynchronously
(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {return;}
    js = d.createElement(s);
    js.id = id;
    js.src = "https://connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

// Called when Facebook login button is clicked
function checkLoginState() {
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
}

// Check if user is connected to Facebook
function statusChangeCallback(response) {
    if (response.status === 'connected') {
        sendTokenToServer(response.authResponse)
    }
}

// Send token to server and redirect if successful
function sendTokenToServer(response) {
    var flaskData = $('#js-data').data();
    var accessToken = response['accessToken'];
    $.ajax({
        type: 'POST',
        url: '/fbconnect?state=' + flaskData.state,
        data: accessToken,
        contentType: 'application/octet-stream; charset=UTF-8'
    }).done(function(result) {
        setTimeout(function() {
            window.location.href = flaskData.next;
        }, 1500);
        $('#feedback').text('Facebook login success!');
        $('#feedback').css('visibility', 'visible');
    }).fail(function() {
        setTimeout(function() {
            window.location.href = flaskData.home;
        }, 1500);
        $('#feedback').text('Server-side call failed. Redirecting to home page...');
        $('#feedback').css('visibility', 'visible');
    });
}
