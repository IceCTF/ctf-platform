renderProblemList = _.template($("#problem-list-template").remove().text())
renderProblem = _.template($("#problem-template").remove().text())
renderProblemSubmit = _.template($("#problem-submit-template").remove().text())
renderProblemReview = _.template($("#problem-review-template").remove().text())
renderAchievementMessage = _.template($("#achievement-message-template").remove().text())

@ratingMetrics = ["Difficulty", "Enjoyment", "Educational Value"]
@ratingQuestion = {"Difficulty": "How difficult is this problem?", "Enjoyment": "Did you enjoy this problem?", "Educational Value": "How much did you learn while solving this problem?"}
@ratingChoices = {"Difficulty": ["Too easy", "", "A bit challenging", "", "Very hard"], "Enjoyment": ["Hated it!", "", "It was okay.", "", "Loved it!"], "Educational Value": ["Nothing at all","", "Something useful", "", "Learned a lot!"]}

@timeValues = ["5 minutes or less", "10 minutes", "20 minutes", "40 minutes", "1 hour", "2 hours", "3 hours", "4 hours", "5 hours", "6 hours", "8 hours", "10 hours", "15 hours", "20 hours", "30 hours", "40 hours or more"]

sanitizeMetricName = (metric) ->
  metric.toLowerCase().replace(" ", "-")


constructAchievementCallbackChainHelper = (achievements, index) ->
  $(".modal-backdrop").remove()
  if index >= 0
    messageDialog renderAchievementMessage({achievement: achievements[index]}),
      "Achievement Unlocked!", "OK", () -> constructAchievementCallbackChainHelper achievements, index-1

constructAchievementCallbackChain = (achievements) ->
  constructAchievementCallbackChainHelper achievements, achievements.length-1

submitProblem = (e) ->
  e.preventDefault()
  input = $(e.target).find("input")
  apiCall "POST", "/api/problems/submit", {pid: input.data("pid"), key: input.val()}
  .done (data) ->
    if data['status'] is 1
      ga('send', 'event', 'Problem', 'Solve', 'Basic')
      loadProblems()
      setTimeout( ->
        $("div[data-target='#" + input.data("pid") + "']").click()
      , 100)
    else
      ga('send', 'event', 'Problem', 'Wrong', 'Basic')
    apiNotify data
    apiCall "GET", "/api/achievements"
    .done (data) ->
      if data['status'] is 1
        new_achievements = (x for x in data.data when !x.seen)
        constructAchievementCallbackChain new_achievements

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
  sliderName = "#slider-" + pid
  feedback.timeSpent = $(sliderName).slider("option", "value");
  feedback.source = 'basic'

  postData = {feedback: JSON.stringify(feedback), pid: pid}

  apiCall "POST", "/api/problems/feedback", postData
  .done (data) ->
    loadProblems()
    apiNotify data
    ga('send', 'event', 'Problem', 'Review', 'Basic')
    apiCall "GET", "/api/achievements"
    .done (data) ->
      if data['status'] is 1
        new_achievements = (x for x in data.data when !x.seen)
        constructAchievementCallbackChain new_achievements

toggleHint = (e) ->
  pid = $(e.target).data("pid")
  ga('send', 'event', 'Problem', 'OpenHint', 'Basic')
  apiCall "GET", "/api/problems/hint", {"pid": pid, "source": "basic"}
  #$("#"+pid+"-hint").toggle("fast")

loadProblems = ->
  apiCall "GET", "/api/problems"
  .done (data) ->
    switch data["status"]
      when 0
        apiNotify(data)
      when 1
      	# We want the score to be level with the title, but the title
	# is defined in a template. This solution is therefore a bit
	# of a hack.
        addScoreToTitle("#title")
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

          $( ".time-slider" ).slider {
            value: 4,
            min: 0,
            max: 15,
            step: 1,
            slide: ( event, ui ) ->
              $( "#" + $(this).data("label-target")).html( window.timeValues[ui.value] );
          }

          $( ".time-slider" ).each (x) ->
            $("#" + $(this).data("label-target")).html(window.timeValues[4]);

          #Should solved problem descriptions still be able to be viewed?
          #$("li.disabled>a").removeAttr "href"

          $(".problem-hint").hide()
          $(".problem-submit").on "submit", submitProblem
          $(".info-span").on "click", toggleHint
          $(".hint-tab-button").on "click", toggleHint

          $(".problem-review-form").on "submit", addProblemReview

addScoreToTitle = (selector) ->
        apiCall "GET", "/api/team/score", {}
        .done (data) ->
          if data.data
            $(selector).children("#team-score").remove()
            $(selector).append("<span id='team-score' class='pull-right'>Score: " + data.data.score + "</span>")
$ ->
  loadProblems()
