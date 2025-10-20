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

${terminal_title}    EUT Setup 2
${IP_ADDRESS}    10.212.43.21

# ${terminal_title}    EUT Setup 1
# ${IP_ADDRESS}    10.212.43.87

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
    ${Telep_name_to_config}=    Set Variable    IOTU
    ${available_modules}=    Detect Available Modules
    ${available_modules_names}=    Set Variable    ${available_modules}[0]
    ${available_modules_commands}=    Set Variable    ${available_modules}[1]

    ${Telep_number_to_config}    Check if Telep available and Return TP ID    ${Telep_name_to_config}    ${available_modules_names}
    Set Suite Variable    ${available_modules_commands}
    Set Suite Variable    ${Telep_number_to_config}
Open Line Interface Section
    Setup Folder Section
    Open Line Interface Section Associated To Teleprotection    ${Telep_number_to_config}
    Sleep    1s

#*************************************************************************************************************************
# PRUEBAS
    # Autoconfig Predefine Tx_commands    ${Telep_number_to_config}    ${available_modules_commands}    Blocking
    # Assign Decision Threshold    2    1
    # Sleep    5s

# 1st Section
# Autoconfig Tx Commands
#     Autoconfig Predefine Tx_commands    ${Telep_number_to_config}    ${available_modules_commands}    Blocking
#     Sleep    2s

#     Autoconfig Predefine Tx_commands    ${Telep_number_to_config}    ${available_modules_commands}    Permissive trip
#     Sleep    2s

#     Autoconfig Predefine Tx_commands    ${Telep_number_to_config}    ${available_modules_commands}    Direct trip
#     Sleep    2s
# Programm
#     Program Old    sCOM
#*************************************************************************************************************************
# 2nd Section
# Identifiers config
#     ${TX_ID}    Set Variable    0
#     ${RX_ID}    Set Variable    1
#     Identifiers config    ${TX_ID}    ${RX_ID}
#     Sleep    2s

# Clock Type Selection
#     ${clock_type}    Set Variable    Internal
#     Clock Type Selection    ${clock_type}
#     Sleep    2s

# Clock Type Selection_Invalid
#     ${clock_type}    Set Variable    Inteal
#     Clock Type Selection    ${clock_type}
#     Sleep    2s

# Automatic Link Test Periodicity
#     ${periodicity}    Set Variable    0
#     Automatic Link Test Periodicity    ${periodicity}
#     Sleep    2s

# With Tx Time measurement
#     ${with_tx_measurement}    Set Variable    1
#     With TX time measure Checkbox    ${with_tx_measurement}
#     Sleep    2s
# Programm
#     Program Old    sCOM

#*************************************************************************************************************************
# 3rd Section
# Command Output Blocking INV_CMD_reception
#     ${command_output_blocking_INV_CMD_reception}    Set Variable    1
#     Command Output Blocking in case of INV_CMD_reception   ${command_output_blocking_INV_CMD_reception}

# Command output blocking in case of BER alarm
#     ${command_output_blocking}    Set Variable    1
#     Command output blocking in case of BER alarm Checkbox    ${command_output_blocking}

# ACTIVATION threshold for BER alarm Selection_Invalid
#     ${activation_threshold}    Set Variable    10
#     ACTIVATION threshold for BER alarm Selection    ${activation_threshold}
#     Sleep    2s
# ACTIVATION threshold for BER alarm Selection
#     ${activation_threshold}    Set Variable    1.0E-6
#     ACTIVATION threshold for BER alarm Selection    ${activation_threshold}
#     Sleep    2s
# DEACTIVATION threshold for BER alarm Selection
#     ${deactivation_threshold}    Set Variable    0.5E-6
#     DEACTIVATION threshold for BER alarm Selection    ${deactivation_threshold}
#     Sleep    2s
# Programm
#     Program Old    sCOM

#*************************************************************************************************************************
# Invalid Command Conditions
Open INV_CMD Conditions Section
    Open INV_CMD Conditions Section Associated To Teleprotection    ${Telep_number_to_config}
    Sleep    2s
Assign INV_CMD Conditions
    ${invalid_alarms}    Create List    Failure of the module in Slot 1    Failure of the module in Slot 2    Manual Blocking Teleprotection 2    #Few exemples of possible INV_CMD conditions       
    Assign Invalid Command Alarms    ${invalid_alarms}
    Program Old    sInvCmdCond
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
#IOTU MODULE CONFIG
# Security and dependability criteria in command reception / Transmission times config
Assign IOTU Command Type
    [Arguments]    ${command_number}    ${config_name}
    [Documentation]    Assigns a radio button to a command in the IOTU section. Available Command Type configurations: Blocking, Permissive trip and Direct trip
    ${radio_type}    Validate Config Name    ${config_name}
    
    IF    ${radio_type} == 0
        ${Decision_threshold}    Set Variable    2
        ${window_length}    Set Variable    3
    ELSE IF    ${radio_type} == 1
        ${Decision_threshold}    Set Variable    3
        ${window_length}    Set Variable    5
    ELSE IF    ${radio_type} == 2
        ${Decision_threshold}    Set Variable    5
        ${window_length}    Set Variable    7
    ELSE
        Fail    Invalid radio type. Please use 'Blocking', 'Permissive trip' or 'Direct trip'.
    END

    Assign Window Length    ${window_length}    ${command_number}
    Assign Decision Threshold    ${Decision_threshold}    ${command_number}


Assign Decision Threshold
    [Arguments]    ${threshold}    ${command_number}
    [Documentation]    Assigns the decision threshold for the IOTU commands.
    ${threshold_locator}    Set Variable    xpath=(//input[contains(@name, 'dtproCommandOutputCfgDecisionThreshold')])[${command_number}]

    Scroll Element Into View Softly    ${threshold_locator}
    Wait Until Element Is Visible    ${threshold_locator}    timeout=5s

    Press Keys    ${threshold_locator}    ${threshold}
Assign Window Length
    [Arguments]    ${window_length}    ${command_number}
    [Documentation]    Assigns the window length for the IOTU commands.
    ${window_length_locator}    Set Variable    xpath=(//input[contains(@name, 'dtproCommandOutputCfgWindowLength')])[${command_number}]

    Scroll Element Into View Softly    ${window_length_locator}
    Wait Until Element Is Visible    ${window_length_locator}    timeout=5s

    Press Keys    ${window_length_locator}    ${window_length}

Validate Config Name
    [Arguments]    ${config_name}
    [Documentation]    Validates the config name to ensure it is one of the expected values. Available config names: Blocking, Permissive trip and Direct trip.
    IF    "${config_name}" == "Blocking"
        ${radio_type}    Set Variable    0
    ELSE IF    "${config_name}" == "Permissive trip"
        ${radio_type}    Set Variable    1
    ELSE IF    "${config_name}" == "Direct trip"
        ${radio_type}    Set Variable    2
    ELSE
        Fail    Invalid radio name. Please use 'Blocking', 'Permissive trip' or 'Direct trip'.
    END
    Return From Keyword    ${radio_type}

Autoconfig Predefine Tx_commands
    [Arguments]    ${Telep_number_to_config}    ${Commands_List}    ${Command Type}
    [Documentation]    This keyword uses the IOCS module number to determine the maximum number of Tx commands for the module. It inspects the provided command_list argument to gather the relevant Tx data for the corresponding TP module. This keyword requires as an argument the Type of Command Assignment (Blocking, Permissive trip or Direct trip). 
    IF    "${Telep_number_to_config}" == "1"
        ${Max_Tx_Commands}=    Set Variable    ${Commands_List}[0]  # TP1 Tx commands
    ELSE IF    "${Telep_number_to_config}" == "2"
        ${Max_Tx_Commands}=    Set Variable    ${Commands_List}[1]  # TP2 Tx commands
    ELSE
        Fail    Invalid Teleprotection module number. Please use '1' or '2'.
    END
    ${Max_Tx_Commands}=    Evaluate    ${Max_Tx_Commands} + 1
    FOR    ${command}    IN RANGE    1    ${Max_Tx_Commands}
        Assign IOTU Command Type    ${command}    ${Command Type}
    END

# ******************************************************************************************************************************
# 2nd Section
Identifiers config
    [Arguments]    ${TX_ID}    ${RX_ID}
    [Documentation]    This keyword configures the identifiers for the Tx and Rx commands in the IOTU section. It requires the Tx and Rx IDs as arguments.
    ${TX_ID_locator}    Set Variable    xpath=//input[@name='dtproCfgTransmitIdCode' ]
    ${RX_ID_locator}    Set Variable    xpath=//input[@name='dtproCfgReceiveIdCode']
    Press Keys    ${TX_ID_locator}    ${TX ID}
    Press Keys    ${RX_ID_locator}    ${RX ID}

Automatic Link Test Periodicity
    [Arguments]    ${periodicity}
    [Documentation]    This keyword configures the periodicity (in hours) for the automatic link test in the IOCS section. It requires the periodicity as an argument.
    ${periodicity_locator}    Set Variable    xpath=//input[@name='dtproTestMgmtAutomaticTestPeriodicityHours']
    Scroll Element Into View Softly    ${periodicity_locator}
    Wait Until Element Is Visible    ${periodicity_locator}    timeout=5s
    Press Keys    ${periodicity_locator}    ${periodicity}

With TX time measure Checkbox
    [Arguments]    ${value}
    [Documentation]    This keyword configures the "With TX time measure" checkbox in the IOTU section. It requires the value as an argument (1 for checked, 0 for unchecked).
    ${checkbox_locator}    Set Variable    xpath=//input[@name='dtproTestMgmtAutomaticTestType']
    Scroll Element Into View Softly    ${checkbox_locator}
    Wait Until Element Is Visible    ${checkbox_locator}    timeout=5s
    Run Keyword If    '${value}' == '1'    Select Checkbox    ${checkbox_locator}
    Run Keyword If    '${value}' == '0'    Unselect Checkbox    ${checkbox_locator}
    Sleep    0.1s
Clock Type Selection
    [Arguments]    ${clock_type}
    [Documentation]    Clock Type names available: Internal/Recovered. This keyword configures the clock type in the IOTU section. It requires the clock type as an argument.
    ${clock_type_locator}    Set Variable    xpath=//select[@var_name='dtproCfgClockSource']
    # '0' for Internal, '1' for Recovered
    Scroll Element Into View Softly    ${clock_type_locator}
    Wait Until Element Is Visible    ${clock_type_locator}    timeout=5s
    ${clock_number_type}    Validate Clock Type    ${clock_type}
    Select From List By Value    ${clock_type_locator}    ${clock_number_type}
Validate Clock Type
    [Arguments]    ${clock_type}
    [Documentation]    Validates the clock type in the IOTU section. It requires the clock type as an argument. Only Internal and Recovered are valid clock types.
    IF    "${clock_type}" == "Internal"
        ${expected_value}    Set Variable    0
    ELSE IF    "${clock_type}" == "Recovered"
        ${expected_value}    Set Variable    1
    ELSE
        Fail    Invalid clock type. Please use 'Internal' or 'Recovered'.
    END
    Return From Keyword    ${expected_value}


# ******************************************************************************************************************************
#3rd Section
Command Output Blocking in case of INV_CMD_reception
    [Arguments]    ${value}
    [Documentation]    This keyword configures the "Command output blocking in case of INV_CMD_reception" checkbox in the IOTU section. It requires the value as an argument (1 for checked, 0 for unchecked).
    ${checkbox_locator}    Set Variable    xpath=//input[@name='dtproCfgInvCmdOutputBlocking']
    Scroll Element Into View Softly    ${checkbox_locator}
    Wait Until Element Is Visible    ${checkbox_locator}    timeout=5s
    Run Keyword If    '${value}' == '1'    Select Checkbox    ${checkbox_locator}
    Run Keyword If    '${value}' == '0'    Unselect Checkbox    ${checkbox_locator}
    Sleep    0.1s
Command output blocking in case of BER alarm Checkbox
    [Arguments]    ${value}
    [Documentation]    This keyword configures the "Command output blocking in case of BER alarm" checkbox in the IOTU section. It requires the value as an argument (1 for checked, 0 for unchecked).
    ${checkbox_locator}    Set Variable    xpath=//input[@name='dtproCfgBEROutputBlocking']
    Scroll Element Into View Softly    ${checkbox_locator}
    Wait Until Element Is Visible    ${checkbox_locator}    timeout=5s
    Run Keyword If    '${value}' == '1'    Select Checkbox    ${checkbox_locator}
    Run Keyword If    '${value}' == '0'    Unselect Checkbox    ${checkbox_locator}
    Sleep    0.1s

ACTIVATION threshold for BER alarm Selection
    [Arguments]    ${activation_threshold}
    [Documentation]    This keyword configures the activation threshold for the BER alarm in the IOTU section. It requires the activation threshold as an argument. Avaliable values: 1.0E-2, 0.5E-2, 1.0E-3, 0.5E-3, 1.0E-4, 0.5E-4, 1.0E-5, 0.5E-5, 1.0E-6, 0.5E-6, 1.0E-7, 0.5E-7, 1.0E-8, 0.5E-8, 1.0E-9, 0.5E-9
    ${Validate}    Run Keyword And Return Status    Validate Activation_Deactivation Threshold    ${activation_threshold}
    Run Keyword If    not ${Validate}    Fail    Invalid activation threshold value: ${activation_threshold}. Please use one of the valid values.

    ${Valid_values_list}    Validate Activation_Deactivation Threshold    ${activation_threshold}
    ${activation_threshold_value}=    Get Index From List    ${Valid_values_list}    ${activation_threshold}

    ${activation_threshold_locator}    Set Variable    xpath=//select[contains(@var_name, 'dclientLowBERThreshold')]
    Scroll Element Into View Softly    ${activation_threshold_locator}
    Wait Until Element Is Visible    ${activation_threshold_locator}    timeout=5s
    Select From List By Value    ${activation_threshold_locator}    ${activation_threshold_value}
DEACTIVATION threshold for BER alarm Selection
    [Arguments]    ${deactivation_threshold}
    [Documentation]    This keyword configures the deactivation threshold for the BER alarm in the IOTU section. It requires the deactivation threshold as an argument. Avaliable values: 1.0E-2, 0.5E-2, 1.0E-3, 0.5E-3, 1.0E-4, 0.5E-4, 1.0E-5, 0.5E-5, 1.0E-6, 0.5E-6, 1.0E-7, 0.5E-7, 1.0E-8, 0.5E-8, 1.0E-9, 0.5E-9
    ${Validate}    Run Keyword And Return Status    Validate Activation_Deactivation Threshold    ${deactivation_threshold}
    Run Keyword If    not ${Validate}    Fail

    ${Valid_values_list}    Validate Activation_Deactivation Threshold    ${deactivation_threshold}
    ${deactivation_threshold_value}=    Get Index From List    ${Valid_values_list}    ${deactivation_threshold}

    ${deactivation_threshold_locator}    Set Variable    xpath=//select[contains(@var_name, 'dclientHighBERThreshold')]
    Scroll Element Into View Softly    ${deactivation_threshold_locator}
    Wait Until Element Is Visible    ${deactivation_threshold_locator}    timeout=5s
    Select From List By Value    ${deactivation_threshold_locator}    ${deactivation_threshold_value}
Validate Activation_Deactivation Threshold
    [Arguments]    ${activation_threshold}
    [Documentation]    Validates the activation threshold for the BER alarm in the IOTU section. It requires the activation threshold as an argument. Avaliable values: 1.0E-2, 0.5E-2, 1.0E-3, 0.5E-3, 1.0E-4, 0.5E-4, 1.0E-5, 0.5E-5, 1.0E-6, 0.5E-6, 1.0E-7, 0.5E-7, 1.0E-8, 0.5E-8, 1.0E-9, 0.5E-9
    ${valid_values}=    Create List    1.0E-2    0.5E-2    1.0E-3    0.5E-3    1.0E-4    0.5E-4    1.0E-5    0.5E-5    1.0E-6    0.5E-6    1.0E-7    0.5E-7    1.0E-8    0.5E-8    1.0E-9    0.5E-9
    Run Keyword If    '${activation_threshold}' not in ${valid_values}    Fail    Invalid activation threshold value: ${activation_threshold}. Please use one of the valid values: ${valid_values}
    Return From Keyword    ${valid_values}

#******************************************************************************************************************************
Assign Invalid Command Alarms
    [Arguments]    ${invalid_alarms}
    FOR    ${alarm}    IN    @{invalid_alarms}
        # ${alarm_locator}    Set Variable    xpath=//div[contains(text(),"${alarm}")]/ancestor-or-self::tr//input[@name='dtproCfgInvCmdTxTp2AlrmConds']
        ${alarm_locator}    Set Variable    xpath=//div[contains(text(), '${alarm}')]/ancestor-or-self::tr//input
        
        Scroll Element Into View Softly    ${alarm_locator}
        Wait Until Element Is Visible    ${alarm_locator}    timeout=5s
        Select Checkbox    ${alarm_locator}
        Sleep    0.1s
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


