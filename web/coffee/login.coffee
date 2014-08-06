login = (e) ->
  e.preventDefault()
  apiCall "POST", "/api/user/login", $("#login-form").serialize()
  .done (data) ->
    switch data['status']
      when 0
        $("#login-button").apiNotify(data, {position: "right"})
      when 1
        document.location.href = "/"

$ ->
  $("#password-reset-form").toggle()

  $("#login-form").on "submit", login

  $(".toggle-login-ui").on "click", (e) ->
    e.preventDefault()

    $("#login-form").toggle()
    $("#password-reset-form").toggle()
