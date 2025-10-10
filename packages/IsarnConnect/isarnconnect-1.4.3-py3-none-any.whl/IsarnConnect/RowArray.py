from typing import Union, List

from IsarnConnect.Meter import Meter
from IsarnConnect.meters import Row


class RowArray:
    def __init__(self, meter: Meter):
        self.elements = []
        self.meter = meter

    def addList(self, list: Union[List[Row.ELS], List[Row.SLB], List[Row.LGZ]]):
        for row in list:
            self.elements.append(row.toTableRow())

    def append(self, row: Union[Row.ELS, Row.LGZ, Row.SLB]):
        if isinstance(row, Row.ELS) and self.meter.value == "els":
            self.elements.append(row.toTableRow())
        elif isinstance(row, Row.LGZ) and self.meter == "lgz":
            self.elements.append(row.toTableRow())
        elif isinstance(row, Row.SLB) and self.meter == "slb":
            self.elements.append(row.toTableRow())

    def pop(self, index):
        self.elements.pop(index)

    def remove(self, row):
        self.elements.remove(row.toTableRow())

    def __str__(self):
        return str(self.elements)

    def __iter__(self):
        return iter(self.elements)

    def asList(self):
        list = []
        for row in self.elements:
            list.append(row.toRow())
        return list
