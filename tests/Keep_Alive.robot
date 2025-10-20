*** Settings ***
Library    SeleniumLibrary
Library    Screenshot

Resource    Keep_Alive.robot


*** Variables ***
${INTERNAL_PASS}    Passwd@02

# *** Test Cases ***


*** Keywords ***
Check And Handle Session Expired Popup
    ${popup_visible}=    Run Keyword And Return Status    Page Should Contain Element    id=ModGetPassword    timeout=1s
    Run Keyword If    ${popup_visible}    Enter Password Credentials
Enter Password Credentials
    Wait Until Element Is Visible    id=ModGetPassword    timeout=2s
    ${password_input_locator}=    Set Variable    xpath=//div[@id='DvUPassInput']//input[@id='PassInput' and @type='password' and @name='PassInput']
    Wait Until Element Is Visible    ${password_input_locator}    timeout=2s
    Input Text    ${password_input_locator}    ${INTERNAL_PASS}
    # Click Accept Button
    ${Accept_xpath}=    Set Variable    xpath=//div[@class='dvModGetPasswordCtrl']//input[@id='passBtnOK' and @type='button' and @value='Accept']
    Click Element    ${Accept_xpath}