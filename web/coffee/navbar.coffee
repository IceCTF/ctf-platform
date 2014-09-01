
apiOffline =
  2013: "https://2013.picoctf.com"
  News: "/news"

teacherLoggedIn =
  2013: "https://2013.picoctf.com"
  Game: "/game/"
  Problems: "/problems"
  Shell: "/shell"
  Scoreboard: "/scoreboard"
  Classroom: "/classroom"
  About:
    FAQ: "/faq"
    Sponsors: "/sponsors"
    News: "/news"
    Teachers: "/teachers"
  Account:
    Manage: "/account"
    Logout: "/logout"

teacherLoggedInNoCompetition =  
  2013: "https://2013.picoctf.com"
  Classroom: "/classroom"  
  FAQ: "/faq"    
  News: "/news"
  Contact: "/contact"
  Teachers: "/teachers"
  Account:
    Manage: "/account"
    Logout: "/logout"

userLoggedIn =
  2013: "https://2013.picoctf.com"
  Game: "/game/"
  Problems: "/problems"
  Shell: "/shell"
  Team: "/team"
  Scoreboard: "/scoreboard"
  About:
    FAQ: "/faq"
    Sponsors: "/sponsors"
    News: "/news"
  Account:
    Manage: "/account"
    Logout: "/logout"

userLoggedInNoCompetition =       
  2013: "https://2013.picoctf.com"
  Team: "/team"  
  FAQ: "/faq"    
  News: "/news"
  Contact: "/contact"  
  Account:
    Manage: "/account"
    Logout: "/logout"


userNotLoggedIn =
  2013: "https://2013.picoctf.com"
  Registration: "/registration"
  # Scoreboard: "/scoreboard"  
  # About:
  #  FAQ: "/faq"
  #  Sponsors: "/sponsors"
  #  News: "/news"
  FAQ: "/faq"
  News: "/news"
  Contact: "/contact"
  Teachers: "/teachers"
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

  .fail ->
    navbarLayout.links = apiOffline
    $("#navbar-links").html renderNavbarLinks(navbarLayout)

$ ->
  renderNavbarLinks = _.template($("#navbar-links-template").remove().text())
  renderNestedNavbarLinks = _.template($("#navbar-links-dropdown-template").remove().text())

  loadNavbar(renderNavbarLinks, renderNestedNavbarLinks)
