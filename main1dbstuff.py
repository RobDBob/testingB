from CleanFunctions import ToKeep
from datetime import datetime
import json


def readFromFile(filePath):
    with open(filePath, "r") as fp:
        return json.loads(fp.read())

def saveToFile(results, filePath):
    with open(filePath, "w") as fp:
        json.dump(results, fp)

def saveToFileCSV(results, filePath):
    """
    Save data in TA format
    `Timestamp`, `Open`, `High`, `Low`, `Close` and `Volume` columns.
    """
    import csv
    with open(filePath, "w", newline='') as fp:
        csvriter = csv.writer(fp, delimiter=',')
        csvriter.writerow(["Timestamp","DateTime","Open","High","Low","Close"])
        for record in results:
            csvriter.writerow([
                record["id"],
                datetime.utcfromtimestamp((int(record["id"])/1000)+3600).strftime('%Y-%m-%d %H:%M:%S'),
                record["openPrice"],
                record["highPrice"],
                record["lowPrice"],
                record["lastPrice"]])


def convertStampsIntoDates(filePathFrom, filePathTo):
    data = readFromFile(filePathFrom)
    for idata in data:
        timeStamp = idata["closeTime"]
        idata["closeTime"] = datetime.utcfromtimestamp((timeStamp/1000)+3600).strftime('%Y-%m-%d %H:%M:%S')
    saveToFile(data, filePathTo)


if __name__ == "__main__":
    results = ToKeep.get_last_records(minutesBack=24*60)
    # saveToFileCSV(results, "testDataTA.csv")
    # results = readFromFile("last3HoursData.json")
    saveToFile(results, "last24HData.json")
    # playground.printResults(results)
    # convertStampsIntoDates("last5MinutesData.json", "last5MinutesDataReadable.json")