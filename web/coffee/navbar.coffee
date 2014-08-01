
apiOffline =
  News: "/news"

teacherLoggedIn =
  Problems: "/problems"
  Scoreboard: "/scoreboard"
  Classroom: "/classroom"
  About:
    FAQ: "/faq"
    Sponsors: "/sponsors"
    News: "/news"
  Logout: "/logout"

userLoggedIn =
  Problems: "/problems"
  Team: "/team"
  Scoreboard: "/scoreboard"
  About:
    FAQ: "/faq"
    Sponsors: "/sponsors"
    News: "/news"
  Logout: "/logout"

userNotLoggedIn =
  Registration: "/registration"
  Scoreboard: "/scoreboard"
  About:
    FAQ: "/faq"
    Sponsors: "/sponsors"
    News: "/news"
  Login: "/login"

loadNavbar = (renderNavbarLinks, renderNestedNavbarLinks) ->

  navbarLayout = {
    renderNavbarLinks: renderNavbarLinks,
    renderNestedNavbarLinks: renderNestedNavbarLinks
  }

  apiCall "GET", "/api/user/status", {}
  .done (data) ->
    navbarLayout.links = userNotLoggedIn

    if data["status"] == 1
      if data.data["teacher"]
        navbarLayout.links = teacherLoggedIn
      else if data.data["logged_in"]
        navbarLayout.links = userLoggedIn

    $("#navbar-links").html renderNavbarLinks(navbarLayout)

  .fail ->
    navbarLayout.links = apiOffline
    $("#navbar-links").html renderNavbarLinks(navbarLayout)

$ ->
  renderNavbarLinks = _.template($("#navbar-links-template").remove().text())
  renderNestedNavbarLinks = _.template($("#navbar-links-dropdown-template").remove().text())

  loadNavbar(renderNavbarLinks, renderNestedNavbarLinks)
