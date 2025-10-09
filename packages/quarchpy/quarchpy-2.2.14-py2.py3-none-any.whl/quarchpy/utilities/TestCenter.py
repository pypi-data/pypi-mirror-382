#!/usr/bin/python
"""
Implements the standard TestCenter API for Python, allowing a Python script to execute all TestCenter functions.
This is Quarch internal use only.  Each function uses the stdin/stdout to communicate with the TestCenter process
as such, communication is based on simple strings
"""

# import testCenter
from inspect import getframeinfo, stack
import sys


def setup(interface_name, *command_params, stack_level=1):
    """
    Sets up a test interface, passing the interface parameters onto TestCenter to process
    
    Parameters
    ----------
    interface_name : str
        Name of the interface to setup
    command_params : iterable object
        List of parameter strings to be passed to the setup function    
        
    Returns
    -------
    setup_response : str
        String returned from setup function. Generally "1" or "0" as a boolean success flag

    """

    # Get stack info so we can track the calling function for reporting and debug
    caller = getframeinfo(stack()[stack_level][0])

    # Write the command and params to STDOUT
    sys.stdout.write("SETUP," + str(caller.filename) + "," + str(caller.lineno) + "," + interface_name + ",")
    for index, item in enumerate(command_params):
        if index < len(command_params) - 1:
            sys.stdout.write("\"" + item + "\"" + ",")
        else:
            sys.stdout.write("\"" + item)

    sys.stdout.write("\n")
    sys.stdout.flush()

    # Read the response from STDIN as the function result
    return sys.stdin.readline().strip()


# Runs an interface setup function
def testPoint(command_name, *command_params, stack_level=1):
    """
    Runs a test point from the testcenter library functions
    
    Parameters
    ----------
    command_name : str
        In the form InterfaceName.TestName
    command_params : iterable object
        List of parameter strings to be passed to the test function    
        
    Returns
    -------
    test_response : str
        String returned from test function. This varies based on the TestPoint spec    

    """

    caller = getframeinfo(stack()[stack_level][0])

    # Write the command and params to STDOUT
    sys.stdout.write("TEST," + str(caller.filename) + "," + str(caller.lineno) + "," + command_name + ",")
    for x in command_params:
        sys.stdout.write("\"" + x + "\"" + ",")

    sys.stdout.write("\n")
    sys.stdout.flush()

    # Read the response from STDIN as the test response
    return sys.stdin.readline().strip()


def endTest(stack_level=1):
    """
    Orders the end of the test.  This will terminate the test parser and disponse of any resources
    held by the test libraries (including quarch module connections)      

    """

    caller = getframeinfo(stack()[stack_level][0])

    sys.stdout.write("ENDTEST," + str(caller.filename) + "," + str(caller.lineno))
    sys.stdout.write("\n")
    sys.stdout.flush()


def beginTestBlock(message_text, stack_level=1):
    """
    Notes the start of a block of tests.  This allows multiple nested layers of related tests
    to improve readability of the results.  This has no effect on the test execution, only
    on the reporting of the results.
    
    Parameters
    ----------
    message_text : str
        User message describing the test block.  This will be shown in the results    
        
    Returns
    -------
    test_response : str
        String returned from test function. This will be "1" on success and "0" on error     
            
    """

    caller = getframeinfo(stack()[stack_level][0])

    # Write the command and params to STDOUT
    sys.stdout.write(
        "BLOCK_START," + str(caller.filename) + "," + str(caller.lineno) + "," + "\"" + message_text + "\"")
    sys.stdout.write("\n")
    sys.stdout.flush()

    # Read the response from STDIN
    return sys.stdin.readline().strip()


def endTestBlock(stack_level=1):
    """
    Notes the end of a block of tests.  This allows multiple nested layers of related tests
    to improve readability of the results.  This has no effect on the test execution, only
    on the reporting of the results. 

    Returns
    -------
    test_response : str
        String returned from test function. This will be "1" on success and "0" on error      
            
    """

    caller = getframeinfo(stack()[stack_level][0])

    # Write the command and params to STDOUT
    sys.stdout.write("BLOCK_END," + str(caller.filename) + "," + str(caller.lineno) + "," + "\"")
    sys.stdout.write("\n")
    sys.stdout.flush()

    # Read the response from STDIN
    return sys.stdin.readline().strip()


def GetVariable(package: str, var_name: str) -> str:
    """
    Access a TestCenter user variable and return its value.

    Args:
        package: Name of the TestCenter package to access. UNUSED
        var_name: Name of the string variable to return.

    Returns:
        The text of the stored variable.
    """

    # Get caller file and line number
    caller = getframeinfo(stack()[stack_level][0])

    # Write the command and params to STDOUT
    print(f"GET_VARIABLE,{str(caller.filename)},{str(caller.lineno)},{var_name}")

    # Read the response from STDIN
    response = sys.stdin.readline().strip()

    return response
