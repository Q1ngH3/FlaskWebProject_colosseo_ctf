from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session,sessionmaker


Base = automap_base()
# 测试已经说明利用这种方式可以将所有表中的属性
# 以！！self.xxx！！的形式得到，即储存在这个类之后生成的实例中
class Question(Base):
    __tablename__ = 'general_questions'

    def __init__(self):
        pass
    def get_flag(self):
        return self.flag

    def to_dict(self):
        d = {}
        d['sequence'] = self.sequence
        d['name'] = self.name

        return d
    """description of class"""

# reflect
engine_q = create_engine('mysql+mysqlconnector://remoteuser:password@192.168.80.144:3306/questions',
echo = True)
Base.prepare(engine_q, reflect=True)
#注册机制
session_factory = sessionmaker(bind=engine_q)
Session = scoped_session(session_factory)
session_test = Session()


#test
q1 = session_test.query(Question).first()
print (q1.to_dict())
