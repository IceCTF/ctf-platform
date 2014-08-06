login = (e) ->
  e.preventDefault()
  apiCall "POST", "/api/user/login", $("#login-form").serializeObject()
  .done (data) ->
    switch data['status']
      when 0
        $("#login-button").apiNotify(data, {position: "right"})
      when 1
        document.location.href = "/"

resetPassword = (e) ->
  e.preventDefault()
  apiCall "GET", "/api/user/reset_password", $("#password-reset-form").serializeObject()
  .done (data) ->
    apiNotify(data)

$ ->
  $("#password-reset-form").toggle()

  $("#login-form").on "submit", login
  $("#password-reset-form").on "submit", resetPassword

  $(".toggle-login-ui").on "click", (e) ->
    e.preventDefault()

    $("#login-form").toggle()
    $("#password-reset-form").toggle()
