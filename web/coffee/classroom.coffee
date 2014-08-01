renderGroupInformation = _.template($("#group-info-template").remove().text())

load_group_info = ->
  $.get "/api/group"
  .done (data) ->
    switch data["status"]
      when 0
        apiNotify(data)
      when 1
        $("#group-management").html renderGroupInformation({data: data.data})

        $("#group-request-form").on "submit", group_request
        $(".delete-group-span").on "click", (e) ->
          delete_group $(e.target).data("group-name")

create_group = (group_name) ->
  $.post "/api/group/create", {"group-name": group_name}
  .done (data) ->
    apiNotify(data)
    if data['status'] is 1
      load_group_info()

delete_group = (group_name) ->
  $.post "/api/group/delete", {"group-name": group_name}
  .done (data) ->
    apiNotify(data)
    if data['status'] is 1
      load_group_info()

#Could be simplified without this function
group_request = (e) ->
  e.preventDefault()

  group_name = $("#group-name-input").val()
  create_group group_name

$ ->
  load_group_info()
  return
