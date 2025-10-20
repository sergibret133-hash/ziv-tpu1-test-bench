*** Settings ***
Documentation                This is a basic test
Library    SeleniumLibrary
Library    String
Library    Collections
Library    OperatingSystem    #for file operations
Library    BuiltIn
Library    XML
Library    DateTime

Suite Setup    Setup Command_Assignments Pretests
Suite Teardown    Close Browser

*** Variables ***
#VALID LOGIN & ACCES TO WEBPAGE
${USER}    admin
${PASS}    Passwd%4002

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
${options}=  Create List  --ignore-certificate-errors  --disable-web-security  --allow-running-insecure-content
${commands}    Input/Output Alias

#************************************************************************************************************************
#BASIC CONFIGURATION TESTS
${SELECT_BUTTON}    xpath=//button[contains(text(),'Select')]


*** Test Cases ***
# PRUEBA Filtrado
#     ${container}=    Set Variable    (BEGINS) COMMAND (9) RECEPTION IN TP(2)
#     ${item}=    Set Variable    COMMAND (9) RECEPTION IN TP(2)    
#     ${found}    Filter Phrase In Phrase Container    ${item}    ${container}
#     Log To Console    ${found}
# PRUEBA 2 Filtrado
#     ${container}=    Set Variable    (BEGINS) COMMAND (1) RECEPTION IN TP(1)
#     ${item}=    Set Variable    COMMAND (9) RECEPTION IN TP(2)    
#     ${found}    Filter Phrase In Phrase Container    ${item}    ${container}
#     Log To Console    ${found}


# Delete & Retrieve Chronological Register
#     Delete Chronological Register
#     Retrieve Chronological Register
#     Sleep    4s

Retrieve Chronological Register   
    Retrieve Chronological Register
    Sleep    4s

# Capture 10 Last Chronological Log Entries
#     ${expected_number_of_entries}=    Set Variable    10
#     ${log_entries}=    Capture Chronological Log Entries    max_entries=${expected_number_of_entries}

#      # Verify if the number of entries is correct
#     ${actual_number_of_entries}=    Get Length    ${log_entries}
#     Should Be Equal As Integers
#     ...    ${actual_number_of_entries}
#     ...    ${expected_number_of_entries}
#     ...    msg=Expected ${expected_number_of_entries} log entries, but got ${actual_number_of_entries}.


#     FOR    ${entry}    IN    @{log_entries}
#         Log To Console    Alarm/Event: ${entry}[alarm_event], Timestamp: ${entry}[timestamp]
#     END
    
# Capture 10 Last Filtered Chronological Log Entries    
#     ${expected_number_of_entries}=    Set Variable    2    #should be only 2 entries found. One for (BEGINS) and one for (END)
#     ${log_entries}=    Capture Chronological Log Entries    event_filter= COMMAND (9) RECEPTION IN TP(2)    max_entries=10

#      # Verify if the number of entries is correct
#     ${actual_number_of_entries}=    Get Length    ${log_entries}
#     Should Be Equal As Integers
#     ...    ${actual_number_of_entries}
#     ...    ${expected_number_of_entries}
#     ...    msg=Expected ${expected_number_of_entries} log entries, but got ${actual_number_of_entries}.

#     FOR    ${entry}    IN    @{log_entries}
#         Log To Console    Alarm/Event: ${entry}[alarm_event], Timestamp: ${entry}[timestamp]
#     END

# Capture 25 Last INVALID Filtered Chronological Log Entries    #invalid event_filter -> There should be no entry found
#     ${expected_number_of_entries}=    Set Variable    0
#     ${log_entries}=    Capture Chronological Log Entries    event_filter= sdfsgs231    max_entries=${expected_number_of_entries}

#     ${actual_number_of_entries}=    Get Length    ${log_entries}

#     Should Be Equal As Integers
#     ...    ${actual_number_of_entries}
#     ...    ${expected_number_of_entries}
#     ...    msg=Expected ${expected_number_of_entries} log entries, but got ${actual_number_of_entries}.

#     FOR    ${entry}    IN    @{log_entries}
#         Log To Console    Alarm/Event: ${entry}[alarm_event], Timestamp: ${entry}[timestamp]
#     END

# Capture 150 Last Filtered Chronological Log Entries    #more entries than the available ones
#     ${expected_number_of_entries}=    Set Variable    99
#     ${log_entries}=    Capture Chronological Log Entries    max_entries= 150

#     ${actual_number_of_entries}=    Get Length    ${log_entries}

#     Should Be Equal As Integers
#     ...    ${actual_number_of_entries}
#     ...    ${expected_number_of_entries}
#     ...    msg=Expected ${expected_number_of_entries} log entries, but got ${actual_number_of_entries}.

#     FOR    ${entry}    IN    @{log_entries}
#         Log To Console    Alarm/Event: ${entry}[alarm_event], Timestamp: ${entry}[timestamp]
#     END


Analyze Activation Times
#Time passed between two orders received from another TPU using two differents teleprotecion modules. 
    ${Tp1_IOCS}=    Capture Chronological Log Entries    event_filter=(BEGINS) COMMAND (1) RECEPTION IN TP(1)    max_entries=1
    ${Tp2_IDTU}=    Capture Chronological Log Entries    event_filter=(BEGINS) COMMAND (9) RECEPTION IN TP(2)    max_entries=1
    # ${Tp1_IOCS} and ${Tp2_IDTU} are now lists of dictionaries with the last 1 entry containing event description and timestamp


    ${TP1_entry_count}=    Get Length    ${Tp1_IOCS}
    ${TP2_entry_count}=    Get Length    ${Tp2_IDTU}
    IF    (${TP1_entry_count} == 1 and ${TP2_entry_count} == 1)
        Log To Console    Alarm/Event: ${Tp1_IOCS}\[alarm_event], Timestamp: ${Tp1_IOCS}[0][timestamp]
        Log To Console    Alarm/Event: ${Tp2_IDTU}\[alarm_event], Timestamp: ${Tp2_IDTU}[0][timestamp]
        # Calculations between timestamps of different entries
        ${time_tp1}=    Set Variable    ${Tp1_IOCS}[0][timestamp]
        ${time_tp2}=    Set Variable    ${Tp2_IDTU}[0][timestamp]
        ${difference_seconds}=    Subtract Date From Date    ${time_tp2}    ${time_tp1}    result_format=number  #Tp2time is suposed to be greater than Tp1time, we follow the logic of Tp2time-Tp1time
        Log To Console    Difference between the last two desactivations: ${difference_seconds} seconds
    ELSE
        Fail    Not enough entries to calculate the difference. Expected 1, but got TP1_entry_count: ${TP1_entry_count} and TP2_entry_count: ${TP2_entry_count}.
    END


#*************************************************************************************************************************

*** Keywords ***
Setup Command_Assignments Pretests
    Open Broswer to Login page
    Wait Title    ${terminal_title}
    Click Open Folder    /
    Click Open Folder    MONITORING
    Open Section    Chronological register
    Wait Until Progress Bar Reaches 100 V2



    # Set Suite Variable    ${teleprotection_commands_list}    ${local_teleprotection_commands_list}

Open Broswer to Login page
    Open Browser    ${URL_COMPLETA}    ${BROWSER}    options=add_argument("--ignore-certificate-errors")
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
    Wait Until Element Is Not Visible    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario
#************************************************************************************************************************
#"Popup login" method Scripts 


Wait Title
    [Arguments]    ${TerminalTitle}    
    Wait Until Element Contains    ${TPU_WelcomeTitle_Type}    ${TerminalTitle}    90s

Wait Section Title
    [Arguments]    ${SectionTitle}    
    ${normalized_title}=    Evaluate    "${SectionTitle}".lower()
    Element Should Be Visible    xpath=//h2[translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${normalized_title}"]

#************************************************************************************************************************
#************************************************************************************************************************

#BASIC CONFIGURATION TESTS

RestartModules
    Select Module   0    0
    Sleep    0.2s
    FOR    ${slot}    IN RANGE    0    10
        ${xpath}=    Set Variable    //input[@name='dclientModulesView'][@var_index='${slot}']
        ${module_present}=    Run Keyword And Return Status    Page Should Contain Element    ${xpath}  #gather boolean value if xpath is present in the page 
        IF    ${module_present}  #check if there's an element in the slot
            ${value}=    SeleniumLibrary.Get Element Attribute    ${xpath}    value
            #If there's a module assigned
            # Run Keyword If    '${value}' != ''    Log    Slot ${slot}: Present Module with value "${value}"
            Run Keyword If    '${value}' != ''    Remove Module From Slot    ${slot}
            #If there's no module assigned
            # Run Keyword If    '${value}' == ''    Log    Slot ${slot}: Empty Module
        ELSE
            Log    Slot ${slot} not present
        END
    END

Assign Module To Slot
    [Arguments]    ${slot}   ${module}    ${id_module}
    Select Slot    ${slot}

    Select Module    ${module}    ${id_module}

    Click Element    xpath=//span[contains(@class,'p-button-label') and normalize-space(text())='Select']

    Sleep    0.3s


Remove Module From Slot
    [Arguments]    ${slot} 
    Select Slot    ${slot}
    Click Element    xpath=//span[contains(@class,'p-button-label') and normalize-space(text())='Select']
    Sleep    0.3s
    Run Keyword And Return Status    Handle Alert    ACCEPT
    Sleep    0.2s


Select Slot
    [Arguments]    ${slot} 
    ${xpath_slot}=    Set Variable    //select[@var_name='dclientSlotSelect'][@var_index='0'] 
    Wait Until Element Is Visible    ${xpath_slot}    timeout=5s    
    Select From List By Value    ${xpath_slot}    ${slot}

Select Module
    [Arguments]    ${module}   ${id_module}
    # Module order&assigment: 
    # 0: None, 112: IBTU, 32: IDTU, 64: IETU, 80: IOTU, 128: ICTU, 16: IPTU, 272: IPTU.10, 96: IRTU, 144: DSTU, 160: MCTU, 176: IOCT, 192: IPIT, 224: IEPT, 256: IOCS, 288: ICPT
    ${xpath_module}=    Set Variable    //select[@var_name='dclientModuleTypeSelect'][@var_index='0'] 
    Wait Until Element Is Visible    ${xpath_module}    timeout=5s    
    Select From List By Value    ${xpath_module}    ${module}

    Run Keyword If    '${id_module}' != '0'    Select Value Module    ${id_module}    

Select Value Module
    [Arguments]    ${id}
    ${xpath_number_module}=    Set Variable    //select[@var_name='dclientModuleNumberSelect'][@var_index='0'] 
    Wait Until Element Is Visible    ${xpath_number_module}    timeout=5s    
    Select From List By Value    ${xpath_number_module}    ${id}
    #We need to select Module number depending on the module type selected: 
    # THIS WILL BE ESTABLISHED IN THE TEST PROGRAM INTERFACE. WE'LL ONLY GATHER THE VALUE OF THE MODULE TYPE SELECTED PASSED AS AN ARGUMENT
        #IBTU, IDTU, IETU, IOTU, IOCT, IPIT, IOCS, ICPT: 2 posible Teleprotection
        #IPTU.10: 1 posible Module number
        #DSTU: 2 posible Module number
        #MCTU: 3 posible Module number
        #IRTU: 4 posible Module number
        #ICTU, IPTU, IEPT: 8 posible Module number    

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
Configure Display Time Zone
    [Arguments]    ${zone}
    ${xpath_timezone}=    Set Variable    //select[@var_name='dnmCfgSysTimeZone'][@var_index='0'] 
    Wait Until Element Is Visible    ${xpath_timezone}    timeout=5s    
    Select From List By Value    ${xpath_timezone}    ${zone}

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
            Log    Incomplete log row or unexpected structure. Skipping row.    WARN
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
                Log    Could not convert timestamp: "${full_timestamp_string}". Using original text components.    WARN
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

    Log List    ${captured_log_entries}
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


