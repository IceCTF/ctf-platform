renderTeamShirtInformation = _.template($("#team-shirt-fields-template").remove().text())

loadTShirtInfo = ->
  apiCall "GET", "/api/tshirts/team"
  .done (data) ->
    switch data["status"]
      when 0
        apiNotify(data)
      when 1
        $("#member-fields").html renderTeamShirtInformation({data: data.data})
        for user in data.data['members']
          do (user) ->
            $("#size-" + user.uid).val(user.shirtsize)
            $("#gender-" + user.uid).val(user.shirttype)
        $("#address").val(data.data['address'])


submitTShirtInfo = (e) ->
  e.preventDefault()
  tshirtData = $("#tshirt-info-form").serializeObject()
  users = {}
  $(".tshirt-field").each (i,field) ->
    users[$(field).data "user"] = {}
  $(".tshirt-field").each (i,field) ->
    users[$(field).data "user"][$(field).data "field"] = $(field).val()
  tshirtData['users'] = JSON.stringify(users)
  apiCall "POST", "/api/tshirts/update", tshirtData
  .done (data) ->
    switch data['status']
      when 0
        $("#update-button").apiNotify(data, {position: "right"})
      when 1
        $("#update-button").apiNotify(data, {position: "right"})


$ ->
  loadTShirtInfo()
  $("#tshirt-info-form").on "submit", submitTShirtInfo
  return
