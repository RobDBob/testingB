import pandas_ta as ta
from newAttempt import HQBrain

class SignalTrigger:
    def __init__(self, data_holder: HQBrain, logger) -> None:
        self.data_holder = data_holder
        self.logger = logger

    def _return_result(self, test_name, test_result):
        if test_result:
            self.logger.info(f"{self.data_holder.current_datetime}: {test_name} TRIGGERED")
            return True
        return False

    def check_bbvol(self):
        length = 18
        std = 2
        bbvol_df = ta.bbands(self.data_holder.df["volume"], length=length, std=std)
        test_result = bbvol_df.tail(1)[f"BBP_{length}_{std}.0"].values[0] > 1
        return self._return_result("BBVOL", test_result)

    def check_macd_asmode(self):
        # MACDAS_12_26_9  MACDASh_12_26_9  MACDASs_12_26_9  MACDASh_12_26_9_XA_0  MACDASh_12_26_9_XB_0  MACDAS_12_26_9_A_0
        macd_df = ta.macd(self.data_holder.df.close, signal_indicators=True, asmode=True)
        test_result = macd_df.tail(1)["MACDASh_12_26_9_XA_0"].values[0] > 0
        return self._return_result("MACDASMODE", test_result)