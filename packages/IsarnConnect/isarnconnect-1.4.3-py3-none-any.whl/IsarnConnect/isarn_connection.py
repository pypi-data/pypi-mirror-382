from datetime import datetime

from pandas import DataFrame
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from IsarnConnect.DatabaseType import DatabaseType
from IsarnConnect.Meter import Meter
from IsarnConnect.RowArray import RowArray
from IsarnConnect.db.ELS import Base as ELSBase, ELS
from IsarnConnect.db.LGZ import Base as LGZBase, LGZ
from IsarnConnect.db.SLB import Base as SLBBase, SLB

from typing import Union, List, Type

from IsarnConnect.meters import Row
from IsarnConnect.methods import tableRowToRowArray


class IsarnConnection:
    def __init__(self, password, username, address, port, database, database_type):
        self.username = username
        self.password = password
        self.address = address
        self.port = port
        self.database = database
        if database_type == DatabaseType.POSTGRE:
            self.engine = create_engine(
                'postgresql+psycopg2://' + username + ':' + password + '@' + address + ':' + port +
                '/' + database, echo=False)
        elif database_type == DatabaseType.MYSQL:
            self.engine = create_engine(
                'mysql+mysqlconnector://' + username + ':' + password + '@' + address + ':' + port +
                '/' + database, echo=False)
        self.session = sessionmaker(bind=self.engine)

    def connect(self):
        ELSBase.metadata.create_all(self.engine, checkfirst=True)
        LGZBase.metadata.create_all(self.engine, checkfirst=True)
        SLBBase.metadata.create_all(self.engine, checkfirst=True)

    def commitOnly(self, row: Union[Row.ELS, Row.LGZ, Row.SLB]):
        session = self.session()
        if isinstance(row, Row.ELS):
            session.add(row.toTableRow())
        elif isinstance(row, Row.LGZ):
            session.add(row.toTableRow())
        elif isinstance(row, Row.SLB):
            session.add(row.toTableRow())
        session.commit()

    def commitAll(self, rows: RowArray):
        session = self.session()
        if rows.meter.value == "els":
            print("els!")
            session.add_all(rows)
        elif rows.meter.value == "lgz":
            print("lgz!")
            session.add_all(rows)
        elif rows.meter.value == "slb":
            print("slb!")
            session.add_all(rows)
        session.commit()

    def getByDate(self, date: datetime, meter: Meter):
        session = self.session()
        date_code = float(date.strftime("%Y%m%d")[2:])
        if meter.value == "els":
            items: List[Type[ELS]] = session.query(ELS).filter_by(c092=date_code).all()
            return tableRowToRowArray(items, Meter.ELS)
        elif meter.value == "lgz":
            items: List[Type[LGZ]] = session.query(LGZ).filter_by(c092=date_code).all()
            return tableRowToRowArray(items, Meter.LGZ)
        elif meter.value == "slb":
            items: List[Type[SLB]] = session.query(SLB).filter_by(c092=date_code).all()
            return tableRowToRowArray(items, Meter.SLB)

    def getByTime(self, time: datetime, meter: Meter):
        session = self.session()
        time_code = float(time.strftime("%H%M%S"))
        if meter.value == "els":
            items = session.query(ELS).filter_by(c091=time_code).all()
            return tableRowToRowArray(items, Meter.ELS)
        elif meter.value == "lgz":
            items = session.query(LGZ).filter_by(c091=time_code).all()
            return tableRowToRowArray(items, Meter.LGZ)
        elif meter.value == "slb":
            items = session.query(SLB).filter_by(c091=time_code).all()
            return tableRowToRowArray(items, Meter.SLB)

    def getByDateTime(self, datetime: datetime, meter: Meter):
        session = self.session()
        condition = (
                (ELS.c092 == 190918) &
                (ELS.c091 == 115759)
        )
        if meter.value == "els":
            item = session.query(ELS).filter(condition).order_by(ELS.c092, ELS.c091).first()
            return item.toRow()
        elif meter.value == "lgz":
            item = session.query(LGZ).filter(condition).order_by(LGZ.c092, LGZ.c091).first()
            return item.toRow()
        elif meter.value == "slb":
            item = session.query(SLB).filter(condition).order_by(SLB.c092, SLB.c091).first()
            return item.toRow()

    def getBetweenDatetime(self, from_date: datetime, to_date: datetime, meter: Meter):
        session = self.session()
        from_date_code = float(from_date.strftime("%Y%m%d")[2:] + "" + from_date.strftime("%H%M%S"))
        to_date_code = float(to_date.strftime("%Y%m%d")[2:] + "" + to_date.strftime("%H%M%S"))
        if meter.value == "els":
            items = (session
                     .query(ELS).filter((ELS.c092 * 1000000 + ELS.c091).between(from_date_code, to_date_code))
                     .order_by(ELS.c092, ELS.c091)
                     .all())
            return tableRowToRowArray(items, Meter.ELS)
        elif meter.value == "lgz":
            items = (session
                     .query(LGZ).filter((ELS.c092 * 1000000 + ELS.c091).between(from_date_code, to_date_code))
                     .order_by(ELS.c092, ELS.c091)
                     .all())
            return tableRowToRowArray(items, Meter.LGZ)
        elif meter.value == "slb":
            items = (session
                     .query(SLB).filter((ELS.c092 * 1000000 + ELS.c091).between(from_date_code, to_date_code))
                     .order_by(ELS.c092, ELS.c091)
                     .all())
            return tableRowToRowArray(items, Meter.SLB)

    def getBetweenTime(self, from_time: datetime, to_time: datetime, meter: Meter):
        session = self.session()
        from_time_code = float(from_time.strftime("%H%M%S"))
        to_time_code = float(to_time.strftime("%H%M%S"))

        if meter.value == "els":
            items = session.query(ELS).filter(ELS.c091.between(from_time_code, to_time_code)).all()
            return tableRowToRowArray(items, Meter.ELS)
        elif meter.value == "lgz":
            items = session.query(LGZ).filter(LGZ.c091.between(from_time_code, to_time_code)).all()
            return tableRowToRowArray(items, Meter.LGZ)
        elif meter.value == "slb":
            items = session.query(SLB).filter(SLB.c091.between(from_time_code, to_time_code)).all()
            return tableRowToRowArray(items, Meter.SLB)

    def getLatest(self, meter: Meter):
        session = self.session()
        if meter.value == "els":
            item = session.query(ELS).order_by(desc(ELS.id)).first()
            return item.toRow()
        elif meter.value == "lgz":
            item = session.query(LGZ).order_by(desc(LGZ.id)).first()
            return item
        elif meter.value == "slb":
            item = session.query(SLB).order_by(desc(SLB.id)).first()
            return item

    def getCombinedForDatetime(self, from_date: datetime, to_date: datetime):
        session = self.session()
        from_date_code = float(from_date.strftime("%Y%m%d")[2:] + "" + from_date.strftime("%H%M%S"))
        to_date_code = float(to_date.strftime("%Y%m%d")[2:] + "" + to_date.strftime("%H%M%S"))
        itemsELS = (session
                    .query(ELS).filter((ELS.c092 * 1000000 + ELS.c091).between(from_date_code, to_date_code))
                    .order_by(ELS.c092, ELS.c091)
                    .all())
        itemsELSDF = DataFrame(tableRowToRowArray(itemsELS, Meter.ELS))
        elsUse = 0
        if not itemsELSDF.empty:
            elsUse = itemsELSDF.iloc[-1][0].c180 - itemsELSDF.iloc[0][0].c180
        itemsLGZ = (session
                    .query(LGZ).filter((LGZ.c092 * 1000000 + LGZ.c091).between(from_date_code, to_date_code))
                    .order_by(LGZ.c092, LGZ.c091)
                    .all())
        itemsLGZDF = DataFrame(tableRowToRowArray(itemsLGZ, Meter.LGZ))
        lgzuse = 0
        if not itemsLGZDF.empty:
            lgzuse = itemsLGZDF.iloc[-1][0].c180 - itemsLGZDF.iloc[0][0].c180
        itemsSLB = (session
                    .query(SLB).filter((SLB.c092 * 1000000 + SLB.c091).between(from_date_code, to_date_code))
                    .order_by(SLB.c092, SLB.c091)
                    .all())
        itemsSLBDF = DataFrame(tableRowToRowArray(itemsSLB, Meter.SLB))
        slbuse = 0
        if not itemsSLBDF.empty:
            slbuse = itemsSLBDF.iloc[-1][0].c180 - itemsSLBDF.iloc[0][0].c180
        return elsUse + lgzuse + slbuse
