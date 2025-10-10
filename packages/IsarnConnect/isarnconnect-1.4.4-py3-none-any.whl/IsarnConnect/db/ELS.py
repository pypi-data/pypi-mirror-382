from sqlalchemy import Double, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column

from IsarnConnect.meters import Row

Base = declarative_base()


class ELS(Base):
    __tablename__ = 'ELS_data'
    __table_args__ = {'schema': 'public'} # TODO reorganize Development Stage!
    id = mapped_column("id", Integer, autoincrement=True, primary_key=True)
    c091 = mapped_column("0.9.1", Double)
    c092 = mapped_column("0.9.2", Double)
    c010 = mapped_column("0.1.0", Double)
    c120 = mapped_column("1.2.0", Double)
    c150 = mapped_column("1.5.0", Double)
    c160 = mapped_column("1.6.0", Double)
    c220 = mapped_column("2.2.0", Double)
    c250 = mapped_column("2.5.0", Double)
    c260 = mapped_column("2.6.0", Double)
    c180 = mapped_column("1.8.0", Double)
    c280 = mapped_column("2.8.0", Double)
    c580 = mapped_column("5.9.0", Double)
    c680 = mapped_column("6.8.0", Double)
    c780 = mapped_column("7.8.0", Double)
    c880 = mapped_column("8.8.0", Double)
    c030 = mapped_column("0.3.0", Double)
    c033 = mapped_column("0.3.3", Double)

    def __str__(self):
        return {"c091": self.c091, "c092": self.c092, "c010": self.c010, "c120": self.c120, "c150": self.c150,
                "c160": self.c160, "c220": self.c220, "c250": self.c250, "c260": self.c260, "c180": self.c180,
                "c280": self.c280, "c580": self.c580, "c680": self.c680, "c780": self.c780, "c880": self.c880,
                "c030": self.c030, "c033": self.c033}.__str__()

    def toRow(self):
        return Row.ELS(c091=self.c091, c092=self.c092, c010=self.c010, c120=self.c120, c150=self.c150, c160=self.c160,
                       c220=self.c220, c250=self.c250, c260=self.c260, c180=self.c180*60, c280=self.c280*60, c580=self.c580,
                       c680=self.c680, c780=self.c780, c880=self.c880, c030=self.c030, c033=self.c033)