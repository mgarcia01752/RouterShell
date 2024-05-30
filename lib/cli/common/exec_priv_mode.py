from enum import Enum, auto

class ExecMode(Enum):
    '''Command Line Execute Mode'''

    USER_MODE = auto()
    ''' 
        Prompt: Router>
        
        User EXEC Mode (User Mode): This is the lower privilege level of EXEC Mode. In User EXEC Mode, users have 
        limited access to basic monitoring and operational commands. The primary purpose of User EXEC Mode is to 
        view information about the device's status, perform basic connectivity tests, and access some diagnostic tools. 
        The prompt for User EXEC Mode is typically shown as Router>. In this mode, users can issue 
        one-word commands like show, ping, or telnet to gather information and perform basic tasks 
        without making configuration changes.
    '''
    PRIV_MODE = auto()
    ''' 
        Prompt: Router#
    
        Privileged EXEC Mode (Privileged Mode): This provides users with full control over the device. 
        In this mode, users can execute all router or switch commands, including configuration, troubleshooting, 
        and system management tasks. The prompt for Privileged EXEC Mode is typically shown as "Router#". 
        Users can enter Privileged Mode from User EXEC Mode by using the "enable" command, provided they have 
        the appropriate credentials (usually a password or authentication method). 
        Once in Privileged Mode, users can access and configure the device's settings, 
        view detailed status information, and make changes to the configuration.
    
    '''

    CONFIG_MODE = auto()
    ''' 
        Prompt: Router(config)#
        
        Allows configuration of global parameters on the device,
        such as setting the hostname, configuring interfaces, and setting up routing protocols.
        Accessed from Privileged EXEC mode using the configure terminal or conf t command.
    '''

class ExecException(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)