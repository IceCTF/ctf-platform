renderProblemList = _.template($("#problem-list-template").remove().text())
renderProblem = _.template($("#problem-template").remove().text())
renderProblemSubmit = _.template($("#problem-submit-template").remove().text())
renderProblemReview = _.template($("#problem-review-template").remove().text())

@ratingMetrics = ["Difficulty", "Enjoyment", "Educational Value"]

sanitizeMetricName = (metric) ->
  metric.toLowerCase().replace(" ", "-")

submitProblem = (e) ->
  e.preventDefault()
  input = $(e.target).find("input")
  apiCall "POST", "/api/problems/submit", {pid: input.data("pid"), key: input.val()}
  .done (data) ->
    if data['status'] is 1
      loadProblems()
      apiNotify(data)
      setTimeout( ->
        $("div[data-target='#" + input.data("pid") + "']").click()
      , 100)

addProblemReview = (e) ->
  e.preventDefault()
  
  feedback = {
    metrics: {}
    comment: ""
  }

  serialized = $(e.target).serializeObject()

  _.each serialized, (value, key) ->
    match = key.match(/^rating-(.+)/)
    if match and match.length == 2
      feedback.metrics[match[1]] = parseInt(value)
    else
      feedback.comment = value

  pid = $(e.target).data("pid")

  postData = {feedback: JSON.stringify(feedback), pid: pid}

  apiCall "POST", "/api/problems/feedback", postData
  .done (data) ->
    loadProblems()
    apiNotify data

toggleHint = (e) ->
  pid = $(e.target).data("pid")
  $("#"+pid+"-hint").toggle("fast")

loadProblems = ->
  apiCall "GET", "/api/problems"
  .done (data) ->
    switch data["status"]
      when 0
        apiNotify(data)
      when 1
        apiCall "GET", "/api/problems/feedback/reviewed", {}
        .done (reviewData) ->
          $("#problem-list-holder").html renderProblemList({
            problems: data.data,
            reviewData: reviewData.data,
            renderProblem: renderProblem,
            renderProblemSubmit: renderProblemSubmit,
            renderProblemReview: renderProblemReview,
            sanitizeMetricName: sanitizeMetricName
          })
  
          #Should solved problem descriptions still be able to be viewed?
          #$("li.disabled>a").removeAttr "href"

          $(".problem-hint").hide()
          $(".problem-submit").on "submit", submitProblem
          $(".info-span").on "click", toggleHint

          $(".problem-rating").rating({
            showClear: false,
            min: 0,
            max: 5,
            step: 0.5,
            size: "xs",
            showCaption: false
          })

          $(".problem-review-form").on "submit", addProblemReview

$ ->
  loadProblems()
