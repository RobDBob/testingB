import atexit

class PriceCheckSession:
    initial_trend_increasing = None
    is_trend_increasing = None

    def __init__(self, logger, start_time):
        self.logger = logger
        self.session_started(start_time)

    def session_to_close(self):
        self.logger.info("--=== SESSION ENDED ===--")

    def session_started(self, start_time):
        self.logger.info(f"{start_time}: SESSION STARTED")


    # @property
    # def trend_known(self):
    #     return self.trend_known