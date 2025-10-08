# //////////////////////////////////////////////////////////////////////////////
class DebugLogger:
    """Debug logger class to log messages to a file.
    It creates a log file at the specified path and appends messages to it.
    Example:
        from prisma.utils import Debug;
        d = Debug("logs/name.log")
        d.log("Some value:", value)
    """
    def __init__(self, path: str):
        import datetime
        self.path = path
        with open(self.path, 'w') as file:
            file.write(f"{datetime.datetime.now()}\n\n")

    # --------------------------------------------------------------------------
    def log(self, *values, sep = ' ', end = '\n'):
        """Log values to the debug file.
        Args:
            *values: Values to log.
            sep (str): Separator between values. Default is a space.
            end (str): String appended after the last value. Default is a newline.
        """
        text = sep.join(map(str, values))
        with open(self.path, 'a') as file:
            file.write(text + end)


# //////////////////////////////////////////////////////////////////////////////
