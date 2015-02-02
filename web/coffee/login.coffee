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
        if (data.data['teacher'])
                document.location.href = "/classroom"                
            else
                document.location.href = "/team"

resetPassword = (e) ->
  $("#reset-password-button").html("Please Wait...")
  $("#reset-password-button").attr('disabled',true)
  e.preventDefault()
  apiCall "GET", "/api/user/reset_password", $("#password-reset-form").serializeObject()
  .done (data) ->
    apiNotify(data)
    switch data['status']
        when 0
            ga('send', 'event', 'Authentication', 'PasswordReset', 'Failure::' + data.message)
        when 1
            ga('send', 'event', 'Authentication', 'PasswordReset', 'Success')
    $("#reset-password-button").html("Reset Password")
    $("#reset-password-button").attr('disabled',false)
            
$ ->
  $("#password-reset-form").toggle()

  $("#login-form").on "submit", login
  $("#password-reset-form").on "submit", resetPassword

  $(".toggle-login-ui").on "click", (e) ->
    e.preventDefault()

    $("#login-form").toggle()
    $("#password-reset-form").toggle()
