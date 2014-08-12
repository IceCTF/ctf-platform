recaptchaPublicKey = ""

reloadCaptcha = ->
  # possibly disable this
  if true
    Recaptcha.reload()

submitRegistration = (e) ->
  e.preventDefault()

  registrationData = $("#user-registration-form").serializeObject()
  registrationData["create-new-team"] = $("#new-team").hasClass("active")
  registrationData["create-new-teacher"] = $("#new-teacher").hasClass("active")

  apiCall "POST", "/api/user/create", registrationData
  .done (data) ->
    switch data['status']
      when 0
        $("#register-button").apiNotify(data, {position: "right"})
        reloadCaptcha()
      when 1
        document.location.href = "/login"

$ ->
  # possibly disable this
  if true
    Recaptcha.create(recaptchaPublicKey, "captcha", { theme: "red" })
  $("#user-registration-form").on "submit", submitRegistration
