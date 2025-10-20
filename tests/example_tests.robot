*** Settings ***
Library    OperatingSystem

Resource    Keep_Alive.robot

*** Test Cases ***
Example Test
    Log To Console    Hello from example test
