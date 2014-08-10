renderProblemList = _.template($("#problem-list-template").remove().text())
renderProblem = _.template($("#problem-template").remove().text())
renderProblemSubmit = _.template($("#problem-submit-template").remove().text())
renderProblemReview = _.template($("#problem-review-template").remove().text())

@ratingMetrics = ["difficulty", "enjoyment", "educational-value"]

submitProblem = (e) ->
  e.preventDefault()
  input = $(e.target).find("input")
  apiCall "POST", "/api/problems/submit", {pid: input.data("pid"), key: input.val()}
  .done (data) ->
    apiNotify(data)
    if data['status'] is 1
      loadProblems()

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

  apiCall "POST", "/api/problems/feedback", {feedback: feedback}
  .done (data) ->
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
        $("#problem-list-holder").html renderProblemList({
          problems: data.data,
          renderProblem: renderProblem,
          renderProblemSubmit: renderProblemSubmit,
          renderProblemReview: renderProblemReview
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
