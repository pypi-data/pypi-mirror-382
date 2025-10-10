import csv
import re
from typing import List, Type

from typing_extensions import Union

from IsarnConnect.Meter import Meter
from IsarnConnect.RowArray import RowArray
from IsarnConnect.db.ELS import ELS
from IsarnConnect.db.LGZ import LGZ
from IsarnConnect.db.SLB import SLB
from IsarnConnect.meters import Row


def ablToRow(path):
    with open(path) as file:
        readfile = file.read()
        datalist = []

        while re.search("\d\.\d\.\d\(\d+\.?\d*(\*[a-zA-Z]*)?\)", readfile):
            span = re.search("\d\.\d\.\d\(\d+\.?\d*(\*[a-zA-Z]*)?\)", readfile).span()
            match = re.search("\d\.\d\.\d\(\d+\.?\d*(\*[a-zA-Z]*)?\)", readfile).group()
            datalist.append(match)
            readfile = readfile[span[1]:]

        entries = []

        for string in datalist:
            entry = float(
                string[6:-1].replace("*kW", "").replace("h", "").replace("*kvarh", "").replace("*kvar", "").replace(
                    "*V", "").replace("*A", ""))
            entries.append(entry)

        meter = file.name.split("/")[-1][1:4]
        if meter == "ELS":
            row = Row.ELS(entries[0], entries[1], entries[2], entries[3], entries[4], entries[5], entries[6],
                          entries[7], entries[8], entries[9], entries[10], entries[11], entries[12], entries[13],
                          entries[14], entries[15], entries[16])
            return row
        elif meter == "LGZ":
            row = Row.LGZ(entries[0], entries[1], entries[2], entries[3], entries[4], entries[5], entries[6],
                          entries[7], entries[8], entries[9], entries[10], entries[11], entries[12], entries[13],
                          entries[14], entries[15], entries[16], entries[17], entries[18], entries[19], entries[20])
            return row
        elif meter == "SLB":
            row = Row.SLB(entries[0], entries[1], entries[2], entries[3], entries[4], entries[5], entries[6],
                          entries[7], entries[8], entries[9], entries[10], entries[11], entries[12], entries[13],
                          entries[14], entries[15], entries[16], entries[17], entries[18], entries[19], entries[20],
                          entries[21], entries[22], entries[23], entries[24], entries[25], entries[26], entries[27],
                          entries[28], entries[29])
            return row


def csvToRowArray(path, meter: Meter):
    with open(path) as file:
        reader = csv.DictReader(file)
        array = RowArray(meter)
        if meter.value == "els":
            for row in reader:
                array_row = Row.ELS(c091=float(row['0.9.1']), c092=float(row['0.9.2']), c010=float(row['0.1.0']),
                                    c120=float(row['1.2.0'].replace("*kW", "")),
                                    c150=float(row['1.5.0'].replace("*kW", "")), c160=float(row['1.6.0']),
                                    c220=float(row['2.2.0'].replace("*kW", "")),
                                    c250=float(row['2.5.0'].replace("*kW", "")), c260=float(row['2.6.0']),
                                    c180=float(row['1.8.0']), c280=float(row['2.8.0']), c580=float(row['5.8.0']),
                                    c680=float(row['6.8.0']), c780=float(row['7.8.0'].replace("None", "00000.000")),
                                    c880=float(row['8.8.0'].replace("None", "00000.000")),
                                    c030=float(row['0.3.0'].replace("None", "00000.000")),
                                    c033=float(row['0.3.3'].replace("None", "00000.000")))
                array.append(array_row)
            return array
        elif meter.value == "lgz":
            for row in reader:
                array_row = Row.LGZ(c091=float(row['0.9.1']), c092=float(row['0.9.2']), c010=float(row['0.1.0']),
                                    c150=float(row['1.5.0'].replace("*kW", "")),
                                    c160=float(row['1.6.0'].replace("*kW", "")),
                                    c180=float(row['1.8.0'].replace("*kWh", "")),
                                    c250=float(row['2.5.0'].replace("*kW", "")),
                                    c260=float(row['2.6.0'].replace("*kW", "")),
                                    c280=float(row['2.8.0'].replace("*kWh", "")),
                                    c580=float(row['5.8.0'].replace("*kvarh", "")),
                                    c680=float(row['6.8.0'].replace("*kvarh", "")),
                                    c780=float(row['7.8.0'].replace("*kvarh", "")),
                                    c880=float(row['8.8.0'].replace("*kvarh", "")),
                                    c021=float(row['0.2.1']),
                                    c2700=float(row['2.7.0'].replace("*V", "")),
                                    c2701=float(row['2.7.0'].replace("*V", "")),
                                    c2702=float(row['2.7.0'].replace("*V", "")),
                                    c1700=float(row['1.7.0'].replace("*A", "")),
                                    c1701=float(row['1.7.0'].replace("*A", "")),
                                    c1702=float(row['1.7.0'].replace("*A", "")),
                                    c512=float(row['5.1.2'].replace("*kW", "")))
                array.append(array_row)
            return array
        elif meter.value == "slb":
            for row in reader:
                array_row = Row.SLB(c000=float(row['0.0.0']), c001=float(row['0.0.1']), c002=float(row['0.0.2']),
                                    c003=float(row['0.0.3']), c010=float(row['0.1.0']), c091=float(row['0.9.1']),
                                    c092=float(row['0.9.2']), c121=float(row['1.2.1']), c122=float(row['1.2.2']),
                                    c141=float(row['1.4.1']), c142=float(row['1.4.2']), c151=float(row['1.5.1']),
                                    c152=float(row['1.5.2']), c161=float(row['1.6.1']), c162=float(row['1.6.2']),
                                    c180=float(row['1.8.0']), c181=float(row['1.8.1']), c182=float(row['1.8.2']),
                                    c183=float(row['1.8.3']), c184=float(row['1.8.4']), c580=float(row['5.8.0']),
                                    c581=float(row['5.8.1']), c582=float(row['5.8.2']), c583=float(row['5.8.3']),
                                    c584=float(row['5.8.4']), c880=float(row['8.8.0']), c881=float(row['8.8.1']),
                                    c882=float(row['8.8.2']), c883=float(row['8.8.3']), c884=float(row['8.8.4']))
                array.append(array_row)
            return array


def tableRowToRowArray(rows: Union[List[Type[ELS]], List[Type[LGZ]], List[Type[SLB]]], meter: Meter):
    array = RowArray(meter)
    for row in rows:
        array.append(row.toRow())
    return array