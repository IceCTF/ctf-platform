renderShellAccountCredentials = _.template($("#shell-account-credentials-template").remove().text())

$ ->
  apiCall "GET", "/api/user/shell", {}
  .done (data) ->
    console.log data
    $("#shell-account-credentials").html renderShellAccountCredentials({account: data.data})
