*** Settings ***
Documentation                This is a basic test
Library    SeleniumLibrary
Library    String
Library    Collections
Library    OperatingSystem    #for file operations
Library    BuiltIn
Library    XML
Library    Screenshot
Library    BrowserManager.py

Resource    Keep_Alive.robot

Suite Setup    Run Keyword    Conectar A Navegador Existente    ${SESSION_ALIAS}    ${SESSION_FILE_PATH}
Test Setup        Check And Handle Session Expired Popup
Suite Teardown

*** Variables ***
# SESSION VARIABLES
${SESSION_ALIAS}
${SESSION_FILE_PATH}
#VALID LOGIN & ACCES TO WEBPAGE
${USER}    admin
${PASS}    Passwd%4002
${INTERNAL_PASS}    Passwd@02   
${URL_BASE}    https://


# ${terminal_title}    EUT Setup 1
${IP_ADDRESS}    10.212.43.87

# ${terminal_title}    EUT Setup 2
# ${IP_ADDRESS}    10.212.43.21

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


# --- DEFAULT VALUES FOR STANDALONE EXECUTION ---
# The GUI will overwrite these variables at runtime.
# Agent Parameters
${SNMP_AGENT_STATE}         1
${TRAPS_ENABLE_STATE}       1
${TPU_SNMP_PORT}            161
${SNMP_V1_V2_ENABLE}        1
${SNMP_V3_ENABLE}           1
# SNMP V1/V2c
${SNMP_V1_V2_READ}          public
${SNMP_V1_V2_SET}           private
# SNMP V3
${SNMP_V3_READ_USER}        snmpbasic
${SNMP_V3_READ_PASS}        snmpbasic
${SNMP_V3_READ_AUTH}        1
${SNMP_V3_WRITE_USER}       snmpadmin
${SNMP_V3_WRITE_PASS}       snmpadmin
${SNMP_V3_WRITE_AUTH}       1
# Notification Handling
${HOSTS_CONFIG_STR}         ${EMPTY}


*** Test Cases ***
Retrieve Full SNMP Configuration
    [Documentation]    Este Test Case recupera toda la configuración y la devuelve.
    Setup Folder Section
    ${agent_state}=    Retrieve SNMP Agent State
    ${hosts_list}=    Retrieve SNMP Hosts    ${agent_state}
    # En el futuro, se añadirían aquí las keywords para leer los otros parámetros.
    # Por ahora, devolvemos la lista de hosts para que la GUI la procese.
    Set Suite Variable    ${retrieved_hosts}    ${hosts_list}
    Log To Console    ${hosts_list}

Execute Full SNMP Configuration
    [Documentation]    Este es el único Test Case que la GUI llamará para programar TODO.
    ...    Recibe todas las variables necesarias desde Python.
    Setup Folder Section
    Configure SNMP Agent From GUI Data
    ...    ${SNMP_AGENT_STATE}
    ...    ${TRAPS_ENABLE_STATE}
    ...    ${TPU_SNMP_PORT}
    ...    ${SNMP_V1_V2_ENABLE}
    ...    ${SNMP_V3_ENABLE}
    ...    ${SNMP_V1_V2_READ}
    ...    ${SNMP_V1_V2_SET}
    ...    ${SNMP_V3_READ_USER}
    ...    ${SNMP_V3_READ_PASS}
    ...    ${SNMP_V3_READ_AUTH}
    ...    ${SNMP_V3_WRITE_USER}
    ...    ${SNMP_V3_WRITE_PASS}
    ...    ${SNMP_V3_WRITE_AUTH}
    ...    ${HOSTS_CONFIG_STR}

    Program Old    sSNMPParams
*** Keywords ***
#============== SUPER-KEYWORD ==============
Configure SNMP Agent From GUI Data
    [Arguments]
    ...    ${agent_state}
    ...    ${traps_state}
    ...    ${port}
    ...    ${v1v2_enable}
    ...    ${v3_enable}
    ...    ${v1v2_read}
    ...    ${v1v2_set}
    ...    ${v3_read_user}
    ...    ${v3_read_pass}
    ...    ${v3_read_auth}
    ...    ${v3_write_user}
    ...    ${v3_write_pass}
    ...    ${v3_write_auth}
    ...    ${hosts_config_str}

    SNMP Agent State                      ${agent_state}
    Traps Enable State                    ${agent_state}    ${traps_state}
    TPU SNMP Port Assignment              ${agent_state}    ${port}
    SNMP V1_V2 Enable                     ${agent_state}    ${v1v2_enable}
    SNMP V3 Enable                        ${agent_state}    ${v3_enable}
    SNMP V1_V2 Read Community             ${agent_state}    ${v1v2_read}
    SNMP V1_V2 Set Community              ${agent_state}    ${v1v2_set}
    Read SNMP V3 User Credentials         ${agent_state}    ${v3_enable}    ${v3_read_user}     ${v3_read_pass}     ${v3_read_auth}
    Read Write SNMP V3 User Credentials   ${agent_state}    ${v3_enable}    ${v3_write_user}    ${v3_write_pass}    ${v3_write_auth}
    Set SNMP Hosts                        ${agent_state}    ${hosts_config_str}



#============== AGENT PARAMETERS KEYWORDS ==============
Retrieve SNMP Agent State
    [Documentation]    Retrieves and returns the SNMP Agent state.
    Retrieve    gSNMPParams
    ${SNMP_Agent_State_xpath}=    Set Variable    xpath=//input[@name='dnmSNMPAgentActivate']
    Wait Until Element Is Visible    ${SNMP_Agent_State_xpath}    timeout=5s
    ${is_checked}=    Run Keyword And Return Status    Checkbox Should Be Selected    ${SNMP_Agent_State_xpath}
    ${agent_state}=    Set Variable If    ${is_checked}    1    0
    Return From Keyword    ${agent_state}

SNMP Agent State
    [Arguments]    ${value}
    Checkbox Selection    dnmSNMPAgentActivate    ${value}
Traps Enable State
    [Arguments]    ${agent_is_enabled}    ${value}
    Run Keyword If    '${agent_is_enabled}' == '1'    Checkbox Selection    dnmSNMPAgentTrapsActivate    ${value}

TPU SNMP Port Assignment
    [Arguments]    ${agent_is_enabled}    ${port}
    Run Keyword If    '${agent_is_enabled}' == '1'    Input Text By Pressing Keys    xpath=//input[@name='dnmSNMPPort']    ${port}

SNMP V1_V2 Enable
    [Arguments]    ${agent_is_enabled}    ${value}
    Run Keyword If    '${agent_is_enabled}' == '1'    Checkbox Selection    dnmSNMPV1V2c    ${value}

SNMP V3 Enable
    [Arguments]    ${agent_is_enabled}    ${value}
    Run Keyword If    '${agent_is_enabled}' == '1'    Checkbox Selection    dnmSNMPV3    ${value}

#============== SNMP V1/V2c KEYWORDS ==============
SNMP V1_V2 Read Community
    [Arguments]    ${agent_is_enabled}    ${community}
    Run Keyword If    '${agent_is_enabled}' == '1'    Input Text By Pressing Keys    xpath=//input[@name='dnmSNMPAgentReadCommunity']    ${community}

SNMP V1_V2 Set Community
    [Arguments]    ${agent_is_enabled}    ${community}
    Run Keyword If    '${agent_is_enabled}' == '1'    Input Text By Pressing Keys    xpath=//input[@name='dnmSNMPAgentSetCommunity']    ${community}

#============== SNMP V3 KEYWORDS ==============
Read SNMP V3 User Credentials
    [Arguments]    ${agent_is_enabled}    ${V3_enable}    ${user}    ${password}    ${auth_protocol}
    IF    '${agent_is_enabled}' == '1' and '${V3_enable}' == '1'
        _Set_V3_User    dnmSNMPAgentUserNameReadOnly    dnmSNMPAgentPasswordReadOnly    dnmSNMPAgentPasswordReadOnlyConfirm    dnmSNMPManagerAuthenticationReadOnly    ${user}    ${password}    ${auth_protocol}
    ELSE
        Log To Console    V3 Protocol is not activated.
    END

Read Write SNMP V3 User Credentials
    [Arguments]    ${agent_is_enabled}    ${V3_enable}    ${user}    ${password}    ${auth_protocol} 
    IF    '${agent_is_enabled}' == '1' and '${V3_enable}' == '1'
        _Set_V3_User    dnmSNMPAgentUserNameReadWrite    dnmSNMPAgentPasswordReadWrite    dnmSNMPAgentPasswordReadWriteConfirm    dnmSNMPManagerAuthenticationReadWrite    ${user}    ${password}    ${auth_protocol}
    ELSE
        Log To Console    V3 Protocol is not activated.
    END
_Set_V3_User
    [Arguments]    ${user_name}    ${pass_name}    ${pass_confirm_name}    ${auth_select_name}    ${user_val}    ${pass_val}    ${auth_val}
    Input Text By Pressing Keys    xpath=//input[@name='${user_name}']           ${user_val}
    Input Text By Pressing Keys    xpath=//input[@name='${pass_name}']          ${pass_val}
    Input Text By Pressing Keys    xpath=//input[@name='${pass_confirm_name}']    ${pass_val}
    Select From List By Value      xpath=//select[@var_name='${auth_select_name}']    ${auth_val}


#============== NOTIFICATION HANDLING KEYWORDS ==============
Retrieve SNMP Hosts
    [Arguments]    ${agent_is_enabled}
    ${hosts_list}=    Create List
    Run Keyword If    '${agent_is_enabled}' == '0'    Return From Keyword    ${hosts_list}

    Retrieve    gSNMPParams
    FOR    ${host_index}    IN RANGE    1    6
        ${host_enable_xpath}=      Set Variable    xpath=((//div[@data-intref='SNMP_NOTIFICATION']/ancestor::div[@class='infoExtTable_Content']//tr)[${host_index}+1]/td)[2]//input[@name='dnmSNMPManagerEnable']
        ${is_checked}=             Run Keyword And Return Status    Checkbox Should Be Selected    ${host_enable_xpath}
        ${host_enable}=            Set Variable If    ${is_checked}    1    0

        ${host_ip_xpath}=          Set Variable    xpath=((//div[@data-intref='SNMP_NOTIFICATION']/ancestor::div[@class='infoExtTable_Content']//tr)[${host_index}+1]/td)[3]//input[@name='dnmSNMPManagerIpAddress']
        ${host_ip}=                Get Element Attribute    ${host_ip_xpath}    value

        ${host_port_xpath}=        Set Variable    xpath=((//div[@data-intref='SNMP_NOTIFICATION']/ancestor::div[@class='infoExtTable_Content']//tr)[${host_index}+1]/td)[4]//input[@name='dnmSNMPManagerPort']
        ${host_port}=              Get Element Attribute    ${host_port_xpath}    value
        
        ${host_trap_mode_xpath}=   Set Variable    xpath=((//div[@data-intref='SNMP_NOTIFICATION']/ancestor::div[@class='infoExtTable_Content']//tr)[${host_index}+1]/td)[5]//select[@var_name='dnmSNMPManagerTrapMode']
        ${host_trap_mode}=         Get Selected List Value    ${host_trap_mode_xpath}

        ${host_info}=              Create List    ${host_enable}    ${host_ip}    ${host_port}    ${host_trap_mode}
        Append To List             ${hosts_list}    ${host_info}
    END
    Return From Keyword    ${hosts_list}
Set SNMP Hosts
    [Arguments]    ${agent_is_enabled}    ${hosts_list_str}
    Run Keyword If    '${agent_is_enabled}' == '0' or '${hosts_list_str}' == '${EMPTY}'    Return From Keyword

    @{hosts_list}=    Evaluate    ${hosts_list_str}
    FOR    ${host_data}    IN ENUMERATE    @{hosts_list}
        ${index}=          Set Variable    ${host_data[0]}
        ${config}=         Set Variable    ${host_data[1]}
        ${host_number}=    Evaluate    ${index} + 1
        Configure Single Notification Host    ${host_number}    ${config[0]}    ${config[1]}    ${config[2]}    ${config[3]}
    END

Configure Single Notification Host
    [Arguments]    ${host_num}    ${enable}    ${ip_addr}    ${port}    ${trap_mode}
    Log    Configurando Host #${host_num}: Enable=${enable}, IP=${ip_addr}, Port=${port}, Mode=${trap_mode}

    ${host_index_in_table}=    Evaluate    ${host_num} + 1
    ${enable_xpath}=    Set Variable    xpath=((//div[@data-intref='SNMP_NOTIFICATION']/ancestor::div[@class='infoExtTable_Content']//tr)[${host_index_in_table}]/td)[2]//input[@name='dnmSNMPManagerEnable']
    Run Keyword If    '${enable}' == '1'    Select Checkbox    ${enable_xpath}
    ...    ELSE    Unselect Checkbox    ${enable_xpath}

    Run Keyword If    '${ip_addr}' != '${EMPTY}'    Input Text By Pressing Keys    xpath=((//div[@data-intref='SNMP_NOTIFICATION']/ancestor::div[@class='infoExtTable_Content']//tr)[${host_index_in_table}]/td)[3]//input[@name='dnmSNMPManagerIpAddress']    ${ip_addr}
    Run Keyword If    '${port}' != '${EMPTY}'       Input Text By Pressing Keys    xpath=((//div[@data-intref='SNMP_NOTIFICATION']/ancestor::div[@class='infoExtTable_Content']//tr)[${host_index_in_table}]/td)[4]//input[@name='dnmSNMPManagerPort']       ${port}
    Run Keyword If    '${trap_mode}' != '${EMPTY}'    Select From List By Value      xpath=((//div[@data-intref='SNMP_NOTIFICATION']/ancestor::div[@class='infoExtTable_Content']//tr)[${host_index_in_table}]/td)[5]//select[@var_name='dnmSNMPManagerTrapMode']    ${trap_mode}
#************************************************************************************************************************
#************************************************************************************************************************

Setup Folder Section
    Click Open Folder    /
    Click Open Folder    SNMP
    Open Section    SNMP Agent
    Wait Section Title    SNMP AGENT CONFIGURATION
    Sleep    0.5s

    # Set Suite Variable    ${teleprotection_commands_list}    ${local_teleprotection_commands_list}
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
    # Sleep    1s

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
    ${Handle_Alert_Detail}    Run Keyword And Return Status    Handle Alert    action=ACCEPT    timeout=0.3s
    Log To Console    ${Handle_Alert_Detail}
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
Wait Title
    [Arguments]    ${TerminalTitle}    
    Wait Until Element Contains    ${TPU_WelcomeTitle_Type}    ${TerminalTitle}    90s

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

Checkbox Selection
    [Arguments]    ${checkbox}    ${value}
    #Checkbox = 0: Teleprotection disabled at start-up; Checkbox = 1: Teleprotection enabled at start-up
    ${checkbox}    Set Variable    //input[@name='${checkbox}']
    Wait Until Element Is Visible    ${checkbox}    timeout=5s    
    Run Keyword If    '${value}' == '1'    Select Checkbox    ${checkbox}
    Run Keyword If    '${value}' == '0'    Unselect Checkbox    ${checkbox}
    Sleep    0.1s
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


