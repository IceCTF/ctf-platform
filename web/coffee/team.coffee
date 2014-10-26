renderTeamInformation = _.template($("#team-info-template").remove().text())
renderGroupInformation = _.template($("#group-info-template").remove().text())
renderAchievementInformation = _.template($("#achievement-info-template").remove().text())

load_team_info = ->
  apiCall "GET", "/api/team"
  .done (data) ->
    switch data["status"]
      when 0
        apiNotify(data)
        ga('send', 'event', 'Team', 'LoadFailure', data.message)
      when 1
        $("#team-info").html renderTeamInformation({data: data.data})
        x = "<ul>" + ("<li>" + _.escape(j) + "</li>" for j in data.data.justification).join("") + "</ul>"
        $('#eligibility-exp').data "content", x

load_group_info = ->
  apiCall "GET", "/api/group/list"
  .done (data) ->
    switch data["status"]
      when 0
        apiNotify(data)
        ga('send', 'event', 'Team', 'GroupLoadFailure', data.message)
      when 1
        $("#group-info").html renderGroupInformation({data: data.data})

        $("#join-group").on "click", group_request
        $("#group-request-form").on "submit", join_group_request
        $(".leave-group-span").on "click", (e) ->
          leave_group $(e.target).data("group-name"), $(e.target).data("group-owner")
            
load_achievement_info = ->
    apiCall "GET", "/api/achievements"
    .done (data) ->
      switch data['status']
        when 0
            apiNotify(data)
            ga('send', 'event', 'Achievements', 'LoadFailure', data.message);
        when 1
            console.log(data.data)
            $("#achievement-info").html renderAchievementInformation({data: data.data})

join_group = (group_name, group_owner) ->
  apiCall "POST", "/api/group/join", {"group-name": group_name, "group-owner": group_owner}
  .done (data) ->
    apiNotify(data)
    if data["status"] is 1
      ga('send', 'event', 'Team', 'JoinGroup', 'Success')
      load_group_info()        
    else
      ga('send', 'event', 'Team', 'JoinGroup', 'Failure::' + data.message)

leave_group = (group_name, group_owner) ->
  apiCall "POST", "/api/group/leave", {"group-name": group_name, "group-owner": group_owner}
  .done (data) ->
    apiNotify(data)
    if data["status"] is 1
      ga('send', 'event', 'Team', 'LeaveGroup', 'Success')
      load_group_info()
    else
      ga('send', 'event', 'Team', 'LeaveGroup', 'Failure::' + data.message)

group_request = (e) ->
  e.preventDefault()
  form = $(this).closest "form"
  confirmDialog("By joining a class you are allowing the instructor to see individual statistics concerning your team's performance. Are you sure you want to join this class?", 
                "Class Confirmation", "Join", "Cancel", 
        (e) ->
            form.trigger "submit"
       ,(e) -> 
            ga('send', 'event', 'Team', 'JoinGroup', 'RejectPrompt'))

join_group_request = (e) ->
  e.preventDefault()

  group_name = $("#group-name-input").val()
  group_owner = $("#group-owner-input").val()
  join_group group_name, group_owner

$ ->
  load_team_info()
  load_group_info()
  load_achievement_info()
  window.drawTeamProgressionGraph("#team-progression-graph", "#team-progression-graph-container")
  return
