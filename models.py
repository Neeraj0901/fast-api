from db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'user'
    id= Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    profile = Column(String(100))
    gender = Column(String(100))
    gender1 = Column(String(100))
    item_data  = relationship("Item", back_populates='user_data')
    
    def __repr__(self):
        return f"user -name {self.name}"

class Item(Base):
    __tablename__ = 'item'
    id= Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    price = Column(Integer())
    user_id = Column(Integer, ForeignKey('user.id'))
    user_data = relationship("User", back_populates="item_data")
  
    def __repr__(self):
        return f"item -name {self.name}"
    


#this is for many to many
assosiate_table = Table('cutomer-product', 
                        Base.metadata, 
                        Column('customer_id', ForeignKey('cutomer.id')),
                        Column('product_id', ForeignKey('product.id')))

class Customer(Base):
    __tablename__ = 'cutomer'
    id= Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    product_data = relationship('Product', secondary=assosiate_table, back_populates='customer_data')
    def __repr__(self):
        return f"{self.name}"


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    price = Column(Integer())
    customer_data = relationship('Customer', secondary=assosiate_table, back_populates='product_data')
    
    def __repr__(self):
        return f"{self.name}"

    
