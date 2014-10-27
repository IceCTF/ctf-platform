google.load 'visualization', '1.0', {'packages':['corechart']}

divFromSelector = (selector) ->
  _.first($(selector))

topTeamsGraphOptions = {
  title: "Top Team Score Progression",
  legend: {
    position: "top"
  },
  vAxis: {
    title: "Score"
  },
  hAxis: {
    ticks: []
  },
  pointSize: 3,
  areaOpacity: 0.0,
  enableInteractivity: true
}

teamGraphOptions = {
  title: "Team Score Progression",
  legend: {
    position: "none"
  },
  vAxis: {
    title: "Score"
  },
  hAxis: {
    ticks: []
  },
  pointSize: 3
}

timestampsToBuckets = (samples, key, min, max, seconds) ->

  bucketNumber = (number) ->
    Math.floor((number - min) / seconds)

  continuousBucket = {}
  maxBuckets = bucketNumber max

  for i in [0..maxBuckets]
    continuousBucket[i] = []

  buckets = _.groupBy samples, (sample) ->
    bucketNumber sample[key]

  return _.extend continuousBucket, buckets

maxValuesFromBucketsExtended = (buckets, sampleKey) ->
  maxValues = []

  lastInsertedValue = 0

  _.each buckets, (samples) ->
    values = _.pluck(samples, sampleKey)

    if values.length > 0
      maxValue = _.max values
      maxValues.push maxValue
      lastInsertedValue = maxValue
    else
      maxValues.push lastInsertedValue

  return maxValues

progressionDataToPoints = (data, dataPoints, currentDate = 0) ->

  sortedData = _.sortBy _.flatten(data), (submission) ->
    return submission.time

  min = _.first(sortedData).time - 60*5
  lastTime = _.last(sortedData).time
  max = if currentDate is 0 then lastTime else Math.min(lastTime + 3600*24, currentDate)
  bucketWindow = Math.max(Math.floor((max - min) / dataPoints), 1)

  dataSets = []

  _.each data, (teamData) ->
    buckets = timestampsToBuckets teamData, "time", min, max, bucketWindow
    steps = maxValuesFromBucketsExtended buckets, "score"

    if steps.length > dataPoints
      steps = _.rest(steps, steps.length - dataPoints)

    dataSets.push steps

  #Avoid returning a two dimensional array with 1 element
  return if dataSets.length > 1 then dataSets else _.first(dataSets)

@drawTopTeamsProgressionGraph = (selector) ->
  div = divFromSelector selector
  apiCall "GET", "/api/stats/top_teams/score_progression", {}
  .done (data) ->
    apiCall "GET", "/api/time", {}
    .done (timedata) ->
      if data.data.length >= 2
        scoreData = (team.score_progression for team in data.data)

        #Ensure there are submissions to work with
        if _.max(_.map(scoreData, (submissions) -> submissions.length)) > 0

          dataPoints = _.zip.apply _, progressionDataToPoints scoreData, 720, timedata.data

          teamNameData = (team.name for team in data.data)

          graphData = [["Score"].concat(teamNameData)]

          _.each dataPoints, (dataPoint) ->
            graphData.push [""].concat(dataPoint)

          packagedData = google.visualization.arrayToDataTable graphData

          chart = new google.visualization.SteppedAreaChart(div)
          chart.draw(packagedData, topTeamsGraphOptions)

@drawTeamProgressionGraph = (selector, container_selector) ->
  div = divFromSelector selector
  apiCall "GET", "/api/stats/team/score_progression", {}
  .done (data) ->
    apiCall "GET", "/api/time", {}
    .done (timedata) ->

      if data.status == 1
          if data.data.length > 0

            graphData = [
              ["Time", "Score", {role: "tooltip"}]
            ]

            steps = progressionDataToPoints data.data, 720, timedata.data
            (graphData.push(["", score, score]) for score in steps)

            packagedData = google.visualization.arrayToDataTable graphData

            chart = new google.visualization.SteppedAreaChart(div)
            chart.draw(packagedData, teamGraphOptions)
          else
            $(container_selector).hide()
        else
          $(container_selector).hide()
