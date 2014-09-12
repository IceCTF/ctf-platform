login = (e) ->
  e.preventDefault()
  apiCall "POST", "/api/user/login", $("#login-form").serializeObject()
  .done (data) ->
    switch data['status']
      when 0
        $("#login-button").apiNotify(data, {position: "right"})
        ga('send', 'event', 'Authentication', 'LogIn', 'Failure::' + data.message)
      when 1
        ga('send', 'event', 'Authentication', 'LogIn', 'Success')
        document.location.href = "/"

resetPassword = (e) ->
  e.preventDefault()
  apiCall "GET", "/api/user/reset_password", $("#password-reset-form").serializeObject()
  .done (data) ->
    apiNotify(data)
    switch data['status']
        when 0
            ga('send', 'event', 'Authentication', 'PasswordReset', 'Failure::' + data.message)
        when 1
            ga('send', 'event', 'Authentication', 'PasswordReset', 'Success')
            
$ ->
  $("#password-reset-form").toggle()

  $("#login-form").on "submit", login
  $("#password-reset-form").on "submit", resetPassword

  $(".toggle-login-ui").on "click", (e) ->
    e.preventDefault()

    $("#login-form").toggle()
    $("#password-reset-form").toggle()
