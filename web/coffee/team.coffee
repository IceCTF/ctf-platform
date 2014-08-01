renderTeamInformation = _.template($("#team-info-template").remove().text())
renderGroupInformation = _.template($("#group-info-template").remove().text())

load_team_info = ->
  $.get "/api/team"
  .done (data) ->
    switch data["status"]
      when 0
        apiNotify(data)
      when 1
        $("#team-info").html renderTeamInformation({data: data.data})

load_group_info = ->
  $.get "/api/group"
  .done (data) ->
    switch data["status"]
      when 0
        apiNotify(data)
      when 1
        $("#group-info").html renderGroupInformation({data: data.data})

        $("#group-request-form").on "submit", group_request
        $(".leave-team-span").on "click", (e) ->
          leave_group $(e.target).data("group-name")

join_group = (group_name) ->
  $.post "/api/group/join", {"group-name": group_name}
  .done (data) ->
    apiNotify(data)
    if data['status'] is 1
      load_group_info()

leave_group = (group_name) ->
  $.post "/api/group/leave", {"group-name": group_name}
  .done (data) ->
    apiNotify(data)
    if data['status'] is 1
      load_group_info()

#Could be simplified without this function
group_request = (e) ->
  e.preventDefault()

  group_name = $("#group-name-input").val()
  join_group group_name

$ ->
  load_team_info()
  load_group_info()
  return
