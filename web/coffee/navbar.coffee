apiOffline =  
  FAQ: "/faq"
  Game: "/game-preview"
  Teachers: "/teachers"
  Sponsors: "/sponsors"
  Contact: "/contact"

teacherLoggedIn =
  Game: "/game/"
  Problems: "/problems"
  Shell: "/shell"
  Scoreboard: "/scoreboard"
  Classroom: "/classroom"
  About:
    FAQ: "/faq"
    Sponsors: "/sponsors"
    #News: "/news"
    Teachers: "/teachers"
    Contact: "/contact"
  Account:
    Manage: "/account"
    Logout: "/logout"

teacherLoggedInNoCompetition =  
  Classroom: "/classroom"  
  Game: "/game-preview"
  FAQ: "/faq"    
  #News: "/news"  
  Teachers: "/teachers"
  Sponsors: "/sponsors"
  Contact: "/contact"    
  Account:
    Manage: "/account"
    Logout: "/logout"

userLoggedIn =
  Game: "/game/"
  Problems: "/problems"
  Shell: "/shell"
  Team: "/team"
  Scoreboard: "/scoreboard"
  About:
    FAQ: "/faq"
    Contact: "/contact"  
    Sponsors: "/sponsors"
    #News: "/news"
  Account:
    Manage: "/account"
    Logout: "/logout"

userLoggedInNoCompetition =       
  Team: "/team"
  Game: "/game-preview"
  FAQ: "/faq"    
  # News: "/news"
  Sponsors: "/sponsors"
  Contact: "/contact"  
  Account:
    Manage: "/account"
    Logout: "/logout"


userNotLoggedIn =
  Registration: "/registration"
  Game: "/game-preview"
  # Scoreboard: "/scoreboard"  
  # About:
  #  FAQ: "/faq"
  #  Sponsors: "/sponsors"
  #  News: "/news"
  FAQ: "/faq"
  # News: "/news"
  Teachers: "/teachers"
  Sponsors: "/sponsors"
  Contact: "/contact"
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

  .fail ->
    navbarLayout.links = apiOffline
    $("#navbar-links").html renderNavbarLinks(navbarLayout)

$ ->
  renderNavbarLinks = _.template($("#navbar-links-template").remove().text())
  renderNestedNavbarLinks = _.template($("#navbar-links-dropdown-template").remove().text())

  loadNavbar(renderNavbarLinks, renderNestedNavbarLinks)
