google.load 'visualization', '1.0', {'packages':['corechart']}

divFromSelector = (selector) ->
  _.first($(selector))

teamGraphOptions = {
  title: "Team Score Progression",
  legend: {
    position: "none"
  },
  pointSize: 3
}

timestampsToBuckets = (samples, key, seconds) ->
  min = _.first(samples)[key]
  buckets = _.groupBy samples, (sample) ->
    (sample[key] - min) / seconds

@drawTeamProgressionGraph = (selector) ->
  div = divFromSelector selector
  apiCall "GET", "/api/stats/team/score_progression", {}
  .done (data) ->
    graphData = [["Time", "Score"]]
    
    lastSubmission = null
    _.each data.data, (submission) ->
      if lastSubmission
        graphData.push [submission.time - 1, lastSubmission.score]
      graphData.push [submission.time, submission.score]
      lastSubmission = submission
      
    console.log(timestampsToBuckets data.data, "time", 600)
    packagedData = google.visualization.arrayToDataTable graphData

    chart = new google.visualization.LineChart(div)
    chart.draw(packagedData, teamGraphOptions)

