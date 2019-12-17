class SafeUtilsPreviousOwnerNotFound(Exception):
    """ SafeUtilsPreviousOwnerNotFound
    Raised when the SafeUtils is unable to perform proper operations while trying to find a previous owner
    :param console_type
    :param _err
    :param _trace
    :return SafeUtilsPreviousOwnerNotFound Exception Message
    """
    def __init__(self, console_type, _err, _trace, *args):
        self.name = self.__class__.__name__
        self.console_type = console_type
        self.err = _err
        self.trace = _trace
        self.message = '{0}, in  {1} Unable to perform proper operations: [ {2} ]'.format(self.name, console_type, _err)
        super(SafeUtilsPreviousOwnerNotFound, self).__init__(self.message, _err, console_type, *args)
