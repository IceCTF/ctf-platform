renderScoreboardTeamScore = _.template($("#scoreboard-teamscore-template").remove().text())
renderScoreboardTabs = _.template($("#scoreboard-tabs-template").remove().text())
renderScoreboard = _.template($("#scoreboard-template").remove().text())

load_teamscore = ->
  apiCall "GET", "/api/team", {}
  .done (resp) ->
    switch resp["status"]
      when 1
        $("#scoreboard-teamscore").html renderScoreboardTeamScore({
          teamscore: resp.data.score
        })
      when 0
        apiNotify(data)

load_scoreboard = ->
  apiCall "GET", "/api/stats/scoreboard", {}
  .done (data) ->
    switch data["status"]
      when 1
        $("#scoreboard-tabs").html renderScoreboardTabs({
          data: data.data
          renderScoreboard: renderScoreboard
        })

        window.drawTopTeamsProgressionGraph "#top-team-score-progression-graph"
      when 0
        apiNotify(data)

$ ->
  load_scoreboard()
  load_teamscore()
