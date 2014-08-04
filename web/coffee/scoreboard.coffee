renderScoreboardTabs = _.template($("#scoreboard-tabs-template").remove().text())
renderScoreboard = _.template($("#scoreboard-template").remove().text())

load_scoreboard = ->
  apiCall "GET", "/api/stats/scoreboard", {}
  .done (data) ->
    switch data["status"]
      when 1
        $("#scoreboard-tabs").html renderScoreboardTabs({
          data: data.data
          renderScoreboard: renderScoreboard
        })
      when 0
        apiNotify(data)

$ ->
  load_scoreboard()
