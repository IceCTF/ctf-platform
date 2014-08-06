updatePassword = (e) ->
  e.preventDefault()
  apiCall "POST", "/api/user/update_password", $("#password-update-form").serializeObject()
  .done (data) ->
    apiNotify data
    

$ ->
  $("#password-update-form").on "submit", updatePassword
