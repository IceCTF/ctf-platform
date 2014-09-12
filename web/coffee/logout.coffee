window.logout = ->
  apiCall "GET", "/api/user/logout"
  .done (data) ->
    switch data['status'] 
      when 1
        ga('send', 'event', 'Authentication', 'LogOut', 'Success')
        document.location.href = "/"
      when 0
        ga('send', 'event', 'Authentication', 'LogOut', 'Failure::'+data.message)
        document.location.href = "/login"
