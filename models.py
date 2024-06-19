from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

# Every table in the database will have its corresponding model
class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False)
    # Make sure to hash the password before saving it
    password = Column(String(80), unique=False, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password
        }

    def __repr__(self):
        return '<User %r>' % self.username