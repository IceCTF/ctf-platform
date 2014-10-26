apiOffline =
  FAQ: "/faq"
  Teachers: "/teachers"
  Sponsors: "/sponsors"
  About: "/about"

teacherLoggedIn =
  Game: "/game/"
  Shell: "/shell"
  Scoreboard: "/scoreboard"
  Classroom: "/classroom"
  About:
    FAQ: "/faq"
    Sponsors: "/sponsors"
    Teachers: "/teachers"
    About: "/about"
  Account:
    Manage: "/account"
    Logout: "#"

teacherLoggedInNoCompetition =
  Classroom: "/classroom"
  About: "/about"
  FAQ: "/faq"
  Teachers: "/teachers"
  Sponsors: "/sponsors"
  Account:
    Manage: "/account"
    Logout: "#"

userLoggedIn =
  Game: "/game/"
  Shell: "/shell"
  Team: "/team"
  Chat: "/chat"
  Scoreboard: "/scoreboard"
  About:
    FAQ: "/faq"
    About: "/about"
    Sponsors: "/sponsors"
  Account:
    Manage: "/account"
    Logout: "#"

userLoggedInNoCompetition =
  Team: "/team"
  Chat: "/chat"
  About: "/about"
  FAQ: "/faq"
  Sponsors: "/sponsors"
  Account:
    Manage: "/account"
    Logout: "#"


userNotLoggedIn =
  About: "/about"
  FAQ: "/faq"
  Teachers: "/teachers"
  Sponsors: "/sponsors"
  Login: "/login"

loadNavbar = (renderNavbarLinks, renderNestedNavbarLinks) ->

  navbarLayout = {
    renderNavbarLinks: renderNavbarLinks,
    renderNestedNavbarLinks: renderNestedNavbarLinks
  }

  apiCall "GET", "/api/user/status", {}
  .done (data) ->
    navbarLayout.links = userNotLoggedIn
    navbarLayout.topLevel = true
    if data["status"] == 1
      if not data.data["logged_in"]
        $(".show-when-logged-out").css("display", "inline-block")
      if data.data["teacher"]
        if data.data["competition_active"]
           navbarLayout.links = teacherLoggedIn
        else
           navbarLayout.links = teacherLoggedInNoCompetition
      else if data.data["logged_in"]
         if data.data["competition_active"]
            navbarLayout.links = userLoggedIn
         else
            navbarLayout.links = userLoggedInNoCompetition
    $("#navbar-links").html renderNavbarLinks(navbarLayout)
    $("#navbar-item-logout").on("click", logout)

  .fail ->
    navbarLayout.links = apiOffline
    $("#navbar-links").html renderNavbarLinks(navbarLayout)

$ ->
  renderNavbarLinks = _.template($("#navbar-links-template").remove().text())
  renderNestedNavbarLinks = _.template($("#navbar-links-dropdown-template").remove().text())

  loadNavbar(renderNavbarLinks, renderNestedNavbarLinks)
