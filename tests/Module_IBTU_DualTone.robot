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
Suite Setup    Conectar A Navegador Existente
Test Setup        Check And Handle Session Expired Popup
Suite Teardown

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

# ${terminal_title}    EUT Setup 1
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
    ${Telep_name_to_config}=    Set Variable    IBTU
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
# 1st Section
# Config max num of TX commands
#     Autoconfig to max num of commands    1    ${Telep_number_to_config}    @{available_modules_commands}
# Config max num of RX commands
#     Autoconfig to max num of commands    0    ${Telep_number_to_config}    @{available_modules_commands}

# Reception Operation Mode
#     Assign Reception Operation Mode    1    #Telesignalling
#     Sleep    2s

# INVALID LOCAL Automatic Link Test Periodicity
#     LOCAL Automatic Link Test Periodicity Assign    25
#     Sleep    2s
# LOCAL Automatic Link Test Periodicity
#     LOCAL Automatic Link Test Periodicity Assign    0
#     Sleep    2s
# REMOTE Automatic Link Test Periodicity
#     REMOTE Automatic Link Test Periodicity Assign    0
#     Sleep    2s

# INVALID Activation & Deactivation Threshold Assign for Low SNR
#     Activation Threshold Assign for low Snr Ratio Alarm    -3
#     Sleep    2s
# Activation & Deactivation Threshold Assign for Low SNR
#     Activation Threshold Assign for low Snr Ratio Alarm    0
#     Sleep    2s
#     Deactivation Threshold Assign for low Snr Ratio Alarm    3
#     Sleep    2s

# Programm
#     Program Old    sCOM
#     Sleep    2s
#*************************************************************************************************************************
# 2nd Section
# Transmision parameters
#     Guard Position Parameters    1    1    # Super audio Band (2640 Hz./3120 Hz.) - (BW = 4 KHz.)
#     Sleep    2s
# Reception parameters
#     Guard Position Parameters    0    1    # Super audio Band (2640 Hz./3120 Hz.) - (BW = 4 KHz.)
#     Sleep    2s

# Assign Invalid RX parameters
#     Assign RX Application Type    5    0    ${Telep_number_to_config}    ${available_modules_commands}
#     Sleep    2s

# Assign RX parameters
#     Autoconfig Reception Operation Mode    0    ${Telep_number_to_config}    ${available_modules_commands}   #Blocking
#     Sleep    2s

# Program
#     Program Old    sCOM
#*************************************************************************************************************************
# 3rd Section
Assign Input Level
    Input Level    -8
    Sleep    3s
Assign Power Boosting_1
    Power Boosting    1
    Sleep    3s
Assign Output Level
    Output Level    -2
    Sleep    3s

Invalid Assign Power Boosting
    Log To Console    Proceed to Introduce a Invalid PowerBoosting number
    Sleep    1s
    Power Boosting    3
    Sleep    2s
Assign Power Boosting_2
    Log To Console    Proceed to Introduce a valid PowerBoosting number
    Sleep    1s
    Power Boosting    0
    Sleep    2s

# We change to Low frequency - (BW = 2.5 KHz.) option in one of the Guard Position
Assign Guard Position Parameters_1
    Log To Console    Proceed to Introduce an invalid Guard Position Parameters for B commands checkbox
    Sleep    1s
    Guard Position Parameters    1    2    # Low frequency - (BW = 2.5 KHz.)
    Sleep    2s

Assign Boosting Signalling Relay with B commands checkbox_INVALID
    Boosting Signalling Relay with B commands    1
    Sleep    2s

Assign Guard Position Parameters_2
# We change Guard Position from Low frequency to another option to be able to use the Boosting Signalling Relay with B commands checkbox
    Log To Console    Proceed to Introduce a valid Guard Position Parameters for B commands checkbox
    Sleep    1s
    Guard Position Parameters    1    1    # Super audio Band (2640 Hz./3120 Hz.) - (BW = 4 KHz.)
    Sleep    2s
    
Assign Boosting Signalling Relay with B commands checkbox
    Boosting Signalling Relay with B commands    1
    Sleep    2s

Programm
    Program Old    sGain
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
    Log To Console    ${Handle_Alert_Detail}
    Wait Until Progress Bar Reaches 100

Wait Until Progress Bar Reaches 100
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.5s
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

# ******************************************************************************************************************************
# ************************************************************************************************************************
#IBTU_ByTones MODULE CONFIG
#1st Section
Autoconfig to max num of commands
    [Arguments]    ${TX_RX}    ${Tp_num_id}    ${available_commands}
    [Documentation]    By default, selects the max Command Number. This value is synchronized with the Basic Configuration section. Available ${TX_RX} options: '1' if TX ; '0' if RX.
    IF    ${TX_RX} == 1
        ${index}=    Evaluate    ${Tp_num_id} - 1
        ${TXRX_value_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name='dtproCfgAnaTonCodedTransmitACommands']
    ELSE IF    ${TX_RX} == 0
        ${index}=    Evaluate    ${Tp_num_id} - 1 + 2
        ${TXRX_value_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name='dtproCfgAnaTonCodedReceiveACommands']
    END
    Wait Until Element Is Visible    ${TXRX_value_xpath}
    Scroll Element Into View Softly    ${TXRX_value_xpath}
    ${available_commands}=    Set Variable    ${available_commands}[${index}]
    # ${available_commands}=    Evaluate    ${available_commands} + 1
    Select From List By Value    ${TXRX_value_xpath}    ${available_commands}
    
LOCAL Automatic Link Test Periodicity Assign
    [Arguments]    ${link_test_periodicity_hours}
    ${is_in_range}    Validate Number In Range    ${link_test_periodicity_hours}    0    24
    IF    ${is_in_range}
        ${link_test_periodicity_hours_xpath}=    Set Variable    xpath=//input[contains(@name, 'dtproTestMgmtAutomaticTestPeriodicityHours')]
        # Click Element    ${link_test_periodicity_hours_xpath}
        Clear Element Text    ${link_test_periodicity_hours_xpath}
        Press Keys    ${link_test_periodicity_hours_xpath}    ${link_test_periodicity_hours}
        Press Key     ${link_test_periodicity_hours_xpath}    \\09
        ${error}    Check If an Error Popup Appeared & Skip It
        Log To Console    ${error}
    ELSE
        Fail    link_test_periodicity_hours is not a valid number. Value should be btw 0 - 24h
    END
    
REMOTE Automatic Link Test Periodicity Assign
    [Arguments]    ${link_test_periodicity_hours}
    ${is_in_range}    Validate Number In Range    ${link_test_periodicity_hours}    0    24
    IF    ${is_in_range}
        ${link_test_periodicity_hours_xpath}=    Set Variable    xpath=//input[contains(@name, 'dtproTestMgmtAutomaticTestRemote')]
        # Click Element    ${link_test_periodicity_hours_xpath}
        Clear Element Text    ${link_test_periodicity_hours_xpath}
        Press Keys    ${link_test_periodicity_hours_xpath}    ${link_test_periodicity_hours}
        Press Key     ${link_test_periodicity_hours_xpath}    \\09
        ${error}    Check If an Error Popup Appeared & Skip It
        Log To Console    ${error}
    ELSE
        Fail    link_test_periodicity_hours is not a valid number. Value should be btw 0 - 24h
    END
    
Activation Threshold Assign for low Snr Ratio Alarm
    [Documentation]    Deactivation threshold for low signal-to-noise ratio alarm (0 to 18 dB). It is recommended first configuring the Deactivation Threshold.
    [Arguments]    ${Snr_Threshold}
    ${is_in_range}    Validate Number In Range    ${Snr_Threshold}    0    18
    IF    ${is_in_range}
        ${Snr_Threshold_xpath}=    Set Variable    xpath=//input[contains(@name, 'dtproLowSnrThreshold')]
        # Click Element    ${Snr_Threshold_xpath}
        Clear Element Text    ${Snr_Threshold_xpath}
        Press Keys    ${Snr_Threshold_xpath}    ${Snr_Threshold}
        Press Key     ${Snr_Threshold_xpath}    \\09
        ${error}    Check If an Error Popup Appeared & Skip It
        Log To Console    ${error}
    ELSE
        Fail    Threshold is not a valid number. Value should be btw 0 - 18dB.
    END

Deactivation Threshold Assign for low Snr Ratio Alarm
    [Documentation]    Deactivation threshold for low signal-to-noise ratio alarm (2 to 20 dB).
    [Arguments]    ${Snr_Threshold}
    ${is_in_range}    Validate Number In Range    ${Snr_Threshold}    2    20
    IF    ${is_in_range}
        ${Snr_Threshold_xpath}=    Set Variable    xpath=//input[contains(@name, 'dtproHighSnrThreshold')]
        # Click Element    ${Snr_Threshold_xpath}
        Clear Element Text    ${Snr_Threshold_xpath}
        Press Keys    ${Snr_Threshold_xpath}    ${Snr_Threshold}
        Press Key     ${Snr_Threshold_xpath}    \\09
        ${error}    Check If an Error Popup Appeared & Skip It
        Log To Console    ${error}
    ELSE
        Fail    Threshold is not a valid number. Value should be btw 2 - 20dB.
    END
    
Assign Reception Operation Mode
    [Documentation]    Assign to the Command Number passed as an argument the Reception Operation Mode Selected. ${Reception_Operation_Mode} = 0 : Normal. ${Reception_Operation_Mode} = 1 : Telesignalling
    [Arguments]    ${Reception_Operation_Mode}
    # ${Command_Letter}    Convert Command Num To Letter    ${Command}
    # ${Mode_box_xpath}=    Set Variable    xpath=//select[contains(@var_name,'dtproFskRx${Command_Letter}Mode')]
    ${Mode_box_xpath}=    Set Variable    xpath=//div[text()= 'Reception operation mode']/ancestor-or-self::tr//div[@class='infoInpSelect']/select[@var_name='dtproRxMode']
    Select From List By Value    ${Mode_box_xpath}    ${Reception_Operation_Mode}
    Check If Alert Appears and Handle It


#*************************************************************************************************************************************************************

#2nd Section
Guard Position Parameters
    [Arguments]    ${TX_RX}    ${guard_position_value}
    [Documentation]    Assign the Guard Position Parameters associated to TX or RX. TX when ${TX_RX}='1' ; RX when ${TX_RX}='0'. Available Value options: '0': Low frequency(1200 Hz./1680 Hz.) - (BW = 4 KHz.) ; '1': Super-audio band(2640 Hz./3120 Hz.) - (BW = 4 KHz.) ; '2': Low frequency - (BW = 2.5 KHz.)
    IF    ${TX_RX} == 1
        ${Guard_Position_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name='dtproCfgAnaTonTxClientGuard']
    ELSE IF    ${TX_RX} == 0
        ${Guard_Position_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name='dtproCfgAnaTonRxClientGuard']
    ELSE
        Fail    TX_RX value passed as an argument is not valid. Available TX_RX values: TX when ${TX_RX}='1' ; RX when ${TX_RX}='0'.
    END

    Wait Until Element Is Visible    ${Guard_Position_xpath}
    Scroll Element Into View Softly    ${Guard_Position_xpath}
    Select From List By Value    ${Guard_Position_xpath}    ${guard_position_value}   

Assign RX Application Type
    [Documentation]    Assign to the Command Number passed as an argument the Application Type Selected. ${Application_Operation_Mode} = 0 : Blocking. ${Application_Operation_Mode} = 1 : Permissive trip. ${Application_Operation_Mode} = 2 : Direct trip. 
    [Arguments]    ${Command}    ${Application_Operation_Mode}    ${Tp_num_id}    ${available_commands}
    ${index}=    Evaluate    ${Tp_num_id} - 1 + 2
    ${available_commands}=    Set Variable    ${available_commands}[${index}]

    ${is_in_range}    Validate Number In Range - NEW    ${Command}    1    ${available_commands}
    Run Keyword If    not(${is_in_range})    Fail    The command parameter passed as an argument is not valid. Max Command Number is: ${available_commands}

    ${Application_box_xpath}=    Set Variable    xpath=//div[@class='infoDatInpLab_content' and text()='C${Command}']/ancestor-or-self::tr//select[@var_name='dtproCfgRxBW']
    Wait Until Element Is Visible    ${Application_box_xpath}    timeout=3s
    Scroll Element Into View Softly    ${Application_box_xpath}
    Select From List By Value    ${Application_box_xpath}    ${Application_Operation_Mode}
    # ${Handle_Alert_Detail}    Run Keyword And Return Status    Handle Alert    action=ACCEPT    timeout=0.5s
    # Log To Console    ${Handle_Alert_Detail}

Autoconfig Reception Operation Mode
    [Documentation]    Autoconfig the same Application Operation Mode to all available channels. ${Application_Operation_Mode} = 0 : Blocking. ${Application_Operation_Mode} = 1 : Permissive. ${Application_Operation_Mode} = 2 : Direct. 
    [Arguments]    ${Application_Operation_Mode}    ${Tp_num_id}    ${available_commands}
    ${index}=    Evaluate    ${Tp_num_id} - 1 + 2

    ${available_rx_commands}=    Set Variable    ${available_commands}[${index}]
    ${available_rx_commands_1}=    Evaluate    ${available_rx_commands} + 1

    FOR    ${command}    IN RANGE    1    ${available_rx_commands_1}
        Assign RX Application Type    ${command}     ${Application_Operation_Mode}    ${Tp_num_id}    ${available_commands}
    END

# 3ª Seccion
Input Level
    [Documentation]    Input Level Should between -40 - 0 dBm.
    [Arguments]    ${input_level}
    ${is_in_range}    Validate Number In Range - NEW    ${input_level}    -40    0
    IF    ${is_in_range}
        ${input_level_xpath}=    Set Variable    xpath=//input[@name= 'dclientTproInputGainFloatView']
        # Scroll Element Into View Softly    ${input_level_xpath}
        Clear Element Text    ${input_level_xpath}
        Press Keys    ${input_level_xpath}    BACKSPACE
        Press Keys    ${input_level_xpath}    BACKSPACE
        Press Keys    ${input_level_xpath}    BACKSPACE
        Press Keys    ${input_level_xpath}    ${input_level}
        Press Keys   ${input_level_xpath}    TAB
        ${error}    Check If an Error Popup Appeared & Skip It
        Run Keyword If    '${error}' != '${None}'   Log To Console    Warning: An error pop-up appeared: "${error}"
    ELSE
        Fail    input_level is not a valid number. Value should be btw -40 - 0dBm
    END

Output Level
    [Documentation]    Output Level Should between -30 - 0 dBm. Start configuring Power Boosting Level First IS CRUCIAL!
    [Arguments]    ${output_level}
    ${is_in_range}    Validate Number In Range - NEW    ${output_level}    -30    0
    IF    ${is_in_range}
        ${output_level_xpath}=    Set Variable    xpath=//input[@name= 'dclientTproOutputGainFloatView']
        # Scroll Element Into View Softly    ${output_level_xpath}
        Clear Element Text    ${output_level_xpath}
        # Sleep    0.1s
        # Click Element    locator=${output_level_xpath}
        Press Keys    ${output_level_xpath}    BACKSPACE
        Press Keys    ${output_level_xpath}    BACKSPACE
        Press Keys    ${output_level_xpath}    BACKSPACE
        Press Keys    ${output_level_xpath}    ${output_level}
        Press Keys   ${output_level_xpath}    TAB
        ${error}    Check If an Error Popup Appeared & Skip It
        Run Keyword If    '${error}' != '${None}'   Log To Console    Warning: An error pop-up appeared: "${error}"
    ELSE
        Fail    input_level is not a valid number. Value should be btw -30 - 0dBm
    END

Power Boosting
    [Documentation]    Power Boosting Should between 0 - 6 dB. Start configuring Power Boosting Level First IS CRUCIAL!
    [Arguments]    ${Power_Boosting}
    ${is_in_range}    Validate Number In Range - NEW    ${Power_Boosting}    0    6
    IF    ${is_in_range}
        ${powerboosting_level_xpath}=    Set Variable    xpath=//input[@name= 'dtproPowerIncrement']
        # Scroll Element Into View Softly    ${powerboosting_level_xpath}
        Clear Element Text    ${powerboosting_level_xpath}
        Press Keys    ${powerboosting_level_xpath}    BACKSPACE
        Press Keys    ${powerboosting_level_xpath}    BACKSPACE
        Press Keys    ${powerboosting_level_xpath}    BACKSPACE
        # Click Element    locator=${powerboosting_level_xpath}
        Press Keys    ${powerboosting_level_xpath}    ${Power_Boosting}
        Press Keys   ${powerboosting_level_xpath}    TAB
        ${error}    Check If an Error Popup Appeared & Skip It
        Run Keyword If    '${error}' != '${None}'   Log To Console    Warning: An error pop-up appeared: "${error}"
    ELSE
        Fail    input_level is not a valid number. Value should be btw 0 - 6dB
    END

Boosting Signalling Relay with B commands
    [Arguments]    ${Activate}
    [Documentation]    This Keyword can only be used when Tx and Rx Guard Position are different from Low frequency - (BW = 2.5 KHz.) option
    ${RX_Guard_Position_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name='dtproCfgAnaTonRxClientGuard']
    ${TX_Guard_Position_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name='dtproCfgAnaTonTxClientGuard']
    
    ${RX_Guard_Position_value}    Get Selected List Value    ${RX_Guard_Position_xpath}
    ${TX_Guard_Position_value}    Get Selected List Value    ${TX_Guard_Position_xpath}
    
    # Check if the Guard Position is different from Low frequency - (BW = 2.5 KHz.) option
    Run Keyword If    '${RX_Guard_Position_value}' == '2' or '${TX_Guard_Position_value}' == '2'    Fail    Boosting Signalling Relay with B commands can only be used when Tx and Rx Guard Position are different from Low frequency - (BW = 2.5 KHz.) option
    # Check if the Activate argument is '1' or '0'
    Run Keyword If    '${Activate}' != '1' and '${Activate}' != '0'    Fail    Activate argument should be '1' or '0'. Received: ${Activate}
    # If Activate is '1', select the checkbox to boost the relay
    ${Checkbox_xpath}=    Set Variable    xpath=//div[@class='infoInpCheck']/input[@name='dtproCfgAnaTonCodedBoostRelayToBCmd']
    Wait Until Element Is Visible    ${Checkbox_xpath}    timeout=5s
    Scroll Element Into View Softly    ${Checkbox_xpath}
    IF    '${Activate}' == '1'
        Select Checkbox    ${Checkbox_xpath}
    ELSE
        Unselect Checkbox    ${Checkbox_xpath}
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



Validate Number In Range - NEW
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
