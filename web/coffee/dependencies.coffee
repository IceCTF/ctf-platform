@apiCall = (type, url, data) ->
  if type == "POST"
    data.token = $.cookie("token")

  $.ajax {url: url, type: type, data: data, cache: false}
  .fail (jqXHR, text) ->
    ga('send', 'event', 'Error', 'APIOffline', url)
    $.notify "The picoCTF server is currently down. We will work to fix this error right away.", "error"

@redirectIfNotLoggedIn = ->
  apiCall "GET", "/api/user/status", {}
  .done (data) ->
    switch data["status"]
      when 1
        if not data.data["logged_in"]
          ga('send', 'event', 'Redirect', 'NotLoggedIn')
          window.location.href = "/login"

@redirectIfLoggedIn = ->
  apiCall "GET", "/api/user/status", {}
  .done (data) ->
    switch data["status"]
      when 1
        if data.data["logged_in"]
          ga('send', 'event', 'Redirect', 'LoggedIn')
          window.location.href = "/"

@redirectIfTeacher = ->
  apiCall "GET", "/api/user/status", {}
  .done (data) ->
    switch data["status"]
      when 1
        if data.data["teacher"]
          ga('send', 'event', 'Redirect', 'Teacher')
          window.location.href = "/classroom"

getStyle = (data) ->
  style = "info"
  switch data.status
    when 0
      style = "error"
    when 1
      style = "success"
  return style

@apiNotify = (data, redirect) ->
  style = getStyle data
  $.notify data.message, style

  if redirect and data.status is 1
    setTimeout (->
        window.location = redirect
      ), 1000

@apiNotifyElement = (elt, data, redirect) ->
  style = getStyle data
  elt.notify data.message, style
  if redirect and data.status is 1
    setTimeout (->
        window.location = redirect
      ), 1000
    
@numericalSort = (data) ->
  data.sort (a, b) ->
    return (b - a)

@confirmDialog = (message, title, yesButton, noButton, yesEvent, noEvent) ->    
    renderDialogModal = _.template($("#modal-template").html())
    dialog_content = renderDialogModal({message: message, title: title, yesButton: yesButton, noButton: noButton, submitButton: ""})
    $("#modal-holder").html dialog_content    
    $("#confirm-modal").modal {backdrop: "static", keyboard: false} 
    .one "click", "#modal-yes-button", yesEvent
    .one "click", "#modal-no-button", noEvent

@messageDialog = (message, title, button, event) ->    
    renderDialogModal = _.template($("#modal-template").html())
    dialog_content = renderDialogModal({message: message, title: title, yesButton: button, noButton: "", submitButton: ""})
    $("#modal-holder").html dialog_content
    $("#confirm-modal").modal {backdrop: "static", keyboard: false} 
    .one "click", "#modal-yes-button", event
    
@formDialog = (message, title, button, defaultFocus, event) ->    
    renderDialogModal = _.template($("#modal-template").html())
    dialog_content = renderDialogModal({message: message, title: title, yesButton: "", noButton: "", submitButton: button})
    $("#modal-holder").html dialog_content    
    $("#confirm-modal").modal {backdrop: "static", keyboard: false} 
    .on 'shown.bs.modal', () -> $("#" + defaultFocus).focus()
    .on "click", "#modal-submit-button", event

@closeDialog = () ->
    $('#confirm-modal').modal('hide')

@logout = ->
  apiCall "GET", "/api/user/logout"
  .done (data) ->
    switch data['status'] 
      when 1
        ga('send', 'event', 'Authentication', 'LogOut', 'Success')
        document.location.href = "/"
      when 0
        ga('send', 'event', 'Authentication', 'LogOut', 'Failure::'+data.message)
        document.location.href = "/login"

$.fn.apiNotify = (data, configuration) ->
  configuration["className"] = getStyle data
  return $(this).notify(data.message, configuration)

# Source: http://stackoverflow.com/a/17488875
$.fn.serializeObject = ->
   o = {}
   a = this.serializeArray()
   $.each(a, ->
       if o[this.name]
           if !o[this.name].push
               o[this.name] = [o[this.name]]
           o[this.name].push(this.value || '')
       else
           o[this.name] = this.value || ''
   )
   return o
