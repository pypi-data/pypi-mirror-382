*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote


*** Variables ***

${RESOURCE_DIR}  ${CURDIR}

${BROWSER}  chrome

${SELECTOR_ADDONS_ENABLED}  jquery=#activated-products
${SELECTOR_ADDONS_MOSAIC}  ${SELECTOR_ADDONS_ENABLED} ul li h3:contains('Mosaic')

${SELECTOR_CONTENTMENU_DISPLAY_LINK}  css=#plone-contentmenu-display a
${SELECTOR_CONTENTMENU_DISPLAY_ITEMS}  css=#plone-contentmenu-display ul

${SELECTOR_TOOLBAR}  css=#edit-zone

${SELENIUM_RUN_ON_FAILURE}  Capture page screenshot and log source

*** Keywords ***

a logged-in manager
  Enable autologin as  Manager

a logged-in site administrator
  Enable autologin as  Site Administrator  Contributor  Reviewer

an example document
  Create content  type=Document
  ...  id=example-document
  ...  title=Example Document
  ...  description=This is an example document
  ...  text=<p>This document will soon have a custom layout.</p>

select mosaic layout view
  Go to  ${PLONE_URL}/example-document

  Wait Until Element Is Visible  ${SELECTOR_CONTENTMENU_DISPLAY_LINK}
  Click element  ${SELECTOR_CONTENTMENU_DISPLAY_LINK}
  Wait Until Element Is Visible  id=plone-contentmenu-display-layout_view

  Mouse over  id=plone-contentmenu-display-layout_view
  Wait for then click element  id=plone-contentmenu-display-layout_view

Setup Mosaic Example Page
    Open test browser

    Given a logged-in site administrator
      and an example document
     then select mosaic layout view

    Run keyword and ignore error  Set window size  1024  1500


# ----------------------------------------------------------------------------
# Backport and simplified from outdated Selenium2Screenshots
# ----------------------------------------------------------------------------

Update element style
    [Arguments]  ${locator}  ${name}  ${value}
    ${elem}  Get WebElement  ${locator}
    Execute Javascript  arguments[0].style.${name} = "${value}";  ARGUMENTS  ${elem}


Highlight
    [Documentation]  Add highlighting around given locator
    [Arguments]  ${locator}
    ...          ${width}=3px
    ...          ${style}=dotted
    ...          ${color}=red
    Update element style  ${locator}  border  ${style} ${color} ${width}


Clear Highlight
    [Arguments]  ${locator}
    Update element style  ${locator}  border  none
