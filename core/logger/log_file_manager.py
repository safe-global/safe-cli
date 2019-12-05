class LogFileManager:
    """ Log File Manager
    This class will create the log files if does not exist
    """
    def __init__(self):
        self.gnosis_log = './log/general_console.log'
        self.contract_log = './log/contract_console.log'
        self.safe_log = './log/safe_console.log'

    def create_log_files(self):
        """ Create Log Files

        """
        try:
            open(self.gnosis_log, 'r')
            open(self.contract_log, 'r')
            open(self.safe_log, 'r')
        except IOError:
            open(self.gnosis_log, 'w')
            open(self.contract_log, 'w')
            open(self.safe_log, 'w')
