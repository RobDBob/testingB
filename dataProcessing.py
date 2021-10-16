import json


def load_binance_from_file():
    with open("new_file.json", mode="r") as file_handler:
        prices = json.loads(file_handler.read())
    print(len(prices))
    ETHBTC = [[l for l in k if l["s"] == "ETHBTC"] for k in prices]
    print(ETHBTC)

def test():
    data = {   # `dict` is a bad name
    "name": "John",
    "age": 30,
    }

    with open("txt_file.txt", 'w') as fout :
        json.dump(data, fout) 

    with open("txt_file.txt") as fin :
        print(json.loads(fin.read()))

if __name__ == "__main__":
    load_binance_from_file()
    # test()
