from IsarnConnect.db.ELS import ELS as elsRow
from IsarnConnect.db.LGZ import LGZ as lgzRow
from IsarnConnect.db.SLB import SLB as slbRow


class ELS:

    def __init__(self, c091: float, c092: float, c010: float, c120: float, c150: float, c160: float, c220: float,
                 c250: float, c260: float, c180: float, c280: float, c580: float, c680: float, c780: float, c880: float,
                 c030: float, c033: float):
        self.c091 = c091
        self.c092 = c092
        self.c010 = c010
        self.c120 = c120
        self.c150 = c150
        self.c160 = c160
        self.c220 = c220
        self.c250 = c250
        self.c260 = c260
        self.c180 = c180
        self.c280 = c280
        self.c580 = c580
        self.c680 = c680
        self.c780 = c780
        self.c880 = c880
        self.c030 = c030
        self.c033 = c033

    def __str__(self):
        return {"c091": self.c091, "c092": self.c092, "c010": self.c010, "c120": self.c120, "c150": self.c150,
                "c160": self.c160, "c220": self.c220, "c250": self.c250, "c260": self.c260, "c180": self.c180,
                "c280": self.c280, "c580": self.c580, "c680": self.c680, "c780": self.c780, "c880": self.c880,
                "c030": self.c030, "c033": self.c033}.__str__()
    def toTableRow(self):
        return elsRow(c091=self.c091, c092=self.c092, c010=self.c010, c120=self.c120, c150=self.c150, c160=self.c160,
                      c220=self.c220, c250=self.c250, c260=self.c260, c180=self.c180, c280=self.c280, c580=self.c580,
                      c680=self.c680, c780=self.c780, c880=self.c880, c030=self.c030, c033=self.c033)


class LGZ:
    def __init__(self, c091: float, c092: float, c010: float, c150: float, c160: float, c180: float, c250: float,
                 c260: float, c280: float, c580: float, c680: float, c780: float, c880: float, c021: float,
                 c2700: float, c2701: float, c2702: float, c1700: float, c1701: float, c1702: float, c512: float):
        self.c091 = c091
        self.c092 = c092
        self.c010 = c010
        self.c150 = c150
        self.c160 = c160
        self.c180 = c180
        self.c250 = c250
        self.c260 = c260
        self.c280 = c280
        self.c580 = c580
        self.c680 = c680
        self.c780 = c780
        self.c880 = c880
        self.c021 = c021
        self.c2700 = c2700
        self.c2701 = c2701
        self.c2702 = c2702
        self.c1700 = c1700
        self.c1701 = c1701
        self.c1702 = c1702
        self.c512 = c512

    def toTableRow(self):
        return lgzRow(c091=self.c091, c092=self.c092, c010=self.c010, c150=self.c150, c160=self.c160, c180=self.c180,
                      c250=self.c250, c260=self.c260, c280=self.c280, c580=self.c580, c680=self.c680, c780=self.c780,
                      c880=self.c880, c021=self.c021, c2700=self.c2700, c2701=self.c2701, c2702=self.c2702,
                      c1700=self.c1700, c1701=self.c1701, c1702=self.c1702, c512=self.c512)


class SLB:
    def __init__(self, c000: float, c001: float, c002: float, c003: float, c010: float, c091: float, c092: float,
                 c121: float, c122: float, c141: float, c142: float, c151: float, c152: float, c161: float, c162: float,
                 c180: float, c181: float, c182: float, c183: float, c184: float, c580: float, c581: float, c582: float,
                 c583: float, c584: float, c880: float, c881: float, c882: float, c883: float, c884: float):
        self.c000 = c000
        self.c001 = c001
        self.c002 = c002
        self.c003 = c003
        self.c010 = c010
        self.c091 = c091
        self.c092 = c092
        self.c121 = c121
        self.c122 = c122
        self.c141 = c141
        self.c142 = c142
        self.c151 = c151
        self.c152 = c152
        self.c161 = c161
        self.c162 = c162
        self.c180 = c180
        self.c181 = c181
        self.c182 = c182
        self.c183 = c183
        self.c184 = c184
        self.c580 = c580
        self.c581 = c581
        self.c582 = c582
        self.c583 = c583
        self.c584 = c584
        self.c880 = c880
        self.c881 = c881
        self.c882 = c882
        self.c883 = c883
        self.c884 = c884

    def toTableRow(self):
        return slbRow(c000=self.c000, c001=self.c001, c002=self.c002, c003=self.c003, c010=self.c010, c091=self.c091,
                      c092=self.c092, c121=self.c121, c122=self.c122, c141=self.c141, c142=self.c142, c151=self.c151,
                      c152=self.c152, c161=self.c161, c162=self.c162, c180=self.c180, c181=self.c181, c182=self.c182,
                      c183=self.c183, c184=self.c184, c580=self.c580, c581=self.c581, c582=self.c582, c583=self.c583,
                      c584=self.c584, c880=self.c880, c881=self.c881, c882=self.c882, c883=self.c883, c884=self.c884)