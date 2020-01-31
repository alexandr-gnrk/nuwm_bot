from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///users.db', 
	echo=False, 
	connect_args={'check_same_thread': False})
Base = declarative_base()
Base.metadata.create_all(engine)

session = sessionmaker(bind=engine)()


class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True)
    group_name = Column(String)

    def __repr__(self):
       return "<User(user_id='%s', group_name='%s')>" % (
                            self.user_id, self.group_name)


def get_user_by_id(user_id):
    """Return User object from database."""
    return session.query(User).\
        filter(User.user_id == user_id).\
        first()


def create_user(user_id, group_name):
    """Create user in database."""
    user = User(user_id=user_id, group_name=None)
    session.add(user)
    session.commit()
    return user
