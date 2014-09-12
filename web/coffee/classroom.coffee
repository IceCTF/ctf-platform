renderGroupInformation = _.template($("#group-info-template").remove().text())

renderTeamSelection = _.template($("#team-selection-template").remove().text())

google.load 'visualization', '1.0', {'packages':['corechart']}

@groupListCache = []

addHoverLabel = (target, container, message) ->    
    $(target).load () -> 
      gridLabel = $("<div>").text(message).width(target.width())
      container.append(gridLabel)    
      gridLabel.css("top", (target.height()/2-gridLabel.height()/2 + target.position().top) + "px").addClass("hover-label")      
      gridLabel.css("left", target.css("left"))
      gridLabelBottom = $("<div>").addClass("fuzzy-top").width(target.width())      
      gridLabelBottom.css("left", target.css("left"))
      gridLabelBottom.css("top", (gridLabel.position().top - 15) + "px").height(15)
      container.append(gridLabelBottom)   
      gridLabelTop = $("<div>").addClass("fuzzy-bottom").width(target.width())      
      gridLabelTop.css("left", target.css("left")).height(15)
      gridLabelTop.css("top", (gridLabel.position().top + gridLabel.outerHeight()) + "px").height(15)
      container.append(gridLabelTop)   

teamSelectionHandler = (e) ->
  tid = $(e.target).data("tid")
  apiCall "GET", "/api/stats/team/solved_problems", {tid: tid}
  .done (data) ->
    if data.status == 1
      drawTeamSolvedVisualization data.data, tid
    else
      elementString = "##{tid}>.panel-body>div>.team-visualizer"
      $(elementString).empty()
      $(elementString).append("<img id='graph-placeholder-#{tid}' class='faded-chart' src='img/classroom_graph.png'>")
      addHoverLabel $("#graph-placeholder-#{tid}"), $(elementString), "Once the competition starts, you'll be able to check out the progress of the team here."

# JB: I think this function can be removed
loadTeamSelection = (gid) ->
  apiCall "GET", "/api/group/member_information", {gid: gid}
  .done (data) ->
    ga('send', 'event', 'Group', 'LoadTeacherGroupInformation', 'Success')
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

  visualElementString = "##{tid}>.panel-body>div>.team-visualizer"
  chart = new google.visualization.ColumnChart _.first($(visualElementString))
  chart.draw packagedData, options

createGroupSetup = () ->
    formDialogContents = _.template($("#new-group-template").html())({})
    formDialog formDialogContents, "Create a New Class", "OK", "new-group-name", () ->
        createGroup($('#new-group-name').val())

loadGroupManagement = (groups, showFirstTab, callback) ->
  $("#group-management").html renderGroupInformation({data: groups})
    
  $("#new-class-tab").on "click", (e) -> 
    createGroupSetup()

  $("#new-class-button").on "click", (e) -> 
    createGroupSetup()
  
  $("#class-tabs").on 'shown.bs.tab', 'a[data-toggle="tab"]', (e) ->
    tabBody = $(this).attr("href")
    groupName = $(this).data("group-name")
    apiCall "GET", "/api/group/member_information", {gid: $(this).data("gid")}
    .done (teamData) ->        
        ga('send', 'event', 'Group', 'LoadTeacherGroupInformation', 'Success')
        apiCall "GET", "/api/user/status", {}
        .done (userData) ->
            $(tabBody).html renderTeamSelection({teams: teamData.data, groupName: groupName, userStatus: userData.data})
            $(".team-visualization-enabler").on "click", (e) ->
                teamSelectionHandler e  
            
  if showFirstTab
    $('#class-tabs a:first').tab('show')

  $("#group-request-form").on "submit", groupRequest
  $(".delete-group-span").on "click", (e) ->
    deleteGroup $(e.target).data("group-name")
    
  if callback
    callback()

loadGroupInfo = (showFirstTab, callback) ->
  apiCall "GET", "/api/group/list", {}
  .done (data) ->
    switch data["status"]
      when 0
        apiNotify(data)
        ga('send', 'event', 'Group', 'GroupListLoadFailure', data.message)
      when 1
        window.groupListCache = data.data
        loadGroupManagement data.data, showFirstTab, callback   

createGroup = (groupName) ->
  apiCall "POST",  "/api/group/create", {"group-name": groupName}
  .done (data) ->            
    if data['status'] is 1
      closeDialog()
      ga('send', 'event', 'Group', 'CreateGroup', 'Success')
      apiNotify(data)    
      loadGroupInfo(false, () -> 
                     $('#class-tabs li:eq(-2) a').tab('show'))
    else
      ga('send', 'event', 'Group', 'CreateGroup', 'Failure::' + data.message)
      apiNotifyElement($("#new-group-name"), data)
        
deleteGroup = (groupName) ->
  confirmDialog("You are about to permanently delete this class. This will automatically remove your students from this class. Are you sure you want to delete this class?", 
                "Class Confirmation", "Delete Class", "Cancel", 
                () ->
                  apiCall "POST", "/api/group/delete", {"group-name": groupName}
                  .done (data) ->
                    apiNotify(data)
                    if data['status'] is 1
                      ga('send', 'event', 'Group', 'DeleteGroup', 'Success')
                      loadGroupInfo(true)
                    else
                      ga('send', 'event', 'Group', 'DeleteGroup', 'Failure::' + data.message)
               ,() -> 
                  ga('send', 'event', 'Group', 'DeleteGroup', 'RejectPrompt'))

#Could be simplified without this function
groupRequest = (e) ->
  e.preventDefault()
  groupName = $("#group-name-input").val()
  createGroup groupName

$ ->
  loadGroupInfo(true)
  return
