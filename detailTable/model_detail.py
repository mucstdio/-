from detailTable.exts_detail import db


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields


class Information(db.Model, EntityBase):
    # 数据表明、字段
    __tablename__ = 'detail'

    buildname = db.Column(db.String(80), primary_key=True)
    roomid = db.Column(db.Integer, primary_key=True)
    campus = db.Column(db.String(80))
    roomname = db.Column(db.String(80))
    areaBuild = db.Column(db.Float)
    areaUse = db.Column(db.Float)
    purpose = db.Column(db.String(80))
    classify = db.Column(db.String(80))
    userid = db.Column(db.Integer)
    username = db.Column(db.String(120))
    roomstate = db.Column(db.String(80))
    notes = db.Column(db.String(310))
    department = db.Column(db.String(80))
    # department = db.Column(db.String(80), unique=True)


class Basic1(db.Model, EntityBase):
    __tablename__ = 'build_information'

    campus = db.Column(db.String(30))
    buildid = db.Column(db.String(30), primary_key=True)
    buildname = db.Column(db.String(60))
    buildvalue = db.Column(db.Integer)
    locate = db.Column(db.String(101))
    acquisitiondata = db.Column(db.String(20))
    yearbuilt = db.Column(db.Integer)
    areacover = db.Column(db.Float)
    areabuild = db.Column(db.Float)
    areause = db.Column(db.Float)
    areabuildabove = db.Column(db.Float)
    areabuildunder = db.Column(db.Float)
    floorabove = db.Column(db.Float)
    floorunder = db.Column(db.Float)
    height = db.Column(db.Float)
    purpose = db.Column(db.String(50))
    propertyform = db.Column(db.String(10))
    ownershipcertificate = db.Column(db.String(10))
    buildstructure = db.Column(db.String(20))
    ownershipnature = db.Column(db.String(10))
    propertyid = db.Column(db.String(20))
    acquisitionmethod = db.Column(db.String(20))
    usecoefficient = db.Column(db.FLOAT)
    funccategory = db.Column(db.String(60))
    arealeased = db.Column(db.Float)


class Basic2(db.Model, EntityBase):
    __tablename__ = 'build_department'

    departmentid = db.Column(db.String(22), primary_key=True)
    departmentname = db.Column(db.String(60))

class Dictionary1(db.Model, EntityBase):
    __tablename__ = 'build_purpose'

    purposeid = db.Column(db.String(12), primary_key=True)
    purposename = db.Column(db.String(50))
