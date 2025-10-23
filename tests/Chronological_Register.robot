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
Library    JSONLibrary

Resource    Keep_Alive.robot

Suite Setup    Conectar A Navegador Existente
Test Setup        Check And Handle Session Expired Popup
Suite Teardown

*** Variables ***
#VALID LOGIN & ACCES TO WEBPAGE
${USER}    admin
${PASS}    Passwd%4002
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
# CHRONOLOGICAL REGISTER
${EXPECTED_NUM_ENTRIES}    500
${EVENT_ALARM_FILTER}    ${EMPTY}
${CHRONO_ORDER}    ${False}
*** Test Cases ***
Delete Chronological Register
    Setup Folder Section
    Delete Chronological Register
    Retrieve Chronological Register

Retrieve Chronological Register
    Setup Folder Section
    Retrieve Chronological Register
    ${log_entries}=    Capture Chronological Log Entries    event_filter=${EVENT_ALARM_FILTER}    max_entries=${EXPECTED_NUM_ENTRIES}    ascending_order=${CHRONO_ORDER}
    
    Log    GUI_DATA::${log_entries}    level=DEBUG

Capture Last Chronological Log Entries
    Setup Folder Section
    Retrieve Chronological Register
    ${log_entries}=    Capture Chronological Log Entries    event_filter=${EVENT_ALARM_FILTER}    max_entries=${EXPECTED_NUM_ENTRIES}    ascending_order=${CHRONO_ORDER}
    
    # Convertimos la lista de diccionarios a un string JSON
    ${json_data}=    Evaluate    json.dumps(${log_entries})    modules=json
    Log    GUI_DATA::${json_data}    level=INFO
    # Log To Console    GUI_DATA::${json_data}    level=DEBUG
    

# Analyze Activation Times
# #Time passed between two orders received from another TPU using two differents teleprotecion modules. 
#     ${Tp1_IOCS}=    Capture Chronological Log Entries    event_filter=(BEGINS) COMMAND (1) RECEPTION IN TP(1)    max_entries=1
#     ${Tp2_IDTU}=    Capture Chronological Log Entries    event_filter=(BEGINS) COMMAND (9) RECEPTION IN TP(2)    max_entries=1
#     # ${Tp1_IOCS} and ${Tp2_IDTU} are now lists of dictionaries with the last 1 entry containing event description and timestamp

#     ${TP1_entry_count}=    Get Length    ${Tp1_IOCS}
#     ${TP2_entry_count}=    Get Length    ${Tp2_IDTU}
#     IF    (${TP1_entry_count} == 1 and ${TP2_entry_count} == 1)
#         Log To Console    Alarm/Event: ${Tp1_IOCS}\[alarm_event], Timestamp: ${Tp1_IOCS}[0][timestamp]
#         Log To Console    Alarm/Event: ${Tp2_IDTU}\[alarm_event], Timestamp: ${Tp2_IDTU}[0][timestamp]
#         # Calculations between timestamps of different entries
#         ${time_tp1}=    Set Variable    ${Tp1_IOCS}[0][timestamp]
#         ${time_tp2}=    Set Variable    ${Tp2_IDTU}[0][timestamp]
#         ${difference_seconds}=    Subtract Date From Date    ${time_tp2}    ${time_tp1}    result_format=number  #Tp2time is suposed to be greater than Tp1time, we follow the logic of Tp2time-Tp1time
#         Log To Console    Difference between the last two desactivations: ${difference_seconds} seconds
#     ELSE
#         Fail    Not enough entries to calculate the difference. Expected 1, but got TP1_entry_count: ${TP1_entry_count} and TP2_entry_count: ${TP2_entry_count}.
#     END

#*************************************************************************************************************************

*** Keywords ***
#CHRONOLOGICAL REGISTER KEYWORDS
Retrieve Chronological Register
    Sleep    0.5s
    ${retrieve_xpath_button}    Set Variable    xpath=//button[@class='p-button p-component p-button-sm button_BLogQuery']//span[normalize-space(text())='Retrieve']
    Scroll Element Into View Softly    ${retrieve_xpath_button}
    Wait Until Element Is Visible    ${retrieve_xpath_button}    timeout=5s
    Click Element    ${retrieve_xpath_button}
    Wait Until Progress Bar Reaches 100 V2

Delete Chronological Register
    Sleep    0.5s
    ${chronological_xpath_button}    Set Variable    xpath=//button[@class='p-button p-component p-button-sm button_BLogDelete']//span[normalize-space(text())='Delete']
    Scroll Element Into View Softly    ${chronological_xpath_button}
    Wait Until Element Is Visible    ${chronological_xpath_button}    timeout=5s
    Click Element    ${chronological_xpath_button}
    Wait Until Progress Bar Reaches 100 V2

Select Type
    [Arguments]    ${type}="All"
    [Documentation]    Select the type of register to be retrieved. "All", "Alarms" and "Events" options available. The default value is "All"
    ${Alarms_xpath}    Set Variable    xpath=//div[normalize-space(text())='Alarms' and @class='infoDatInpLab_content']/ancestor::td/following-sibling::td[1]//input[@type='checkbox']
    ${Events_xpath}    Set Variable    xpath=//div[normalize-space(text())='Events' and @class='infoDatInpLab_content']/ancestor::td/following-sibling::td[1]//input[@type='checkbox']
    IF    "${type}" == "All"
        Wait Until Element Is Visible    ${Alarms_xpath}    timeout=5s
        Select Checkbox    ${Alarms_xpath}
        Select Checkbox    ${Events_xpath}

    ELSE IF    "${type}" == "Alarms"
        Wait Until Element Is Visible    ${Alarms_xpath}    timeout=5s
        Select Checkbox    ${Alarms_xpath}
    ELSE IF    "${type}" == "Events"
        Wait Until Element Is Visible    ${Events_xpath}    timeout=5s
        Select Checkbox    ${Alarms_xpath} 
    ELSE
        Fail    Type not recognized. Please select All, Alarms or Events.
    END
    Sleep    0.1s

Capture Chronological Log Entries
    [Arguments]    ${event_filter}=${EMPTY}    ${max_entries}=10    ${ascending_order}=${False}
    [Documentation]    Captures entries from a chronological log, optionally filtering by event text
    ...    and limiting the number of entries from the most recent ones.
    ...    `event_filter`: If ${EMPTY}, no filter is applied.
    ...    `max_entries`: Maximum number of ¡filtered! (or not) entries to return.
    ...    `ascending_order`: If ${True}, takes the first N entries. If ${False} (default), takes the last N (most recent first in the list).

    # Locate the log rows
    ${rows_xpath}=    Set Variable    //table[contains(@class, 'TbChReg')]/tbody/tr
    
    Wait Until Page Contains Element    ${rows_xpath}    timeout=10s
    ${row_elements}=    Get WebElements    ${rows_xpath}
    ${row_count}=    Get Length    ${row_elements}
    ${row_count_FOR}=    Evaluate    ${row_count} + 1
    ${captured_log_entries}=    Create List
    ${added_entries_counter}=    Set Variable    0

    # Determine effective list to iterate based on 'ascending_order'
    # We'll iterate and then sort/slice if needed, or build the list in desired order.
    # The current loop processes DOM order. If DOM is chronological, and ascending_order=False,
    # we insert at the beginning of 'captured_log_entries' to get newest first.
    FOR    ${row}    IN RANGE    2    ${row_count_FOR}
        ${row_xpath}=    Set Variable    ((${rows_xpath})[${row}])
        # Extract data from each column of the row
        TRY
            ${alarm_event_text}=    Get Text    xpath=${row_xpath}//td[2]
            ${date_text}=    Get Text    xpath=${row_xpath}//td[3]
            ${time_text}=    Get Text    xpath=${row_xpath}//td[4]
            ${ms_text}=    Get Text    xpath=${row_xpath}//td[5]

        EXCEPT    Element not found    type=glob
            # Log    Incomplete log row or unexpected structure. Skipping row.    WARN
            CONTINUE
        END

        # Filter by event text (if specified)
        ${passes_filter}=    Set Variable    ${True}
        IF    "${event_filter}" != "${EMPTY}"
            ${alarm_event_lower}=    Convert To Lowercase    ${alarm_event_text}
            ${event_filter_lower}=    Convert To Lowercase    ${event_filter}

            ${phrase_found}=    Filter Phrase In Phrase Container    ${event_filter_lower}    ${alarm_event_lower}
            IF    ${phrase_found} == ${False}
                ${passes_filter}=    Set Variable    ${False}
            END
        END

        IF    ${passes_filter}    #As we set the default value of ${passes_filter} to True, if there's no filter, we will always pass the filter and continue
            # Combine date, time, ms and convert to datetime object
            ${full_timestamp_string}=    Set Variable    ${date_text} ${time_text}.${ms_text}
            TRY
                # Adjust input_format to match how ${full_timestamp_string} looks.
                ${timestamp_dt}=    Convert Date    ${full_timestamp_string}    date_format=%Y/%m/%d %H:%M:%S.%f
            EXCEPT
                # Log    Could not convert timestamp: "${full_timestamp_string}". Using original text components.    WARN
                ${timestamp_dt}=    Create Dictionary
                ...    date=${date_text}
                ...    time=${time_text}
                ...    ms=${ms_text}
                ...    raw_string=${full_timestamp_string}    # For debugging
            END

            ${entry}=    Create Dictionary
            ...    timestamp=${timestamp_dt}
            ...    alarm_event=${alarm_event_text}

            IF    ${ascending_order}
                Append To List    ${captured_log_entries}    ${entry}    # Adds to the end
            ELSE
                Insert Into List    ${captured_log_entries}    0    ${entry}    # Adds to the beginning
            END
            ${added_entries_counter}=    Set Variable    ${${added_entries_counter} + 1}
        END

        IF    ${added_entries_counter} >= ${max_entries}
            BREAK  # Exit loop if we have enough entries
        END
    END

    # Log List    ${captured_log_entries}
    # Log To Console    ${captured_log_entries}
    Return From Keyword    ${captured_log_entries}

Filter Phrase In Phrase Container
    [Arguments]    ${item}    ${container}
    # Scape brackets
    ${escaped_item}=    Replace String    ${item}    (    \\(
    ${escaped_item}=    Replace String    ${escaped_item}    )    \\)

    ${escaped_container}=    Replace String    ${container}    (    \\(
    ${escaped_container}=    Replace String    ${escaped_container}    )    \\)
    # Do a simple substring search
    ${found}=    Run Keyword And Return Status    Should Contain    ${escaped_container}    ${escaped_item}
    # Log To Console    ${found}
    Return From Keyword    ${found}

#*********************************************************************************************************************
#*********************************************************************************************************************
Setup Folder Section
    Click Open Folder    /
    Click Open Folder    MONITORING
    Open Section    Chronological register
    Wait Until Progress Bar Reaches 100 V2

Open Broswer to Login page
    [Arguments]    ${url}    ${brows}
    # Crea un objeto de opciones de Chrome
    ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver

    # Añade todos los argumentos de tu lista @{options}
    FOR    ${option}    IN    @{options}
        Call Method    ${chrome_options}    add_argument    ${option}
    END

    Open Browser    ${url}    browser=${brows}    options=${chrome_options}
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
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.2s
    Log    Waiting for the progress bar to be dissapeared...
    ${progress_bar_title_xpath}=    Set Variable    xpath=//div[contains(@class, "p-progressbar-label")]
    Wait Until Element Is Not Visible    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario
#************************************************************************************************************************
#"Popup login" method Scripts 


Wait Title
    [Arguments]    ${TerminalTitle}    
    Wait Until Element Contains    ${TPU_WelcomeTitle_Type}    ${TerminalTitle}    120s

Wait Section Title
    [Arguments]    ${SectionTitle}    
    ${normalized_title}=    Evaluate    "${SectionTitle}".lower()
    Element Should Be Visible    xpath=//h2[translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${normalized_title}"]



#************************************************************************************************************************
# ******************************************************************************************************************************
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
    ${checkbox}    Set Variable    //input[@name='dtproCfgEnedisDisabledAtStartUp']
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

#********************************************************************************************************************
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
