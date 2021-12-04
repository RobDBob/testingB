# Cosmos DB Python sample

Customize the [config.py](./config.py) file with your account host and key.


Notes

PEAKS:
>>> df['max'] = df.v[(df.v.shift(1) < df.v) & (df.v.shift(-1) < df.v)]
>>> df['min'] = df.v[(df.v.shift(1) > df.v) & (df.v.shift(-1) > df.v)]

df["vEMAPctChange"]=ta.ema(df.v, length=10).pct_change(periods=3)



PCT CHANGE ON VOLUME > 70 IRISUSDT
1638476630000	2021-12-02 20:23:50	0.1205	0.1207	-0.2	-0.4757	5491.8		-0.2	3.5701667089462585
1638476735000	2021-12-02 20:25:35	0.1205	0.1226	173077.2	21861.9673	207.0	173077.2		78.57523908245088
1638476736000	2021-12-02 20:25:36	0.1202	0.1226	0.2	-0.0327	207.0			8.534851813766926



df.loc[df.v<0, "v"]=0

from Helpers import DBFunctions
from Helpers import PandaFunctions
r=DBFunctions.get_records_after_timestamp(0, "ticker_cosusdt")
df=PandaFunctions.get_df_from_records(r, ["timeStamp", "c", "v"], setIndex=True)
df["vEMAPctChange"]=df.v.pct_change(periods=100)
df.to_csv("PEAKS.csv")


>>> df["vPctChange"]=df.v.pct_change(periods=2)
>>> df.to_csv("PEAKS.csv")