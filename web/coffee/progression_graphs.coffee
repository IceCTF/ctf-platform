google.load 'visualization', '1.0', {'packages':['corechart']}

divFromSelector = (selector) ->
  _.first($(selector))

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

progressionDataToPoints = (data, bucketWindow, dataPoints) ->
      buckets = timestampsToBuckets data, "time", bucketWindow
      steps = maxValuesFromBucketsExtended buckets, "score"

      if steps.length < dataPoints
        return steps

      return _.rest(steps, steps.length - dataPoints)

@drawTeamProgressionGraph = (selector, points) ->
  div = divFromSelector selector
  apiCall "GET", "/api/stats/team/score_progression", {}
  .done (data) ->
    if data.data.length > 0

      graphData = [
        ["Time", "Score", {role: "tooltip"}]
      ]
      
      steps = progressionDataToPoints data.data, 600, 30
      
      (graphData.push(["", score, score]) for score in steps)

      console.log graphData

      packagedData = google.visualization.arrayToDataTable graphData

      chart = new google.visualization.SteppedAreaChart(div)
      chart.draw(packagedData, teamGraphOptions)

