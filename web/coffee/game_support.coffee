@renderProblemReview = _.template($("#problem-review-template").remove().text())

@ratingMetrics = ["Difficulty", "Enjoyment", "Educational Value"]
@ratingQuestion = {"Difficulty": "How difficult is this problem?", "Enjoyment": "Did you enjoy this problem?", "Educational Value": "How much did you learn by doing this problem?"}
@ratingChoices = {"Difficulty": ["Very Easy", "", "Average", "", "Too Hard"], "Enjoyment": ["Hated it!", "", "Neutral", "", "Loved it!"], "Educational Value": ["Learned Nothing","", "Some New Things", "", "A Lot"]}

@timeValues = ["5 minutes or less", "10 minutes", "20 minutes", "40 minutes", "1 hour", "2 hours", "3 hours", "4 hours", "5 hours", "6 hours", "8 hours", "10 hours", "15 hours", "20 hours", "30 hours", "40 hours or more"]

@sanitizeMetricName = (metric) ->
  metric.toLowerCase().replace(" ", "-")


@addProblemReview = (e) ->
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
  feedback.source = 'game'

  postData = {feedback: JSON.stringify(feedback), pid: pid}

  apiCall "POST", "/api/problems/feedback", postData
  .done (data) ->
    apiNotify data
    ig.game.getEntitiesByType(EntityQuestions)[0].CloseLearnPanel();
    ig.gui.element.action('showGroup', 'Group_QA');
    ig.gui.element.action('enableGroup', 'Group_QA');
    ig.gui.element.action('disableGroup', 'Group_QA_Learn');
    ig.gui.element.action('hideGroup', 'Group_QA_Learn');

@toggleHint = (e) ->
  pid = $(e.target).data("pid")
  apiCall "GET", "/api/problems/hint", {"pid": pid, "source": "game"}
