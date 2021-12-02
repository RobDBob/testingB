import matplotlib.pyplot as plt

def plot_data(df, price_df):
    df.to_pickle("pickle.pkl")
    df.reset_index(inplace=True)

    
    mx=df.plot(x="timeStamp", y="close", c="orange")
    ax=price_df.plot.scatter(x="timeStamp", y="bought", c="red", ax=mx)
    for i, txt in enumerate(price_df.bought):
        ax.annotate(txt, (price_df.timeStamp.iat[i], price_df.bought.iat[i]))

    bx=price_df.plot.scatter(x="timeStamp", y="sold", c="green", ax=mx)
    for i, txt in enumerate(price_df.sold):
        bx.annotate(txt, (price_df.timeStamp.iat[i], price_df.sold.iat[i]))

    plt.show()