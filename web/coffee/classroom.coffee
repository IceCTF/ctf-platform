renderGroupInformation = _.template($("#group-info-template").remove().text())
renderGroupSelection = _.template($("#group-selection-template").remove().text())

renderTeamSelection = _.template($("#team-selection-template").remove().text())

google.load 'visualization', '1.0', {'packages':['corechart']}

@groupListCache = []

loadGroupSelection = (groups) ->
  $("#group-selection").html renderGroupSelection({groups: groups})

  $("#group-selector").on "change", (e) ->
    selectedGroupName = $("#group-selector").val()

    #Clears the pane on none selected.
    if selectedGroupName == "none-selected"
      $("#team-selection").html ""

    _.each groups, (group) ->
      if group.name == selectedGroupName
        loadTeamSelection group.gid

    return

teamSelectionHandler = (e) ->
  tid = $(e.target).data("tid")
  apiCall "GET", "/api/stats/team/solved_problems", {tid: tid}
  .done (data) ->
    if data.status == 1
      drawTeamSolvedVisualization data.data, tid
    else
      elementString = "##{tid}>.panel-body>div>.team-visualizer"
      $(elementString).empty()
      $(elementString).append("<img class='faded-chart' src='img/classroom_graph.png'>")

loadTeamSelection = (gid) ->
  apiCall "GET", "/api/group/member_information", {gid: gid}
  .done (data) ->
    $("#team-selection").html renderTeamSelection({teams: data.data})

    $(".team-visualization-enabler").on "click", (e) ->
      teamSelectionHandler e

    return

drawTeamSolvedVisualization = (teamData, tid) ->
  members = _.keys(teamData.members)
  users = ["users"].concat members, "Unsolved", {role: 'annotation'}
  graphData = [users]

  _.each teamData.problems, (problems, category) ->
    categoryData = [category]
    solvedSet = []

    _.each teamData.members, (solved, member) ->
      userSolved = _.intersection solved, problems
      categoryData.push userSolved.length

      solvedSet = _.union solvedSet, userSolved

    #Number of unsolved problems
    categoryData.push _.difference(problems, solvedSet).length
    categoryData.push ''

    graphData.push categoryData

  packagedData = google.visualization.arrayToDataTable graphData

  options = {
    height: 400,
    legend: {position: 'top', maxLines: 3},
    bar: {groupWidth: '75%'},
    isStacked: true,
    colors: ["#2FA4F0", "#B9F9D0", "#2E5CC0", "#8BADE0", "#E6BF70", "#CECFF0", "#30A0B0"]
    series: {},
    title: "Problem Overview"
  }

  options.series[members.length] = {color: "black", visibleInLegend: false}

  console.log options

  visualElementString = "##{tid}>.panel-body>div>.team-visualizer"
  chart = new google.visualization.ColumnChart _.first($(visualElementString))
  chart.draw packagedData, options

loadGroupManagement = (groups) ->
  $("#group-management").html renderGroupInformation({data: groups})
  $("#group-request-form").on "submit", groupRequest
  $(".delete-group-span").on "click", (e) ->
    deleteGroup $(e.target).data("group-name")

loadGroupInfo = ->
  apiCall "GET", "/api/group/list", {}
  .done (data) ->
    switch data["status"]
      when 0
        apiNotify(data)
      when 1
        window.groupListCache = data.data
        loadGroupManagement data.data
        loadGroupSelection data.data

createGroup = (groupName) ->
  apiCall "POST",  "/api/group/create", {"group-name": groupName}
  .done (data) ->
    apiNotify(data)
    if data['status'] is 1
      loadGroupInfo()

deleteGroup = (groupName) ->
  confirmDialog("You are about to permanently delete this class. This will automatically remove your students from this class. Are you sure you want to delete this class?", 
                "Class Confirmation", "Delete Class", "Cancel", 
                () ->
                  apiCall "POST", "/api/group/delete", {"group-name": groupName}
                  .done (data) ->
                    apiNotify(data)
                    if data['status'] is 1
                      loadGroupInfo())

#Could be simplified without this function
groupRequest = (e) ->
  e.preventDefault()

  groupName = $("#group-name-input").val()
  createGroup groupName

$ ->
  loadGroupInfo()
  return
