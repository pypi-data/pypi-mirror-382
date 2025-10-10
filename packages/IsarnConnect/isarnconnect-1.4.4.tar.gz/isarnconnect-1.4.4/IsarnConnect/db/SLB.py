from sqlalchemy import Double, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column

from IsarnConnect.meters import Row

Base = declarative_base()


class SLB(Base):
    __tablename__ = 'SLB_data'
    __table_args__ = {'schema': 'public'} # TODO reorganize Development Stage!
    id = mapped_column("id", Integer, autoincrement=True, primary_key=True)
    c000 = mapped_column("0.0.0", Double)
    c001 = mapped_column("0.0.1", Double)
    c002 = mapped_column("0.0.2", Double)
    c003 = mapped_column("0.0.3", Double)
    c010 = mapped_column("0.1.0", Double)
    c091 = mapped_column("0.9.1", Double)
    c092 = mapped_column("0.9.2", Double)
    c121 = mapped_column("1.2.1", Double)
    c122 = mapped_column("1.2.2", Double)
    c141 = mapped_column("1.4.1", Double)
    c142 = mapped_column("1.4.2", Double)
    c151 = mapped_column("1.5.1", Double)
    c152 = mapped_column("1.5.2", Double)
    c161 = mapped_column("1.6.1", Double)
    c162 = mapped_column("1.6.2", Double)
    c180 = mapped_column("1.8.0", Double)
    c181 = mapped_column("1.8.1", Double)
    c182 = mapped_column("1.8.2", Double)
    c183 = mapped_column("1.8.3", Double)
    c184 = mapped_column("1.8.4", Double)
    c580 = mapped_column("5.8.0", Double)
    c581 = mapped_column("5.8.1", Double)
    c582 = mapped_column("5.8.2", Double)
    c583 = mapped_column("5.8.3", Double)
    c584 = mapped_column("5.8.4", Double)
    c880 = mapped_column("8.8.0", Double)
    c881 = mapped_column("8.8.1", Double)
    c882 = mapped_column("8.8.2", Double)
    c883 = mapped_column("8.8.3", Double)
    c884 = mapped_column("8.8.4", Double)

    def __str__(self):
        return ({"c000": self.c000, "c001": self.c001, "c002": self.c002, "c003": self.c003, "c010": self.c010,
                "c091": self.c091, "c092": self.c092, "c121": self.c121, "c122": self.c122, "c141": self.c141,
                "c142": self.c142, "c151": self.c151, "c152": self.c152, "c161": self.c161, "c162": self.c162,
                "c180": self.c180, "c181": self.c181, "c182": self.c182, "c183": self.c183, "c184": self.c184,
                "c580": self.c580, "c581": self.c581, "c582": self.c582, "c583": self.c583, "c584": self.c584,
                "c880": self.c880, "c881": self.c881, "c882": self.c882, "c883": self.c883, "c884": self.c884}
                .__str__())

    def toRow(self):
        return Row.SLB(c000= self.c000, c001= self.c001, c002= self.c002, c003= self.c003, c010=self.c010,
                       c091= self.c091, c092= self.c092, c121= self.c121, c122= self.c122, c141=self.c141,
                       c142= self.c142, c151= self.c151, c152= self.c152, c161= self.c161, c162= self.c162,
                       c180= self.c180, c181= self.c181, c182= self.c182, c183= self.c183, c184= self.c184,
                       c580= self.c580, c581= self.c581, c582= self.c582, c583= self.c583, c584= self.c584,
                       c880= self.c880, c881= self.c881, c882= self.c882, c883= self.c883, c884= self.c884)