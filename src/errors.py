class TwitchCLIError(Exception):
    pass

class TwitchAPIError(TwitchCLIError):
    pass

class TwitchAPIUnauthenticatedError(TwitchAPIError):
    pass
