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
  max = _.last(samples)[key]

  bucketNumber = (number) ->
    Math.floor((number - min) / seconds)

  continuousBucket = {}
  maxBuckets = bucketNumber max

  for i in [0..maxBuckets]
    continuousBucket[i] = []

  buckets = _.groupBy samples, (sample) ->
    bucketNumber sample[key]

  return _.extend continuousBucket, buckets

maxValuesFromBuckets = (buckets, sampleKey) ->
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
      
    packagedData = google.visualization.arrayToDataTable graphData

    chart = new google.visualization.LineChart(div)
    chart.draw(packagedData, teamGraphOptions)

