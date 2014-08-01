submit_registration = (e) ->
  e.preventDefault()
  
  registrationData = $("#user-registration-form").serializeObject()
  registrationData["create-new-team"] = $("#new-team").hasClass("active")
  registrationData["create-new-teacher"] = $("new-teacher").hasClass("active")

  $.post "/api/user/create", registrationData
  .done (data) ->
    switch data['status']
      when 0
        $("#register-button").apiNotify(data, {position: "right"})
      when 1
        document.location.href = "/login"

$ ->
  $("#user-registration-form").on "submit", submit_registration
