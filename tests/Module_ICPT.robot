*** Settings ***
Documentation                This is a basic test
Library    SeleniumLibrary
Library    String
Library    Collections
Library    OperatingSystem    #for file operations
Library    BuiltIn
Library    XML
Library    DateTime
Library    Screenshot
Library    BrowserManager.py

Resource    Keep_Alive.robot

# Library    trapReceiver_Robot_1
Suite Setup    Run Keyword    Conectar A Navegador Existente    ${SESSION_ALIAS}    ${SESSION_FILE_PATH}
Test Setup        Check And Handle Session Expired Popup
Suite Teardown
# Resource    IOCS_config.robot

*** Variables ***
# SESSION VARIABLES
${SESSION_ALIAS}
${SESSION_FILE_PATH}
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
# ${options}=  Create List  --ignore-certificate-errors  --disable-web-security  --allow-running-insecure-content
${commands}    Input/Output Alias

#************************************************************************************************************************
#BASIC CONFIGURATION TESTS
${SELECT_BUTTON}    xpath=//button[contains(text(),'Select')]


*** Test Cases ***
Check if Telep available and Open Section
    Setup Folder Section
    ${Telep_name_to_config}=    Set Variable    ICPT
    ${available_modules}=    Detect Available Modules
    ${available_modules_names}=    Set Variable    ${available_modules}[0]    # It's a list!
    ${available_modules_commands}=    Set Variable    ${available_modules}[1]    # It's a list!

    ${Telep_number_to_config}    Check if Telep available and Return TP ID    ${Telep_name_to_config}    ${available_modules_names}
    Set Suite Variable    ${available_modules_commands}
    Set Suite Variable    ${Telep_number_to_config}
Open Line Interface Section
    Setup Folder Section
    Open Line Interface Section Associated To Teleprotection    ${Telep_number_to_config}
    Sleep    1s

#*************************************************************************************************************************
# PRUEBAS


# Reception Section
Reception Operation Mode Selection
    Assign Reception Operation Mode    1    #Telesignalling
    Sleep    2s
#*************************************************************************************************************************
# Transmitter Section
Constant Time Interval Type Between Packets Selection
    Constant Time Interval Type Between Packets     1
    Sleep    2s

Variable Time Interval Type Between Packets Selection
    Variable Time Interval Type Between Packets    1    1
    Sleep    2s
#*************************************************************************************************************************
# Line Section
Config IP Line Interface_1
    Config IP Line Interface    Redundance_Mode=1
    Sleep    2s
Config Ethernet Line Interface_1
    Config Ethernet Line Interface    Redundance_Mode=1
    Sleep    2s
Automatic Link Test Periodicity Assignment
    Automatic Link Test Periodicity    24

# Alarms Section
Command Output Blocking In Case of INV_CMD_reception_Checkbox
    Command Output Blocking In Case of INV_CMD_reception    0
    Sleep    2s
Command Output Blocking In Case of Transmission time alarm_Checkbox
    Command Output Blocking In Case of Transmission time alarm    0
    Sleep    2s
ACTIVATION threshold for transmission time alarm_Assignment
    ACTIVATION threshold for transmission time alarm    11
    Sleep    2s

DEACTIVATION threshold for transmission time alarm_Assignment
    DEACTIVATION threshold for transmission time alarm    10
ACTIVATION threshold for MTD alarm_Assignment
    ACTIVATION threshold for MTD alarm    11
DEACTIVATION threshold for MTD alarm_Assignment
    DEACTIVATION threshold for MTD alarm    10

ACTIVATION threshold for FDV alarm_Assignment
    ACTIVATION threshold for FDV alarm    0.60
DEACTIVATION threshold for FDV alarm_Assignment
    DEACTIVATION threshold for FDV alarm    0.50

Command output blocking in case of FLR alarm_Checkbox
    Command output blocking in case of FLR alarm    0
    Sleep    2s

ACTIVATION threshold for FLR alarm_Assignment
    ACTIVATION threshold for FLR alarm    55
    Sleep    2s
DEACTIVATION threshold for FLR alarm_Assignment
    DEACTIVATION threshold for FLR alarm    50

INVALID DEACTIVATION threshold for FLR alarm_Assignment
    DEACTIVATION threshold for FLR alarm    4

#Auth Key Section
Activate and Config INVALID Authentication Key
    Authentication key Assignment    1    abcd1234    abcd1234
Activate and Config VALID Authentication Key
    Authentication key Assignment    1    Abcd.1234    Abcd.1234
Deactivate Authentication Key
    Authentication key Assignment    0    Abcd.1234    Abcd.1234
    Sleep    2s
Programm
    Program Old    sCOM
    Check If Alert Appears and Handle It
    Sleep    2s

#*************************************************************************************************************************

*** Keywords ***
Setup Folder Section
    Click Open Folder    /
    Click Open Folder    EQUIPMENT
    Open Section    Basic Configuration
    Wait Section Title    BASIC CONFIGURATION
    Sleep    5s


Get Full Matching Element
    [Arguments]    ${substring_to_find}    ${list_to_search}
    ${full_element}=    Evaluate    next((word for word in @{list_to_search} if '${substring_to_find}' in word), None)
    Return From Keyword    ${full_element}

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
    # Check if the folder is already open
    ${is_open}    Run Keyword And Return Status    Page Should Contain Element    xpath=//span[contains(text(), "${folderName}")]/ancestor-or-self::div[contains(@tabindex, '0') and contains(@aria-expanded, 'true') and not(contains(@style, 'display: none;'))]
    IF    ${is_open}
    # If the folder is already open, log a message and do nothing. 
        Log To Console    Folder "${folderName}" is already open.
    ELSE
        Scroll Element Into View Softly    xpath=//span[contains(text(), "${folderName}")]/ancestor-or-self::div[contains(@tabindex, '0')]//button[contains(@class, 'p-tree-toggler')]
        ${button}  Get WebElement  xpath=//span[contains(text(), "${folderName}")]/ancestor-or-self::div[contains(@tabindex, '0')]//button[contains(@class, 'p-tree-toggler')]
        Click Element  ${button}
        Sleep    0.3s
    END
Open Section
    [Arguments]    ${section}
    ${locator}    Set Variable    xpath=//li[contains(@class,'p-treenode p-treenode-leaf') and not(contains(@style, 'display: none;'))]//span[@class='p-treenode-label' and translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${section.lower()}"]
    Scroll Element Into View Softly    ${locator}
 
    Wait Until Element Is Visible    ${locator}    timeout=10s
    Click Element    ${locator}
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
    # Sleep    0.5s
    Wait Until Page Contains Element    ${xpath_button}
    Scroll Element Into View Softly    ${xpath_button}
    Wait Until Element Is Visible    ${xpath_button}    timeout=5s
    Click Element    ${xpath_button}
    Sleep    1s
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
Program Old
    [Arguments]    ${button_name}
    Button    ${button_name}    Program
    ${Handle_Alert_Detail}    Run Keyword And Return Status    Handle Alert    action=ACCEPT    timeout=0.3s
    # Log To Console    ${Handle_Alert_Detail}
    Wait Until Progress Bar Reaches 100

Wait Until Progress Bar Reaches 100
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.2s
    Log    Waiting for the progress bar to reach 100%...
    Wait Until Keyword Succeeds
    ...    ${timeout}
    ...    ${poll_interval}
    ...    Element Attribute Value Should Be    xpath=//div[@role="progressbar"]    aria-valuenow    100
    Sleep    2s

Wait Until Progress Bar Reaches 100 V2_OLD
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.2s
    Log    Waiting for the progress bar to be dissapeared...
    ${progress_bar_title_xpath}=    Set Variable    xpath=//div[contains(@class, 'titulo_progress modal-title h4') and normalize-space(text())='Operation in progress...']
    Wait Until Element Is Not Visible    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario

Wait Until Progress Bar Reaches 100 V2
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.3s
    Log    Waiting for the progress bar to be dissapeared...
    ${progress_bar_title_xpath}=    Set Variable    xpath=//div[contains(@class, "p-progressbar-label")]
    # Wait Until Element Is Not Visible    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario
    Wait Until Page Does Not Contain    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario

Input Text By Pressing Keys
    [Arguments]    ${locator}    ${text}
    # This keyword inputs text by pressing keys, simulating a user typing.
        Clear Element Text    ${locator}
        Press Keys    ${locator}    BACKSPACE
        Press Keys    ${locator}    BACKSPACE
        Press Keys    ${locator}    BACKSPACE
        # Click Element    locator=${powerboosting_level_xpath}
        Press Keys    ${locator}    ${text}
        Press Keys   ${locator}    TAB
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


# ******************************************************************************************************************************
# ******************************************************************************************************************************

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
 
Get Attribute If Locator Exists
    [Arguments]    ${locator}    ${Attr_name}    ${default_value}='N/A'
    ${status}=    Run Keyword And Return Status    Page Should Contain Element    ${locator}
    # ${status}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${locator}    timeout=1s # Pequeño timeout

    IF    ${status}
        ${text}=    SeleniumLibrary.Get Element Attribute    ${locator}    ${Attr_name}
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

Check If an Error Popup Appeared & Skip It
    ${Error_popup_button_xpath}=    Set Variable    xpath=//button[contains(@class, 'p-toast-icon-close p-link')]
    ${Error_popup_error_xpath}=    Set Variable    xpath=//div[contains(@class, 'p-toast-message-error')]
    ${Error_popup_error_detail_xpath}=    Set Variable    xpath=//div[contains(@class, 'p-toast-detail')]
    ${error_appeared}    Run Keyword And Return Status    Wait Until Element Is Visible    ${Error_popup_error_xpath}    1s
    IF    ${error_appeared}
        ${Error_Detail}    Get Text     ${Error_popup_error_detail_xpath}
        Log To Console    ${Error_Detail}
        Click Element    ${Error_popup_button_xpath}
        Return From Keyword    ${Error_Detail}
        Sleep    0.5s
    END

Check If Alert Appears and Handle It
    ${alert_present}=    Run Keyword And Return Status    Alert Should Be Present    timeout=1s
    IF    ${alert_present}
        ${Handle_Alert_Detail}    Run Keyword And Return Status    Handle Alert    action=ACCEPT    timeout=1s
        Log To Console    ${Handle_Alert_Detail}
        Return From Keyword    ${alert_present}
        Sleep    0.5s
    END

Print Table In The Console
    [Arguments]    @{table_for_print}

    ${separator}=         Set Variable    ========================================================
    ${header}=            Format String    | {:<10} | {:<20} | {:<22} |    Tone    Command activated    Command transmitted

    Log To Console    ${separator}
    Log To Console    ${header}
    Log To Console    ${separator}

    FOR    ${row}    IN    @{table_for_print}
        ${line_to_log}=    Format String    | {:<10} | {:<20} | {:<22} |    ${row}[0]    ${row}[1]    ${row}[2]
        Log To Console    ${line_to_log}
    END
    Log To Console    ${separator}
# ******************************************************************************************************************************
# ******************************************************************************************************************************
# CONFIG MODULES KEYWORDS
Detect Available Modules
    [Documentation]    Detects the available teleprotection modules in the "Number of commands" table. Morover, it returns a list of the available modules' names and a list of the available modules' commands. This keyword only can be used in the "Basic Configuration" section. It returns 2 lists. The first one contains the names of the available modules, and the second one contains the number of commands for each module (Tx_Tp1_Comm, Tx_Tp2_Comm, Rx_Tp1_Comm, Rx_Tp2_Comm). 
    
    ${available_modules_names}=    Create List
    ${available_modules_commands}=    Create List

    #############################################################################################################################
    # Locate "Teleprotection modules" in the "Number of commands" table by its input name and var_index (TP1 or TP2).
    ${teleprotection_modules_xpath}=    Set Variable    //div[contains(text(), 'Teleprotection modules')]
    #  Get the Tp1 and Tp2 XPaths relative to the "Teleprotection modules" row.
    ${Tp1_xpath}=    Set Variable    xpath=${teleprotection_modules_xpath}//ancestor::tr//input[contains(@name, 'dclientComAssignView') and contains(@var_index, '0')]
    ${Tp2_xpath}=    Set Variable    xpath=${teleprotection_modules_xpath}//ancestor::tr//input[contains(@name, 'dclientComAssignView') and contains(@var_index, '1')]

    # Get the text of the Tp1 and Tp2 elements.
    ${Tp1_text}=    Get Attribute If Locator Exists    ${Tp1_xpath}    value
    ${Tp2_text}=    Get Attribute If Locator Exists    ${Tp2_xpath}    value

    # Add them to the list.
    Append To List    ${available_modules_names}    ${Tp1_text}
    Append To List    ${available_modules_names}    ${Tp2_text}
    # Log the available modules.
    Log To Console    \nAvailable modules detected: ${available_modules_names}\n

    #############################################################################################################################
    # Locate "Number of commands in transmission" in the "Number of commands" table.
    ${num_Tx_commands_xpath}=    Set Variable    //div[contains(text(), 'Number of commands in transmission')]
    #  Get the Tp1 and Tp2 XPaths relative to the "Number of commands in transmission" row.
    ${Tp1_tx_commands_xpath}=    Set Variable    xpath=${num_Tx_commands_xpath}//ancestor::tr//input[contains(@name, 'dtproCfgNumTransmitCommands') and contains(@var_index, '0')]
    ${Tp2_tx_commands_xpath}=    Set Variable    xpath=${num_Tx_commands_xpath}//ancestor::tr//input[contains(@name, 'dtproCfgNumTransmitCommands') and contains(@var_index, '1')]

    # Get the text of the Tp1 and Tp2 elements.
    ${Tp1_tx_commands_text}=    Get Attribute If Locator Exists    ${Tp1_tx_commands_xpath}    value
    ${Tp2_tx_commands_text}=    Get Attribute If Locator Exists    ${Tp2_tx_commands_xpath}    value


    # Locate "Number of commands in reception" in the "Number of commands" table.
    ${num_Rx_commands_xpath}=    Set Variable    //div[contains(text(), 'Number of commands in reception')]
    #  Get the Tp1 and Tp2 XPaths relative to the "Number of commands in reception" row.
    ${Tp1_rx_commands_xpath}=    Set Variable    xpath=${num_Rx_commands_xpath}//ancestor::tr//input[contains(@name, 'dtproCfgNumReceiveCommands') and contains(@var_index, '0')]
    ${Tp2_rx_commands_xpath}=    Set Variable    xpath=${num_Rx_commands_xpath}//ancestor::tr//input[contains(@name, 'dtproCfgNumReceiveCommands') and contains(@var_index, '1')]
    
    # Get the text of the Tp1 and Tp2 elements.
    ${Tp1_rx_commands_text}=    Get Attribute If Locator Exists    ${Tp1_rx_commands_xpath}    value
    ${Tp2_rx_commands_text}=    Get Attribute If Locator Exists    ${Tp2_rx_commands_xpath}    value

    # Add them to the list.
    Append To List    ${available_modules_commands}    ${Tp1_tx_commands_text}
    Append To List    ${available_modules_commands}    ${Tp2_tx_commands_text}
    Append To List    ${available_modules_commands}    ${Tp1_rx_commands_text}
    Append To List    ${available_modules_commands}    ${Tp2_rx_commands_text}
    # Log the available modules.
    Log To Console    \nAvailable modules commands: ${available_modules_commands}\n

    # Return the list of available modules.
    Return From Keyword    ${available_modules_names}    ${available_modules_commands}
    

Check if Telep available and Return TP ID
    [Arguments]    ${Telep_name_to_config}    ${available_TPs}
    [Documentation]    Checks if the specified teleprotection module is available in the list of available modules. If it is, it opens the corresponding section. Morover, it returns de TP ID associated to the module.
    ${index}=    Set Variable    ${-1}  # Initialize to -1 in case the module is not found
    ${telep-match}    Evaluate    any('${Telep_name_to_config}' in word for word in @{available_TPs})
    IF    ${telep-match}
        Log    Teleprotection module ${Telep_name_to_config} is available.
        ${Full_Tp_Name}    Get Full Matching Element    ${Telep_name_to_config}    ${available_TPs}
        Log To Console    Full Teleprotection module name: ${Full_Tp_Name}
        ${index}=    Evaluate    ${available_TPs}.index('${Full_Tp_Name}')
        ${Telep_number_to_config}=    Evaluate    ${index} + 1
        Log    Modulo indicado (${Telep_name_to_config}) pertenece a TP${Telep_number_to_config}
    ELSE
        Fail    Teleprotection module ${Telep_name_to_config} is not available in the detected modules: ${available_TPs}
    END
    Return From Keyword    ${Telep_number_to_config}

Open Line Interface Section Associated To Teleprotection
    [Arguments]    ${Telep_number_to_config}
    [Documentation]    Opens the Line Interface section associated to the specified teleprotection module.
    Click Open Folder    Line Interfaces
    Open Section    Teleprotection(${Telep_number_to_config}) 

Open INV_CMD Conditions Section Associated To Teleprotection
    [Arguments]    ${Telep_number_to_config}
    [Documentation]    Opens the INV_CMD Conditions section associated to the specified teleprotection module.
    Click Open Folder    Line Interfaces
    Open Section    INV_CMD Conditions TP${Telep_number_to_config}



# ************************************************************************************************************************
# ************************************************************************************************************************


#ICPT MODULE CONFIG
#Reception Section
Assign Reception Operation Mode
    [Documentation]    Assign to the Command Number passed as an argument the Reception Operation Mode Selected. ${Reception_Operation_Mode} = 0 : Normal. ${Reception_Operation_Mode} = 1 : Telesignalling
    [Arguments]    ${Reception_Operation_Mode}
    ${is_in_range}=    Validate Number In Range - int    ${Reception_Operation_Mode}    0    1
    Run Keyword If    not ${is_in_range}    Fail    Reception Operation Mode must be 0 or 1. Received: ${Reception_Operation_Mode}
    ${Mode_box_xpath}=    Set Variable    xpath=//select[@var_name='dtproCfgIcptBehavior']
    Select From List By Value    ${Mode_box_xpath}    ${Reception_Operation_Mode}

#*************************************************************************************************************************************************************

#Transmitter Section
Constant Time Interval Type Between Packets 
    [Arguments]    ${K}=1
    [Documentation]    Sets the Time Interval Constant K Between Packets in the Transmitter section. Message Interval: T = K * Tmin(msec) [Tmin = 1 msec] 
    ${Time_Interval_xpath}=    Set Variable    xpath=//select[@var_name='dtproCfgIcptTxMode']
    Wait Until Element Is Visible    ${Time_Interval_xpath}    timeout=5s
    Select From List By Value    ${Time_Interval_xpath}    0
    
    ${K_xpath}=    Set Variable    xpath=//input[@name='dtproCfgIcptTxInitialInterval']
    Input Text By Pressing Keys    ${K_xpath}    ${K}
    Check If an Error Popup Appeared & Skip It
Variable Time Interval Type Between Packets 
    [Arguments]    ${Ki}=1    ${Kt}=1
    [Documentation]    Sets the Time Interval Constant Ki & Kt Between Packets in the Transmitter section. Message interval in idle state: Ti = Ki * Tmin(msec) [Tmin = 1 msec]. Message interval during transition state: Tt = Kt * Tmin(msec) [Tmin = 1 msec]. Transition state lenght: 15ms. For Kt=0 progressive intervals are applied at the transitions (1, 2, 4, 8ms)
    ${Time_Interval_xpath}=    Set Variable    xpath=//select[@var_name='dtproCfgIcptTxMode']
    Wait Until Element Is Visible    ${Time_Interval_xpath}    timeout=5s
    Select From List By Value    ${Time_Interval_xpath}    1

    ${Ki_xpath}=    Set Variable    xpath=//input[@name='dtproCfgIcptTxInitialInterval']
    Input Text By Pressing Keys    ${Ki_xpath}    ${Ki}
    ${Kt_xpath}=    Set Variable    xpath=//input[@name='dtproCfgIcptTxMaxInterval']
    Input Text By Pressing Keys    ${Kt_xpath}    ${Kt}
    Check If an Error Popup Appeared & Skip It

# Line Section
Config IP Line Interface
    [Arguments]    ${IP_Address}=0.0.0.0    ${Mask}=255.255.0.0    ${Gateway_IP}=0.0.0.0    ${Redundance_Mode}=0    ${Supervision frame interval}=2000    ${Supervision frame last MAC byte}=0    ${Information_Transport_Mode}=1    ${Destination_IP_Adress}=0.0.0.0    ${Destination_UDP_Port}=0
    [Documentation]    Configures the IP Line Interface with the specified parameters. The parameters are:
    # IP Address: IP address of the interface.
    # Mask: Subnet mask for the interface.
    # Gateway IP: Gateway IP address for the interface.
    # Redundance_Mode: 0 = No redundancy, 1 = Redundant with PRP
    # Supervision frame interval: Interval in seconds for the supervision frame. From 0 to 30000ms
    # Supervision frame last MAC byte: Last MAC byte for the supervision frame. From 0 to 255.
    # Information Transport Mode: Fixed Type: UDP Socket over IP
    # Destination IP Address: IP address of the destination.
    # Destination UDP Port: UDP port of the destination.
    ${Line_Interface_xpath}=    Set Variable    xpath=//select[@var_name='dtproCfgIcptLineType']
    Wait Until Element Is Visible    ${Line_Interface_xpath}    timeout=5s
    Select From List By Value    ${Line_Interface_xpath}    0    #IP
    
    ${IP_Address_xpath}=    Set Variable    xpath=//input[@name='dclientIcptIpAddress']
    Input Text By Pressing Keys    ${IP_Address_xpath}    ${IP_Address}
    Check If an Error Popup Appeared & Skip It

    ${Mask_xpath}=    Set Variable    xpath=//input[@name='dclientIcptIpNetMask']
    Check If an Error Popup Appeared & Skip It

    ${Mask_xpath}=    Set Variable    xpath=//input[@name='dclientIcptIpNetMask']
    Input Text By Pressing Keys    ${Mask_xpath}    ${Mask}
    Check If an Error Popup Appeared & Skip It

    ${Gateway_IP_xpath}=    Set Variable    xpath=//input[@name='dclientIcptIpGateway']
    Input Text By Pressing Keys    ${Gateway_IP_xpath}    ${Gateway_IP}
    Check If an Error Popup Appeared & Skip It
    ${Redundance_Mode_xpath}=    Set Variable    xpath=//select[@var_name='dtpuCfgIcptRedundMode']
    ${is_in_range}    Validate Number In Range - int    ${Redundance_Mode}    0    1
    Run Keyword If    not ${is_in_range}    Fail    Redundance Mode must be 0 or 1. Received: ${Redundance_Mode}
    Select From List By Value    ${Redundance_Mode_xpath}    ${Redundance_Mode}
    IF    ${Redundance_Mode} == 1
        ${Supervision_frame_interval_xpath}=    Set Variable    xpath=//input[@name='dtpuCfgIcptPrp_supervinterv']
        Input Text By Pressing Keys    ${Supervision_frame_interval_xpath}    ${Supervision_frame_interval}
        Check If an Error Popup Appeared & Skip It
        ${Supervision_frame_last_MAC_byte_xpath}=    Set Variable    xpath=//input[@name='dtpuCfgIcptPrp_supervframemac']
        Input Text By Pressing Keys    ${Supervision_frame_last_MAC_byte_xpath}    ${Supervision_frame_last_MAC_byte}
        Check If an Error Popup Appeared & Skip It
    END
    ${Destination_IP_Adress_xpath}=    Set Variable    xpath=//input[@name='dclientIcptIpDestination']
    Input Text By Pressing Keys    ${Destination_IP_Adress_xpath}    ${Destination_IP_Adress}
    Check If an Error Popup Appeared & Skip It
    ${Destination_UDP_Port_xpath}=    Set Variable    xpath=//input[@name='dtproCfgIcptUdpPort']
    Input Text By Pressing Keys    ${Destination_UDP_Port_xpath}    ${Destination_UDP_Port}
    Check If an Error Popup Appeared & Skip It
    
Config Ethernet Line Interface
    [Arguments]    ${Redundance_Mode}=0    ${Supervision frame interval}=2000    ${Supervision frame last MAC byte}=0    ${VLAN}=0    ${Priority}=0    ${Destination_Adress_MAC}=00:00:00:00:00:00
    [Documentation]    Configures the Ethernet Line Interface with the specified parameters. The parameters are:
    # Redundance_Mode: 0 = No redundancy, 1 = Redundant with PRP
    # Supervision frame interval: Interval in seconds for the supervision frame. From 0 to 30000ms
    # Supervision frame last MAC byte: Last MAC byte for the supervision frame. From 0 to 255.
    # VLAN: VLAN ID for the Ethernet interface.
    # Priority: Priority level for the Ethernet interface.
    # Destination Address MAC: MAC address of the destination.
    ${Line_Interface_xpath}=    Set Variable    xpath=//select[@var_name='dtproCfgIcptLineType']
    Wait Until Element Is Visible    ${Line_Interface_xpath}    timeout=5s
    Select From List By Value    ${Line_Interface_xpath}    2    #Ethernet

    IF    ${Redundance_Mode} == 1
        ${Supervision_frame_interval_xpath}=    Set Variable    xpath=//input[@name='dtpuCfgIcptPrp_supervinterv']
        Input Text By Pressing Keys    ${Supervision_frame_interval_xpath}    ${Supervision_frame_interval}
        ${Supervision_frame_last_MAC_byte_xpath}=    Set Variable    xpath=//input[@name='dtpuCfgIcptPrp_supervframemac']
        Input Text By Pressing Keys    ${Supervision_frame_last_MAC_byte_xpath}    ${Supervision_frame_last_MAC_byte}
    END

    ${VLAN_xpath}=    Set Variable    xpath=//input[@name='dtproCfgIcptVlan']
    Input Text By Pressing Keys    ${VLAN_xpath}    ${VLAN}
    Check If an Error Popup Appeared & Skip It

    ${Priority_xpath}=    Set Variable    xpath=//input[@name='dtproCfgIcptPriority']
    Input Text By Pressing Keys    ${Priority_xpath}    ${Priority}
    Check If an Error Popup Appeared & Skip It

    ${Destination_Adress_MAC_xpath}=    Set Variable    xpath=//input[@name='dtproCfgIcptDestMacAddress']
    Input Text By Pressing Keys    ${Destination_Adress_MAC_xpath}    ${Destination_Adress_MAC}
    Check If an Error Popup Appeared & Skip It
Automatic Link Test Periodicity
    [Arguments]    ${Automatic_Link_Test_Periodicity}=0
    [Documentation]    Sets the Automatic Link Test Periodicity in the Line section. The value is in hours.
    ${is_in_range}=    Validate Number In Range - int    ${Automatic_Link_Test_Periodicity}    0    24
    Run Keyword If    not ${is_in_range}    Fail    Automatic Link Test Periodicity must be between 0 and 24 hours. Received: ${Automatic_Link_Test_Periodicity}

    ${Automatic_Link_Test_Periodicity_xpath}=    Set Variable    xpath=//input[@name='dtproTestMgmtAutomaticTestPeriodicityHours']
    Wait Until Element Is Visible    ${Automatic_Link_Test_Periodicity_xpath}    timeout=5s
    Input Text By Pressing Keys    ${Automatic_Link_Test_Periodicity_xpath}    ${Automatic_Link_Test_Periodicity}
    Check If an Error Popup Appeared & Skip It
    
# Alarms Section
Command Output Blocking In Case of INV_CMD_reception
    [Arguments]    ${Command_Output_Blocking_In_Case_of_INV_CMD_reception}=0
    [Documentation]    Sets the Command Output Blocking In Case of INV_CMD reception in the Alarms section. The value is 0 or 1.
    ${is_in_range}=    Validate Number In Range - int    ${Command_Output_Blocking_In_Case_of_INV_CMD_reception}    0    1
    Run Keyword If    not ${is_in_range}    Fail    Command Output Blocking In Case of INV_CMD reception must be 0 or 1. Received: ${Command_Output_Blocking_In_Case_of_INV_CMD_reception}

    ${Command_Output_Blocking_In_Case_of_INV_CMD_reception_xpath}=    Set Variable    xpath=//input[@name='dtproCfgInvCmdOutputBlocking']
    Wait Until Element Is Visible    ${Command_Output_Blocking_In_Case_of_INV_CMD_reception_xpath}    timeout=5s
    Run Keyword If    '${Command_Output_Blocking_In_Case_of_INV_CMD_reception}' == '1'    Select Checkbox    ${Command_Output_Blocking_In_Case_of_INV_CMD_reception_xpath}
    Run Keyword If    '${Command_Output_Blocking_In_Case_of_INV_CMD_reception}' == '0'    Unselect Checkbox    ${Command_Output_Blocking_In_Case_of_INV_CMD_reception_xpath}

Command Output Blocking In Case of Transmission time alarm
    [Arguments]    ${Command_Output_Blocking_In_Case_of_Transmission_time_alarm}=0
    [Documentation]    Sets the Command Output Blocking In Case of Transmission time alarm in the Alarms section. The value is 0 or 1.
    ${is_in_range}=    Validate Number In Range - int    ${Command_Output_Blocking_In_Case_of_Transmission_time_alarm}    0    1
    Run Keyword If    not ${is_in_range}    Fail    Command Output Blocking In Case of Transmission time alarm must be 0 or 1. Received: ${Command_Output_Blocking_In_Case_of_Transmission_time_alarm}

    ${Command_Output_Blocking_In_Case_of_Transmission_time_alarm_xpath}=    Set Variable    xpath=//input[@name='dtproCfgIcptMtdOutputBlocking']
    Wait Until Element Is Visible    ${Command_Output_Blocking_In_Case_of_Transmission_time_alarm_xpath}    timeout=5s
    Run Keyword If    '${Command_Output_Blocking_In_Case_of_Transmission_time_alarm}' == '1'    Select Checkbox    ${Command_Output_Blocking_In_Case_of_Transmission_time_alarm_xpath}
    Run Keyword If    '${Command_Output_Blocking_In_Case_of_Transmission_time_alarm}' == '0'    Unselect Checkbox    ${Command_Output_Blocking_In_Case_of_Transmission_time_alarm_xpath}

ACTIVATION threshold for transmission time alarm
    [Arguments]    ${ACTIVATION_threshold_for_transmission_time_alarm}=11
    [Documentation]    Sets the ACTIVATION threshold for transmission time alarm in the Alarms section. The value is between 5 and 50ms.
    ${is_in_range}=    Validate Number In Range - int    ${ACTIVATION_threshold_for_transmission_time_alarm}    5    50
    Run Keyword If    not ${is_in_range}    Fail    ACTIVATION threshold for transmission time alarm must be between 5 and 50ms. Received: ${ACTIVATION_threshold_for_transmission_time_alarm}

    ${ACTIVATION_threshold_for_transmission_time_alarm_xpath}=    Set Variable    xpath=//input[@name='dclientHighTxTransThreshold']
    Wait Until Element Is Visible    ${ACTIVATION_threshold_for_transmission_time_alarm_xpath}    timeout=5s
    Input Text By Pressing Keys    ${ACTIVATION_threshold_for_transmission_time_alarm_xpath}    ${ACTIVATION_threshold_for_transmission_time_alarm}
    Check If an Error Popup Appeared & Skip It

DEACTIVATION threshold for transmission time alarm
    [Arguments]    ${DEACTIVATION_threshold_for_transmission_time_alarm}=10
    [Documentation]    Sets the DEACTIVATION threshold for transmission time alarm in the Alarms section. The value is between 4 and 49ms.
    ${is_in_range}=    Validate Number In Range - int    ${DEACTIVATION_threshold_for_transmission_time_alarm}    4    49
    Run Keyword If    not ${is_in_range}    Fail    DEACTIVATION threshold for transmission time alarm must be between 4 and 49ms. Received: ${DEACTIVATION_threshold_for_transmission_time_alarm}

    ${DEACTIVATION_threshold_for_transmission_time_alarm_xpath}=    Set Variable    xpath=//input[@name='dclientLowTxTransThreshold']
    Wait Until Element Is Visible    ${DEACTIVATION_threshold_for_transmission_time_alarm_xpath}    timeout=5s
    Input Text By Pressing Keys    ${DEACTIVATION_threshold_for_transmission_time_alarm_xpath}    ${DEACTIVATION_threshold_for_transmission_time_alarm}
    Check If an Error Popup Appeared & Skip It

ACTIVATION threshold for MTD alarm
    [Arguments]    ${ACTIVATION_threshold_for_MTD_alarm}=11
    [Documentation]    Sets the ACTIVATION threshold for MTD alarm in the Alarms section. The value is between 2 and 50ms.
    ${is_in_range}=    Validate Number In Range - int    ${ACTIVATION_threshold_for_MTD_alarm}    2    50
    Run Keyword If    not ${is_in_range}    Fail    ACTIVATION threshold for MTD alarm must be between 2 and 50ms. Received: ${ACTIVATION_threshold_for_MTD_alarm}

    ${ACTIVATION_threshold_for_MTD_alarm_xpath}=    Set Variable    xpath=//input[@name='dclientHighMTDThreshold']
    Wait Until Element Is Visible    ${ACTIVATION_threshold_for_MTD_alarm_xpath}    timeout=5s
    Input Text By Pressing Keys    ${ACTIVATION_threshold_for_MTD_alarm_xpath}    ${ACTIVATION_threshold_for_MTD_alarm}
    Check If an Error Popup Appeared & Skip It

DEACTIVATION threshold for MTD alarm
    [Arguments]    ${DEACTIVATION_threshold_for_MTD_alarm}=10
    [Documentation]    Sets the DEACTIVATION threshold for MTD alarm in the Alarms section. The value is between 1 and 49ms.
    ${is_in_range}=    Validate Number In Range - int    ${DEACTIVATION_threshold_for_MTD_alarm}    1    49
    Run Keyword If    not ${is_in_range}    Fail    DEACTIVATION threshold for MTD alarm must be between 1 and 49ms. Received: ${DEACTIVATION_threshold_for_MTD_alarm}

    ${DEACTIVATION_threshold_for_MTD_alarm_xpath}=    Set Variable    xpath=//input[@name='dclientLowMTDThreshold']
    Wait Until Element Is Visible    ${DEACTIVATION_threshold_for_MTD_alarm_xpath}    timeout=5s
    Input Text By Pressing Keys    ${DEACTIVATION_threshold_for_MTD_alarm_xpath}    ${DEACTIVATION_threshold_for_MTD_alarm}
    Check If an Error Popup Appeared & Skip It

ACTIVATION threshold for FDV alarm
    [Arguments]    ${ACTIVATION_threshold_for_FDV_alarm}=0.60
    [Documentation]    Sets the ACTIVATION threshold for FDV alarm in the Alarms section. The value is between 0.2 and 25.0ms.
    ${is_in_range}=    Validate Number In Range _ decimals    ${ACTIVATION_threshold_for_FDV_alarm}    0.2    25.0
    Run Keyword If    not ${is_in_range}    Fail    ACTIVATION threshold for FDV alarm must be between 0.2 and 25.0ms. Received: ${ACTIVATION_threshold_for_FDV_alarm}

    ${ACTIVATION_threshold_for_FDV_alarm_xpath}=    Set Variable    xpath=//input[@name='dclientHighCDVThreshold']
    Wait Until Element Is Visible    ${ACTIVATION_threshold_for_FDV_alarm_xpath}    timeout=5s
    Input Text By Pressing Keys    ${ACTIVATION_threshold_for_FDV_alarm_xpath}    ${ACTIVATION_threshold_for_FDV_alarm}
    Check If an Error Popup Appeared & Skip It

DEACTIVATION threshold for FDV alarm
    [Arguments]    ${DEACTIVATION_threshold_for_FDV_alarm}=0.50
    [Documentation]    Sets the DEACTIVATION threshold for FDV alarm in the Alarms section. The value is between 0.1 and 24.9ms.
    ${is_in_range}=    Validate Number In Range _ decimals    ${DEACTIVATION_threshold_for_FDV_alarm}    0.1    24.9
    Run Keyword If    not ${is_in_range}    Fail    DEACTIVATION threshold for FDV alarm must be between 0.1 and 24.9ms. Received: ${DEACTIVATION_threshold_for_FDV_alarm}

    ${DEACTIVATION_threshold_for_FDV_alarm_xpath}=    Set Variable    xpath=//input[@name='dclientLowCDVThreshold']
    Wait Until Element Is Visible    ${DEACTIVATION_threshold_for_FDV_alarm_xpath}    timeout=5s
    Input Text By Pressing Keys    ${DEACTIVATION_threshold_for_FDV_alarm_xpath}    ${DEACTIVATION_threshold_for_FDV_alarm}
    Check If an Error Popup Appeared & Skip It


Command output blocking in case of FLR alarm
    [Arguments]    ${Command_output_blocking_in_case_of_FLR_alarm}=0
    [Documentation]    Sets the Command output blocking in case of FLR alarm in the Alarms section. The value is 0 or 1.
    ${is_in_range}=    Validate Number In Range - int    ${Command_output_blocking_in_case_of_FLR_alarm}    0    1
    Run Keyword If    not ${is_in_range}    Fail    Command output blocking in case of FLR alarm must be 0 or 1. Received: ${Command_output_blocking_in_case_of_FLR_alarm}

    ${Command_output_blocking_in_case_of_FLR_alarm_xpath}=    Set Variable    xpath=//input[@name='dtproCfgIcptFlrOutputBlocking']
    Wait Until Element Is Visible    ${Command_output_blocking_in_case_of_FLR_alarm_xpath}    timeout=5s
    Run Keyword If    '${Command_output_blocking_in_case_of_FLR_alarm}' == '1'    Select Checkbox    ${Command_output_blocking_in_case_of_FLR_alarm_xpath}
    Run Keyword If    '${Command_output_blocking_in_case_of_FLR_alarm}' == '0'    Unselect Checkbox    ${Command_output_blocking_in_case_of_FLR_alarm_xpath}

ACTIVATION threshold for FLR alarm
    [Arguments]    ${ACTIVATION_threshold_for_FLR_alarm}=55
    [Documentation]    Sets the ACTIVATION threshold for FLR alarm in the Alarms section. The value is between 10 and 100%.
    ${is_in_range}=    Validate Number In Range - int    ${ACTIVATION_threshold_for_FLR_alarm}    10    100
    Run Keyword If    not ${is_in_range}    Fail    ACTIVATION threshold for FLR alarm must be between 10 and 100%. Received: ${ACTIVATION_threshold_for_FLR_alarm}

    ${ACTIVATION_threshold_for_FLR_alarm_xpath}=    Set Variable    xpath=//input[@name='dtproCfgIcptFlrActivationThreshold']
    Wait Until Element Is Visible    ${ACTIVATION_threshold_for_FLR_alarm_xpath}    timeout=5s
    Input Text By Pressing Keys    ${ACTIVATION_threshold_for_FLR_alarm_xpath}    ${ACTIVATION_threshold_for_FLR_alarm}
    Check If an Error Popup Appeared & Skip It

DEACTIVATION threshold for FLR alarm
    [Arguments]    ${DEACTIVATION_threshold_for_FLR_alarm}=50
    [Documentation]    Sets the DEACTIVATION threshold for FLR alarm in the Alarms section. The value is between 5 and 95%.
    ${is_in_range}=    Validate Number In Range - int    ${DEACTIVATION_threshold_for_FLR_alarm}    5    95
    Run Keyword If    not ${is_in_range}    Fail    DEACTIVATION threshold for FLR alarm must be between 5 and 95%. Received: ${DEACTIVATION_threshold_for_FLR_alarm}

    ${DEACTIVATION_threshold_for_FLR_alarm_xpath}=    Set Variable    xpath=//input[@name='dtproCfgIcptFlrDeactivationThreshold']
    Wait Until Element Is Visible    ${DEACTIVATION_threshold_for_FLR_alarm_xpath}    timeout=5s
    Input Text By Pressing Keys    ${DEACTIVATION_threshold_for_FLR_alarm_xpath}    ${DEACTIVATION_threshold_for_FLR_alarm}
    Check If an Error Popup Appeared & Skip It

Authentication key Assignment
    [Arguments]    ${activate_deactivate}=0    ${ICPT_AUTH_KEY_USR}=${EMPTY}    ${ICPT_AUTH_KEY_CONF_USR}=${EMPTY}
    [Documentation]    Assigns the Authentication key in the Alarms section.
    #It must have at least: 8 characters, 1 number, 1 uppercase letter, 1 lowercase letter, 1 special symbol
    IF    ${activate_deactivate} == 1
        Select Checkbox    xpath=//input[@name='dclientIcptUseAuthKey']

        ${ICPT_AUTH_KEY_USR_xpath}=    Set Variable    xpath=//input[@name='ICPT_AUTH_KEY_USR']
        Wait Until Element Is Visible    ${ICPT_AUTH_KEY_USR_xpath}    timeout=5s
        Input Text By Pressing Keys    ${ICPT_AUTH_KEY_USR_xpath}    ${ICPT_AUTH_KEY_USR}
        Check If an Error Popup Appeared & Skip It

        ${ICPT_AUTH_KEY_CONF_USR_xpath}=    Set Variable    xpath=//input[@name='ICPT_AUTH_KEY_CONF_USR']
        Wait Until Element Is Visible    ${ICPT_AUTH_KEY_CONF_USR_xpath}    timeout=5s
        Input Text By Pressing Keys    ${ICPT_AUTH_KEY_CONF_USR_xpath}    ${ICPT_AUTH_KEY_CONF_USR}
        Check If an Error Popup Appeared & Skip It
    ELSE IF   ${activate_deactivate} == 0
        Unselect Checkbox    xpath=//input[@name='dclientIcptUseAuthKey']
    ELSE
        Fail    activate_deactivate must be 1 or 0. Received: ${activate_deactivate}
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



Validate Number In Range - int
    [Documentation]    Now, this Keyword will accept int numbers (in the rev before wasn't able to do it)
    [Arguments]    ${number}    ${min}    ${max}
    ${is_number}    Run Keyword And Return Status    Convert To Integer    ${number}
    ${is_min}    Run Keyword And Return Status    Convert To Integer    ${min}
    ${is_max}    Run Keyword And Return Status    Convert To Integer    ${max}    
    
    #We evaluate wether max & min are numbers or not. If they are not, we fail the test.
    Run Keyword If    not ${is_number}    Fail    El numero introducido no es válido
    Run Keyword If    not ${is_min}    Fail    No es un mínimo válido
    Run Keyword If    not ${is_max}    Fail    No es un máximo válido

    ${is_in_range}    Evaluate    (${min} <= ${number} <= ${max})
    Return From Keyword    ${is_in_range}
    Should Be True    ${is_in_range}

Validate Number In Range _ decimals
    [Documentation]    Now, this Keyword will accept decimal numbers
    [Arguments]    ${number}    ${min}    ${max}
    ${is_number}    Run Keyword And Return Status    Convert To Number    ${number}
    ${is_min}    Run Keyword And Return Status    Convert To Number    ${min}
    ${is_max}    Run Keyword And Return Status    Convert To Number    ${max}
    
    #We evaluate wether max & min are numbers or not. If they are not, we fail the test.
    Run Keyword If    not ${is_number}    Fail    El numero introducido no es válido
    Run Keyword If    not ${is_min}    Fail    No es un mínimo válido
    Run Keyword If    not ${is_max}    Fail    No es un máximo válido

    ${is_in_range}    Evaluate    (${min} <= ${number} <= ${max})
    Return From Keyword    ${is_in_range}
    Should Be True    ${is_in_range}