from catwalk_client.common.logger import init_logger

log = init_logger()


class CatwalkClientException(Exception):
    def __init__(self, reason: str, **extra):
        log.error(reason)
        log.debug(extra)
        log.debug(self.__traceback__)

        self.reason = reason
        [self.__setattr__(name, value) for name, value in extra.items()]
