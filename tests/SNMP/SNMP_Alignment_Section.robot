*** Settings ***
Documentation                This is a basic test
Library    SeleniumLibrary
Library    String
Library    Collections
Library    OperatingSystem    #for file operations
Library    BuiltIn
Library    XML
Library    DateTime
Library    Screenshot    ${OUTPUTDIR}/screenshots
# Suite Setup    Setup Command_Assignments Pretests
# Suite Teardown    Close Browser

*** Variables ***
#VALID LOGIN & ACCES TO WEBPAGE
${USER}    admin
${PASS}    Passwd%4002    #Login PASS
${INTERNAL_PASS}    Passwd@02    
${URL_BASE}    https://


# ${terminal_title}    EUT Setup 1
# ${IP_ADDRESS}    10.212.43.11

# ${terminal_title}    AUX Setup 1
# ${IP_ADDRESS}    10.212.43.12

# ${terminal_title}    EUT Setup 2
# ${IP_ADDRESS}    10.212.43.21

${terminal_title}    EUT Setup 1
${IP_ADDRESS}    10.212.43.87

${URL_COMPLETA}=    ${URL_BASE}${USER}:${PASS}@${IP_ADDRESS}
#popup login method
${TPU_WelcomeTitle_Type}    css=div.text-center.headerCenter.col h4
# ${TerminalTitle}    Terminal 1
#Section title

# ${Section_Type}    css=div.text-center.headerCenter.col h2

#*************************************************************************************************************************
# MODULES
${IBTU}    112
${IDTU}    32
${IETU}    64
${IOTU}    80
${ICTU}    128
${IPTU}    16
${IPTU.10}    272
${IRTU}    96
${DSTU}    144
${MCTU}    160
${IOCT}    176
${IPIT}    192
${IEPT}    224
${IOCS}    256
${ICPT}    288
@{Teleprotection_list}        ${IBTU}    ${IDTU}    ${IETU}    ${IOTU}    ${IOCT}    ${IPIT}    ${IOCS}    ${ICPT}    ${DSTU}
@{ICTU_IPTU_IEPT_list}        ${ICTU}    ${IPTU}    ${IEPT}
#*************************************************************************************************************************

#OPEN AND CLOSE BROWSER PARAMETERS
${BROWSER}          chrome
${LOGOUT_BUTTON}   xpath=//button[contains(@class, 'p-button p-component p-button-rounded p-button-danger p-button-text p-button-icon-only')]
${LOGOUT_SURE}   xpath=//button[contains(@class, 'p-button p-component p-confirm-dialog-accept')]
${TPU_IMG}    xpath=//img[contains(@src, './static/media/tpu-1-300x130.868f04f7.jpg')]
${options}=  Create List  --ignore-certificate-errors  --disable-web-security  --allow-running-insecure-content
${commands}    Input/Output Alias

#************************************************************************************************************************
#BASIC CONFIGURATION TESTS
${SELECT_BUTTON}    xpath=//button[contains(text(),'Select')]


# *** Test Cases ***

#INPUT ASSIGNMENT TESTCASES:
# Input Activation_sweep_permanently
#     ${input_numbers_list}=    Create List
#     FOR    ${input_number}    IN RANGE    1    19
#         Append To List    ${input_numbers_list}    ${input_number}
#     END
#     Input Activation/desactivation    1    0    ${input_numbers_list}
# Inputs Desactivation
#     Input Activation/desactivation    0
#     Sleep    3s
# Input Activation_severalinputs_30s
#     ${input_numbers_list}=    Create List

#     Append To List    ${input_numbers_list}    1
#     Append To List    ${input_numbers_list}    2
#     Append To List    ${input_numbers_list}    17

#     Input Activation/desactivation    1    0    ${input_numbers_list}
# Inputs Desactivation
#     Input Activation/desactivation    0
#     Sleep    2s
# Input Activation_severalinputs_InvalidDuration
#     ${input_numbers_list}=    Create List

#     Append To List    ${input_numbers_list}    1
#     Append To List    ${input_numbers_list}    2
#     Append To List    ${input_numbers_list}    18

#     Input Activation/desactivation    1    342    ${input_numbers_list}

# Input Activation_severalinputs_InvalidInputNumbers
#     ${input_numbers_list}=    Create List

#     Append To List    ${input_numbers_list}    0
#     Append To List    ${input_numbers_list}    19
#     Append To List    ${input_numbers_list}    1

#     Input Activation/desactivation    1    0    ${input_numbers_list}

#########################################################################################################################################################

#LOOP ACTIVATION TESTCASES:
# Activate Teleprotection 1 Loop: Invalid Type
#     Configure and Program Loop    1    1    DSFFSS    30
#     Sleep    2s
# Activate Teleprotection 2 Loop: Invalid Duration
#     Configure and Program Loop    1    2    INTERNAL    32
#     Sleep    2s

# Activate Teleprotection 1 Loop
#     Configure and Program Loop    1    1    INTERNAL    0
#     Sleep    2s
# Activate Teleprotection 2 Loop
#     Configure and Program Loop    1    2    LINE    0
#     Sleep    2s

# Desactivate Teleprotection 1 Loop
#     Configure and Program Loop    0    1    INTERNAL    0
#     Sleep    2s
# Desactivate Teleprotection 2 Loop
#     Configure and Program Loop    0    2    LINE    0
#     Sleep    2s

#*************************************************************************************************************************
#BLOCKING ACTIVATION TESTCASES:

# Activate Teleprotection 2 Blocking: Invalid Duration
#     Configure and Program Blocking    1    2    32
#     Sleep    2s

# Activate Teleprotection 1 Blocking
#     Configure and Program Blocking    1    1    0
#     Sleep    2s
# Activate Teleprotection 2 Blocking
#     Configure and Program Blocking    1    2    0
#     Sleep    2s

# Desactivate Teleprotection 1 Blocking
#     Configure and Program Blocking    0    1    0
#     Sleep    2s
# Desactivate Teleprotection 2 Blocking
#     Configure and Program Blocking    0    2    0
#     Sleep    2s

#*************************************************************************************************************************

*** Keywords ***
Setup Command_Assignments Pretests
    # Test Screenshot Config
    ${ruta_screenshots}    Set Variable    ${CURDIR}/screenshots
    Set Screenshot Directory    ${ruta_screenshots}
    Log    El directorio para las capturas de pantalla es: ${ruta_screenshots}
    Open Broswer to Login page    ${URL_COMPLETA}    ${BROWSER}
    # Wait Title    ${terminal_title}
    # Sleep    3s
    # Wait Until Progress Bar Reaches 100 V2
    Wait Until Page Contains Element    xpath=//span[contains(@class, 'p-button-icon p-c pi pi-sign-out')]    timeout=50s
    Click Open Folder    /
    Click Open Folder    ALIGNMENT
    Open Section    Loops, Blocking and Test
    Wait Section Title    INPUT CIRCUITS ACTIVATION
Open Broswer to Login page
    [Arguments]    ${url}    ${brows}
    Open Browser    ${url}    ${brows}    options=add_argument("--ignore-certificate-errors")
    Maximize Browser Window
    
Close Browser
    Close All Browsers
Type In Username
    [Arguments]    ${username}
    Maximize Browser Window
    Input Text    id=Username    ${username}

Type In Password
    [Arguments]    ${password}
    Input Text    id=Password    ${password}
Submit Credentials
    Click Button   name=toIniciar

Wait Login
    Wait Until Element Is Not Visible    ${TPU_IMG}    timeout=30s


Logout
    Execute JavaScript    window.scrollBy(0, -1000)
    Sleep    1s
    Click Element    ${LOGOUT_BUTTON}

Sure_LogOut 
    Click Element    ${LOGOUT_SURE}


Click Open Folder
    [Arguments]    ${folderName}
    Scroll Element Into View Softly    xpath=//span[contains(text(), "${folderName}")]/ancestor-or-self::div[contains(@tabindex, '0')]//button[contains(@class, 'p-tree-toggler')]
    ${button}  Get WebElement  xpath=//span[contains(text(), "${folderName}")]/ancestor-or-self::div[contains(@tabindex, '0')]//button[contains(@class, 'p-tree-toggler')]
    Click Element  ${button}
    Sleep    0.1s

Open Section
    [Arguments]    ${section}
    Scroll Element Into View Softly    xpath=//span[@class='p-treenode-label' and translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${section.lower()}"]
    Sleep    0.1s
    # Scroll Element Into View Softly    xpath=//span[@class='p-treenode-label' and translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${section.lower()}"]
    #Not necessary to establish a new variable (like "button" variable from scrpt before)-> GET WEBELEMENT IS NOT NECESSARY
    #Click Element  xpath=//span[@class='p-treenode-label' and text()="${section}"]
    # Click Element    xpath=//span[@class='p-treenode-label' and translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${section.lower()}"]
    Click Element    xpath=//span[@class='p-treenode-label' and translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${section.lower()}"]
    Sleep    0.1s
Scroll Until Visible
    [Arguments]    ${locator}
    # Check if the button is visible
    ${visible}    Run Keyword And Return Status    Element Should Be Visible    ${locator}
    WHILE    '${visible}' == 'False'
        Execute JavaScript    window.scrollBy(0, window.innerHeight / 1.5)
        Sleep    0.2s
        ${visible}    Run Keyword And Return Status    Element Should Be Visible    ${locator}
    END
    Sleep    1s

Assign input/output to command
    [Arguments]    ${input}    ${command}
    #//div[contains(text(), "${input}")]:primero encuentra el texto input para cualquier <div> y seguidamente 
    #/ancestor-or-self::tr:  Busca el elemento <tr> (fila de tabla) más cercano, subiendo en la jerarquía del DOM.
    Scroll Element Into View Softly    xpath=//div[contains(text(), "${input}")]/ancestor::tr//following::input[contains(@type, 'checkbox')][${command}]
    Select Checkbox    xpath=//div[contains(text(), "${input}")]/ancestor-or-self::tr//following::input[contains(@type, 'checkbox')][${command}]
    Sleep    0.1s

Unassign input/ouptut to command
    [Arguments]    ${input}    ${command}
    Scroll Element Into View Softly    xpath=//div[contains(text(), "${input}")]/ancestor::tr//following::input[contains(@type, 'checkbox')][${command}]
    Unselect Checkbox    xpath=//div[contains(text(), "${input}")]/ancestor-or-self::tr//following::input[contains(@type, 'checkbox')][${command}]
    Sleep    0.1s
 

Scroll Element Into View Softly
    [Arguments]    ${locator}
    ${element}=    Get WebElement    ${locator}
    Execute JavaScript    arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});    ARGUMENTS    ${element}
    Sleep    0.5s


Button
    [Arguments]    ${path_name}    ${button_name}    
    ${xpath_button}    Set Variable    xpath=//button[@name='${path_name}']//span[normalize-space(text())='${button_name}']
    Scroll Element Into View Softly    ${xpath_button}
    Wait Until Element Is Visible    ${xpath_button}    timeout=5s
    Click Element    ${xpath_button}
    Sleep    0.7s
ButtonNoSleep
    [Arguments]    ${path_name}    ${button_name}    
    ${xpath_button}    Set Variable    xpath=//button[@name='${path_name}']//span[normalize-space(text())='${button_name}']
    Wait Until Element Is Visible    ${xpath_button}    timeout=5s
    Click Element    ${xpath_button}
    # Sleep    0.7s

Retrieve
    [Arguments]    ${name}
    Button    ${name}    Retrieve
    Wait Until Progress Bar Reaches 100 V2
Program
    [Arguments]    ${button_name}
    Button    ${button_name}    Program
    Wait Until Progress Bar Reaches 100 V2

Wait Until Progress Bar Reaches 100
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.5s
    Log    Waiting for the progress bar to reach 100%...
    Wait Until Keyword Succeeds
    ...    ${timeout}
    ...    ${poll_interval}
    ...    Element Attribute Value Should Be    xpath=//div[@role="progressbar"]    aria-valuenow    100
    Sleep    0.3s

Wait Until Progress Bar Reaches 100 V2_OLD
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.2s
    Log    Waiting for the progress bar to be dissapeared...
    ${progress_bar_title_xpath}=    Set Variable    xpath=//div[contains(@class, 'titulo_progress modal-title h4') and normalize-space(text())='Operation in progress...']
    Wait Until Element Is Not Visible    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario

Wait Until Progress Bar Reaches 100 V2
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.2s
    Log    Waiting for the progress bar to be dissapeared...
    ${progress_bar_title_xpath}=    Set Variable    xpath=//div[contains(@class, "p-progressbar-label")]
    # Wait Until Element Is Not Visible    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario
    Wait Until Page Does Not Contain    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario

#************************************************************************************************************************
#"Popup login" method Scripts 


Wait Title
    [Arguments]    ${TerminalTitle}    
    Wait Until Element Contains    ${TPU_WelcomeTitle_Type}    ${TerminalTitle}    120s

Wait Section Title
    [Arguments]    ${SectionTitle}    
    ${normalized_title}=    Evaluate    "${SectionTitle}".lower()
    Element Should Be Visible    xpath=//h2[translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${normalized_title}"]

Enter Password Credentials
    Wait Until Element Is Visible    id=ModGetPassword    timeout=10s
    ${password_input_locator}=    Set Variable    xpath=//div[@id='DvUPassInput']//input[@id='PassInput' and @type='password' and @name='PassInput']
    Wait Until Element Is Visible    ${password_input_locator}    timeout=5s
    Input Text    ${password_input_locator}    ${INTERNAL_PASS}
    # Click Accept Button
    ${Accept_xpath}=    Set Variable    xpath=//div[@class='dvModGetPasswordCtrl']//input[@id='passBtnOK' and @type='button' and @value='Accept']
    Click Element    ${Accept_xpath}
#************************************************************************************************************************
#************************************************************************************************************************

#BASIC CONFIGURATION TESTS


# ******************************************************************************************************************************

Get Command
    [Arguments]    ${name}    ${var_index}
    ${command}    Set Variable    //input[@name='${name}' and @var_index='${var_index}']
    Return From Keyword    ${command}

Checkbox Selection
    [Arguments]    ${checkbox}    ${value}
    #Checkbox = 0: Teleprotection disabled at start-up; Checkbox = 1: Teleprotection enabled at start-up
    ${checkbox}    Set Variable    //input[@name='dtproCfgEnedisDisabledAtStartUp']
    Wait Until Element Is Visible    ${checkbox}    timeout=5s    
    Run Keyword If    '${value}' == '1'    Select Checkbox    ${checkbox}
    Run Keyword If    '${value}' == '0'    Unselect Checkbox    ${checkbox}
    Sleep    0.1s
# <input type="checkbox" name="dtpuMgmtTpuIoActivationMask">
Convert Module Text to Number
    [Arguments]    ${module_name}
    #Convert the module name to the corresponding number. We will use the list of modules to do it.
    IF    "${module_name}" == "IBTU"
        Return From Keyword    ${IBTU}
    ELSE IF    "${module_name}" == "IDTU"
        Return From Keyword    ${IDTU}
    ELSE IF    "${module_name}" == "IETU"
        Return From Keyword    ${IETU}
    ELSE IF    "${module_name}" == "IOTU"
        Return From Keyword    ${IOTU}
    ELSE IF    "${module_name}" == "ICTU"
        Return From Keyword    ${ICTU}
    ELSE IF    "${module_name}" == "IPTU"
        Return From Keyword    ${IPTU}
    ELSE IF    "${module_name}" == "IPTU.10"
        Return From Keyword    ${IPTU.10}
    ELSE IF    "${module_name}" == "IRTU"
        Return From Keyword    ${IRTU}
    ELSE IF    "${module_name}" == "DSTU"
        Return From Keyword    ${DSTU}
    ELSE IF    "${module_name}" == "MCTU"
        Return From Keyword    ${MCTU}
    ELSE IF    "${module_name}" == "IOCT"
        Return From Keyword    ${IOCT}
    ELSE IF    "${module_name}" == "IPIT"
        Return From Keyword    ${IPIT}
    ELSE IF    "${module_name}" == "IEPT"
        Return From Keyword    ${IEPT}
    ELSE IF    "${module_name}" == "IOCS"
        Return From Keyword    ${IOCS}
    ELSE IF    "${module_name}" == "ICPT"
        Return From Keyword    ${ICPT}
    ELSE
        Return From Keyword    None
    END  


#************************************************************************************************************************
#Display Time Zone Configuration


# ******************************************************************************************************************************
# ******************************************************************************************************************************

#COMMAND ASSIGNMENTS KEYWORDS
Get Text If Locator Exists
    [Arguments]    ${locator}    ${default_value}='N/A'
    ${status}=    Run Keyword And Return Status    Page Should Contain Element    ${locator}
    # ${status}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${locator}    timeout=1s # Pequeño timeout

    IF    ${status}
        ${text}=    Get Text    ${locator}
        Return From Keyword    ${text}
    ELSE
        Log    Element with locator '${locator}' not found. Returning default value '${default_value}'.    WARN
        Return From Keyword    ${default_value}
    END
 
 Get Text If Element Exists
    [Arguments]    ${element}    ${default_value}='N/A'
    ${status}=    Run Keyword And Return Status    Element Should Be Visible    ${element}

    IF    ${status}
        ${text}=    Get Text    ${element}
        Return From Keyword    ${text}
    ELSE
        Log    Element with locator '${element}' not found. Returning default value '${default_value}'.    WARN
        Return From Keyword    ${default_value}
    END

Assign input to command V2
    [Arguments]    ${input}    ${command}
    #xpath=//div[contains(text(), "${input}")]/ancestor::tr//following::input[contains(@type, 'checkbox')][${command}]
    Scroll Element Into View Softly    xpath=//div[contains(text(), "Inp ${input}-")]/ancestor::tr/descendant::input[contains(@type, 'checkbox')][${command}]
    # Wait Until Element Is Visible    xpath=//div[contains(text(), "Inp ${input}-")]/ancestor::tr//descendant::input[contains(@type, 'checkbox')][${command}]    timeout=5s
    Select Checkbox    xpath=//div[contains(text(), "Inp ${input}-")]/ancestor-or-self::tr//following::input[contains(@type, 'checkbox')][${command}]
    # Sleep    0.1s

Unassign input to command V2
    [Arguments]    ${input}    ${command}
    Scroll Element Into View Softly    xpath=//div[contains(text(), "Inp ${input}-")]/ancestor::tr/descendant::input[contains(@type, 'checkbox')][${command}]
    # Wait Until Element Is Visible    xpath=//div[contains(text(), "Inp ${input}-")]/ancestor::tr//descendant::input[contains(@type, 'checkbox')][${command}]    timeout=5s
    Unselect Checkbox    xpath=//div[contains(text(), "Inp ${input}-")]/ancestor-or-self::tr//following::input[contains(@type, 'checkbox')][${command}]
    # Sleep    0.1s

Assign output to command V2
    [Arguments]    ${output}    ${command}
    Scroll Element Into View Softly    xpath=//div[contains(text(), "Out ${output}-")]/ancestor-or-self::tr//descendant::input[contains(@type, 'checkbox')][${command}]
    # Wait Until Element Is Visible    xpath=//div[contains(text(), "Out ${output}-")]/ancestor-or-self::tr//descendant::input[contains(@type, 'checkbox')][${command}]   timeout=5s
    Select Checkbox    xpath=//div[contains(text(), "Out ${output}-")]/ancestor-or-self::tr//following::input[contains(@type, 'checkbox')][${command}]
    # Sleep    0.1s

Unassign output to command V2
    [Arguments]    ${output}    ${command}
    Scroll Element Into View Softly    xpath=//div[contains(text(), "Out ${output}-")]/ancestor-or-self::tr/descendant::input[contains(@type, 'checkbox')][${command}]
    # Wait Until Element Is Visible    xpath=//div[contains(text(), "Out ${output}-")]/ancestor-or-self::tr//descendant::input[contains(@type, 'checkbox')][${command}]    timeout=5s
    Unselect Checkbox    xpath=//div[contains(text(), "Out ${output}-")]/ancestor-or-self::tr//following::input[contains(@type, 'checkbox')][${command}]
    # Sleep    0.1s

Validate Input Output In Range
    [Arguments]    ${input_output}    ${num_input_output}
    # Validate Input In Range    ${num_input}    ${min}    ${max}
    ${min}    Set Variable    1
    ${input_count}    ${output_count}=    Get Displayed Input Output Counts

    IF    ${input_output} == "input"
        ${max}    Set Variable    ${input_count}
    ELSE IF    ${input_output} == "output"
        ${max}    Set Variable    ${output_count}
    ELSE
        Log    input_output not recognized. Please select input or output.
        ${max}    Set Variable    0
    END

    ${is_number_0}    Evaluate    "${num_input_output}".isdigit()
    Run Keyword If    not ${is_number_0}    Fail    No es un mínimo válido
    ${is_in_range}    Evaluate    (${min} <= ${num_input_output} <= ${max}) and (${is_number_0} == True)

    Return From Keyword    ${is_in_range}

Get Displayed Input Output Counts
    [Documentation]    Counts the visible Input and Output configuration rows on the page.
    # Count the Input labels (td starting with 'Inp ')
    ${input_count}=    SeleniumLibrary.Get Element Count    xpath=//td[starts-with(normalize-space(.), 'Inp ')]
    # Count the Output labels (td starting with 'Out ')
    ${output_count}=   SeleniumLibrary.Get Element Count    xpath=//td[starts-with(normalize-space(.), 'Out ')]

    # Log To Console    \nNumber of configurable Inputs displayed: ${input_count}
    # Log To Console    Number of configurable Outputs displayed: ${output_count}\n
    Return From Keyword    ${input_count}    ${output_count}
# ******************************************************************************************************************************
# ******************************************************************************************************************************
#CHRONOLOGICAL REGISTER KEYWORDS



# ******************************************************************************************************************************
# ******************************************************************************************************************************
#ALIGNMENT KEYWORDS
#INPUT ACTIVATION


Input Activation/desactivation
    [Arguments]    ${Activate_Desactivate}    ${duration}=0    ${num_input_list}=[]
    [Documentation]    ${Activate_Desactivate}=1: Activate     ${Activate_Desactivate}=0: Desactivate inputs. Available duration values: 0 (Permanently), 5(s), 10(s), 30(s), 60(s), 600(s).
    ${current_state}    Current Activation_Desactivaton State

    # Validate Activate_Desactivate

    IF    ${current_state} == 0 and ${Activate_Desactivate} == 0
        Fail    Inputs are already desactivated!

    ELSE IF    ${current_state} == 0 and ${Activate_Desactivate}
        Restart Inputs Activation
        Input Activation Duration   ${duration}
        FOR    ${num_input}    IN    @{num_input_list}
            Input Checkbox Selection    ${num_input}    1
        END
        Program    sInputAct_ON
        Enter Password Credentials
        Wait Until Progress Bar Reaches 100 V2

    ELSE IF    ${current_state} and ${Activate_Desactivate} == 0
        Program    sInputAct_OFF
        Wait Until Progress Bar Reaches 100 V2

    ELSE IF    ${current_state} and ${Activate_Desactivate}
        Fail    Inputs are already activated!
    ELSE IF    ${current_state} == 0 and ${Activate_Desactivate} and ${num_input_list} == []

        Fail    Invalid or missing Arguments!
    ELSE
        Fail    Error in "current_state" and "Activate_Desactivate" variables evaluation
    END

Current Activation_Desactivaton State
    [Documentation]    Return ${current_state}=1 if there are inputs active. Return ${current_state}=0 if there are NOT inputs activate.
    Sleep    2s
    ${current_state_xpath}=    Set Variable    xpath=//div[@class='infoDatInpLab_content' and text()='Deactivate']
    # Wait Until Element Is Visible    ${current_state_xpath}    timeout=5s    
    ${current_state}=    Run Keyword And Return Status    Element Should Be Visible    ${current_state_xpath}
    Log To Console    El estado detectado es: ${current_state}
    [Return]    ${current_state}

Restart Inputs Activation
    # First we must count the max number of inputs
    ${rows_locator}=    Set Variable    xpath=//tr[@class="numCols_2 maxCols_3 numMustShow_3"]
    ${row_elements}=    Get WebElements    ${rows_locator}
    ${row_count}=    Get Length    ${row_elements}
    ${row_count}=    Evaluate    ${row_count} + 1
    FOR    ${num_inp}    IN RANGE    1    ${row_count}
        Input Checkbox Selection    ${num_inp}    0
    END

Input Checkbox Selection
    [Arguments]    ${num_input}    ${value}
    ${checkbox}=    Set Variable    xpath=//tr[contains(@class, "numCols_2 maxCols_3 numMustShow_3")][${num_input}]//input[@type='checkbox']
    Scroll Element Into View    ${checkbox}   
    Wait Until Element Is Visible    ${checkbox}    timeout=5s
    Run Keyword If    '${value}' == '1'    Select Checkbox    ${checkbox}
    Run Keyword If    '${value}' == '0'    Unselect Checkbox    ${checkbox}


Input Activation Duration
    [Arguments]    ${Duration}
    Validate Input Duration Value    ${Duration}
    
    ${locator}=    Set Variable    xpath=//select[@var_name='dtpuMgmtTpuIoActivationTime'][@var_index='0'] 
    Select From List By Value    ${locator}    ${Duration}



Validate Input Duration Value
    [Arguments]    ${Duration}
    [Documentation]    Only the following value numbers are available: 5(s), 10(s), 30(s), 60(s), 600(s) and 0 (Permanently)
    ${allowed_values}=    Evaluate    ['0', '5', '10', '30', '60', '600']

    # Convert the input duration to a string to ensure consistent comparison
    ${duration_as_string}=    Convert To String    ${Duration}

    # Check if the provided duration is in the list of allowed values
    ${duration_match}    Evaluate    any('${duration_as_string}' == word for word in @{allowed_values})
    IF    ${duration_match}
        Log    Duration '${duration_as_string}' is valid.
    ELSE
        Fail    Invalid duration: '${duration_as_string}'. Allowed numeric values are: 0 (Permanently), 5(s), 10(s), 30(s), 60(s), 600(s).
    END


# ******************************************************************************************************************************
Configure and Program Loop
    [Arguments]    ${Activate_Desactivate}    ${Teleprotection_Number}    ${Type}    ${Duration}
    [Documentation]    ${Activate_Desactivate}=1: Activate     ${Activate_Desactivate}=0: Desactivate inputs. Available duration values: 0 (Permanently), 10(s), 30(s), 60(s), 600(s). Available types: 0: NONE, 1: INTERNAL, 2: LINE
     # We ensure the number passed does not exceed 2 (maximum teleprotection modules we can install).
    ${current_state}    Current Loop Activation_Desactivaton State    ${Teleprotection_Number}
     
    IF    ${current_state} == 0 and ${Activate_Desactivate} == 0
        Fail    Loop is already desactivated!

    ELSE IF    ${current_state} == 0 and ${Activate_Desactivate}
        Assign Loop    ${Teleprotection_Number}    ${Type}    ${Duration}
        Program Loop    ${Activate_Desactivate}    ${Teleprotection_Number}
        Wait Until Progress Bar Reaches 100 V2

    ELSE IF    ${current_state} and ${Activate_Desactivate} == 0
        Program Loop    ${Activate_Desactivate}    ${Teleprotection_Number}
        Wait Until Progress Bar Reaches 100 V2

    ELSE IF    ${current_state} and ${Activate_Desactivate}
        Fail    Loop is already activated!

    ELSE
        Fail    Error in "current_state" and "Activate_Desactivate" variables evaluation
    END


Current Loop Activation_Desactivaton State
    [Arguments]    ${Teleprotection_Number}
    [Documentation]    Return ${current_state}=1 if there is an active loop in the teleprotecion passed as an arguent. Return ${current_state}=0 if there is no activate loop.
    Sleep    3s
    ${current_state_xpath_activate}=    Set Variable    xpath=//td[@class='tGrpLab' and text()='TELEPROTECTION -${Teleprotection_Number}-'][1]/parent::tr/preceding-sibling::tr[1]//td[@class='tGrpLab' and text()='Deactivate loop']

    # Wait Until Element Is Visible    ${current_state_xpath}    timeout=5s    
        # Wait Until Element Is Visible    ${current_state_xpath}    timeout=5s    //Doesn't work because there's a lapse of time where the loop state is not updated, appearing as it isn't activated.
    # That's the reason we use the first sleep and not the Wait Until Element Is Visible.
    ${current_state_activate}=    Run Keyword And Return Status    Element Should Be Visible    ${current_state_xpath_activate}


    IF    ${current_state_activate} == 1
        # If the loop is active, we will return 1
        ${current_state}=    Set Variable    1
    ELSE
        # If the loop is not active, we will return 0
        ${current_state}=    Set Variable    0

    END
    Log To Console    Loop state in Teleprotection ${Teleprotection_Number} : ${current_state}
    Return From Keyword    ${current_state}


Assign Loop
    [Arguments]    ${Teleprotection_Number}    ${Type}    ${Duration}
    Validate Number In Range    ${Teleprotection_Number}    1    2

    Validate Loop Type    ${Type}

    Validate Loop Duration Value    ${Duration}

    # Locate the Teleprotection and validate its existence
    ${Teleprotection_xpath}=    Set Variable    xpath=//td[@class='tGrpLab' and text()='TELEPROTECTION -${Teleprotection_Number}-'][1]

    ${status}=    Run Keyword And Return Status    Page Should Contain Element    ${Teleprotection_xpath}
    Run Keyword If    '${status}' == '1'    Fail    Teleprotection module ${Teleprotection_Number} not found.

    # Teleprotection name
    ${Teleprotection_name_path}=    Set Variable    ${Teleprotection_xpath}/following-sibling::td[1]//div[contains(@class,'infoUsrTxtPart')]
    ${Teleprotection_name}=    Get Text If Element Exists    ${Teleprotection_name_path}    default_value=Teleprotection ${Teleprotection_Number}
    Log To Console    Teleprotection Name: ${Teleprotection_name}

    # Type: 0: NONE, 1: INTERNAL, 2: LINE
    ${Loop_Type_Value}    Convert Loop Type to Number    ${Type}
    ${Type_xpath}=    Set Variable    xpath=//td[@class='tGrpLab' and text()='TELEPROTECTION -${Teleprotection_Number}-'][1]/following-sibling::td[2]//select[@var_name='dtproMgmtLoopType']
    Select From List By Value    ${Type_xpath}    ${Loop_Type_Value}
    # Durations: 10(s), 30(s), 60(s), 600(s) and 0 (Permanently)
    ${Duration_xpath}=    Set Variable    xpath=//td[@class='tGrpLab' and text()='TELEPROTECTION -${Teleprotection_Number}-'][1]/following-sibling::td[3]//select[@var_name='dtproMgmtLoopTime']
    Select From List By Value    ${Duration_xpath}    ${Duration}

Program Loop
    [Arguments]    ${Activate_Desactivate}    ${Teleprotection_Number}
    IF  '${Teleprotection_Number}' == '1' and ${Activate_Desactivate} == 1
        ${button_name}=    Set Variable    sLoopON_Ch1
    
    ELSE IF  '${Teleprotection_Number}' == '2' and ${Activate_Desactivate} == 1
        ${button_name}=    Set Variable    sLoopON_Ch2
    
    ELSE IF  '${Teleprotection_Number}' == '1' and ${Activate_Desactivate} == 0
        ${button_name}=    Set Variable    sLoopOFF_Ch1
    
    ELSE IF  '${Teleprotection_Number}' == '2' and ${Activate_Desactivate} == 0
        ${button_name}=    Set Variable    sLoopOFF_Ch2
    ELSE
        ${button_name}=    Set Variable    None
    END
    Program    ${button_name}



Convert Loop Type to Number
    [Arguments]    ${Type}
    # Convert the loop type to the corresponding number. We will use the list of loop types to do it.
    IF    "${Type}" == "NONE"
        Return From Keyword    0
    ELSE IF    "${Type}" == "INTERNAL"
        Return From Keyword    1
    ELSE IF    "${Type}" == "LINE"
        Return From Keyword    2
    ELSE
        Return From Keyword    None
    END
Validate Loop Duration Value
    [Arguments]    ${Duration}
    [Documentation]    Only the following value numbers are available: 10(s), 30(s), 60(s), 600(s) and 0 (Permanently)
    ${allowed_values}=    Evaluate    ['0', '10', '30', '60', '600']

    # Convert the input duration to a string to ensure consistent comparison
    ${duration_as_string}=    Convert To String    ${Duration}

    # Check if the provided duration is in the list of allowed values
    ${duration_match}    Evaluate    any('${duration_as_string}' == word for word in @{allowed_values})
    IF    ${duration_match}
        Log    Duration '${duration_as_string}' is valid.
    ELSE
        Fail    Invalid duration: '${duration_as_string}'. Allowed numeric values are: 0 (Permanently), 10(s), 30(s), 60(s), 600(s).
    END

Validate Loop Type
    [Arguments]    ${Type}
    [Documentation]    Only the following value types are available: NONE, INTERNAL and LINE
    ${allowed_values}=    Evaluate    ['NONE', 'INTERNAL', 'LINE']

    # Convert the input duration to a string to ensure consistent comparison
    ${type_as_string}=    Convert To String    ${Type}

    # Check if the provided duration is in the list of allowed values
    ${duration_match}    Evaluate    any('${type_as_string}' == word for word in @{allowed_values})
    IF    ${duration_match}
        Log    Duration '${type_as_string}' is valid.
    ELSE
        Fail    Invalid type: '${type_as_string}'. Allowed type values are: 'NONE', 'INTERNAL', 'LINE'.
    END

# ******************************************************************************************************************************
# BLOCKING SECTION
Configure and Program Blocking
    [Arguments]    ${Activate_Desactivate}    ${Teleprotection_Number}    ${Duration}
    [Documentation]    ${Activate_Desactivate}=1: Activate     ${Activate_Desactivate}=0: Desactivate inputs. Available duration values: 0 (Permanently), 10(s), 30(s), 60(s), 600(s).
     # We ensure the number passed does not exceed 2 (maximum teleprotection modules we can install).
    ${current_state}    Current Blocking Activation_Desactivaton State    ${Teleprotection_Number}
     
    IF    ${current_state} == 0 and ${Activate_Desactivate} == 0
        Fail    Blocking is already deactivated!

    ELSE IF    ${current_state} == 0 and ${Activate_Desactivate}
        Assign Blocking    ${Teleprotection_Number}    ${Duration}
        Program Blocking    ${Activate_Desactivate}    ${Teleprotection_Number}
        Wait Until Progress Bar Reaches 100 V2

    ELSE IF    ${current_state} and ${Activate_Desactivate} == 0
        Program Blocking    ${Activate_Desactivate}    ${Teleprotection_Number}
        Wait Until Progress Bar Reaches 100 V2

    ELSE IF    ${current_state} and ${Activate_Desactivate}
        Fail    Blocking is already activated!

    ELSE
        Fail    Error in "current_state" and "Activate_Desactivate" variables evaluation
    END


Current Blocking Activation_Desactivaton State
    [Arguments]    ${Teleprotection_Number}
    [Documentation]    Return ${current_state}=1 if there is an active blocking in the teleprotecion passed as an arguent. Return ${current_state}=0 if there is no activate blocking.
    Sleep    3s
    ${current_state_xpath_activate}=    Set Variable    xpath=//td[@class='tGrpLab' and text()='TELEPROTECTION -${Teleprotection_Number}-']/parent::tr/preceding-sibling::tr[1]//td[@class='tGrpLab' and text()='Program blocking']


    # Wait Until Element Is Visible    ${current_state_xpath}    timeout=5s    //Doesn't work because there's a lapse of time where the blocking state is not updated, appearing as it isn't activated.
    # That's the reason we use the first sleep and not the Wait Until Element Is Visible.
    ${current_state_activate}=    Run Keyword And Return Status    Element Should Be Visible    ${current_state_xpath_activate}


    IF    ${current_state_activate} == 1
        # If the blocking isn't active, we will return 0
        ${current_state}=    Set Variable    0
    ELSE
        # If the blocking is active, we will return 1
        ${current_state}=    Set Variable    1

    END
    Log To Console    Blocking state in Teleprotection ${Teleprotection_Number} : ${current_state}
    Return From Keyword    ${current_state}


Assign Blocking
    [Arguments]    ${Teleprotection_Number}    ${Duration}
    Validate Number In Range    ${Teleprotection_Number}    1    2

    Validate Blocking Duration Value    ${Duration}

    # Locate the Teleprotection and validate its existence
    ${Teleprotection_xpath}=    Set Variable    xpath=//td[@class='tGrpLab' and text()='TELEPROTECTION -${Teleprotection_Number}-']

    ${status}=    Run Keyword And Return Status    Page Should Contain Element    ${Teleprotection_xpath}
    Run Keyword If    '${status}' == '1'    Fail    Teleprotection module ${Teleprotection_Number} not found.

    # Durations: 10(s), 30(s), 60(s), 600(s) and 0 (Permanently)
    ${Duration_xpath}=    Set Variable    xpath=//td[@class='tGrpLab' and text()='TELEPROTECTION -${Teleprotection_Number}-']/following-sibling::td[1]//select[@var_name='dtproMgmtLockTime']
    Select From List By Value    ${Duration_xpath}    ${Duration}

Program Blocking
    [Arguments]    ${Activate_Deactivate}    ${Teleprotection_Number}
    IF  '${Teleprotection_Number}' == '1' and ${Activate_Deactivate} == 1
        ${button_name}=    Set Variable    sBlockON_Ch1
    
    ELSE IF  '${Teleprotection_Number}' == '2' and ${Activate_Deactivate} == 1
        ${button_name}=    Set Variable    sBlockON_Ch2
    
    ELSE IF  '${Teleprotection_Number}' == '1' and ${Activate_Deactivate} == 0
        ${button_name}=    Set Variable    sBlockOFF_Ch1
    
    ELSE IF  '${Teleprotection_Number}' == '2' and ${Activate_Deactivate} == 0
        ${button_name}=    Set Variable    sBlockOFF_Ch2
    ELSE
        ${button_name}=    Set Variable    None
    END
    Program    ${button_name}

Validate Blocking Duration Value
    [Arguments]    ${Duration}
    [Documentation]    Only the following value numbers are available: 10(s), 30(s), 60(s), 600(s) and 0 (Permanently)
    ${allowed_values}=    Evaluate    ['0', '10', '30', '60', '600']

    # Convert the input duration to a string to ensure consistent comparison
    ${duration_as_string}=    Convert To String    ${Duration}

    # Check if the provided duration is in the list of allowed values
    ${duration_match}    Evaluate    any('${duration_as_string}' == word for word in @{allowed_values})
    IF    ${duration_match}
        Log    Duration '${duration_as_string}' is valid.
    ELSE
        Fail    Invalid duration: '${duration_as_string}'. Allowed numeric values are: 0 (Permanently), 10(s), 30(s), 60(s), 600(s).
    END


# ******************************************************************************************************************************
# ******************************************************************************************************************************

#GENERAL VALIDATIONS
Validate Number In Range
    [Arguments]    ${number}    ${min}    ${max}
    ${is_number_0}    Evaluate    "${number}".isdigit()
    ${is_number_1}    Evaluate    "${min}".isdigit()
    ${is_number_2}    Evaluate    "${max}".isdigit()
    
    #We evaluate wether max & min are numbers or not. If they are not, we fail the test.

    Run Keyword If    not ${is_number_1}    Fail    No es un mínimo válido
    Run Keyword If    not ${is_number_2}    Fail    No es un máximo válido

    ${is_in_range}    Evaluate    (${min} <= ${number} <= ${max}) and (${is_number_0} == True)
    Return From Keyword    ${is_in_range}
    Should Be True    ${is_in_range}


