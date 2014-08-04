@apiCall = (type, url, data) ->
  $.ajax {url: url, type: type, data: data, cache: false}
  .fail (jqXHR, text) ->
    $.notify "API is offline. :(", "error"

@redirectIfNotLoggedIn = ->
  apiCall "GET", "/api/user/status", {}
  .done (data) ->
    switch data["status"]
      when 1
        if not data.data["logged_in"]
          window.location.href = "/login"

@redirectIfLoggedIn = ->
  apiCall "GET", "/api/user/status", {}
  .done (data) ->
    switch data["status"]
      when 1
        if data.data["logged_in"]
          window.location.href = "/"

getStyle = (data) ->
  style = "info"
  switch data.status
    when 0
      style = "error"
    when 1
      style = "success"
  return style

@apiNotify = (data) ->
  style = getStyle data
  $.notify data.message, style

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
