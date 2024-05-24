import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.inspection import inspect

DATABASE_URL = 'sqlite:///MieLockDatabase.db'
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class Master(Base):
    __tablename__ = 'master'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(Integer, nullable=False)
    verifications = relationship('Verification', backref='master', lazy=True)
    accesses = relationship('Access', backref='master', lazy=True)

class Verification(Base):
    __tablename__ = 'verification'
    vid = Column(Integer, primary_key=True)
    id = Column(Integer, ForeignKey('master.id'), nullable=False)
    email_id = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    question_1_id = Column(Integer, ForeignKey('security_question.question_id'), nullable=False)
    question_1_answer = Column(String(100), nullable=False)
    question_2_id = Column(Integer, ForeignKey('security_question.question_id'), nullable=False)
    question_2_answer = Column(String(100), nullable=False)
    question_3_id = Column(Integer, ForeignKey('security_question.question_id'), nullable=False)
    question_3_answer = Column(String(100), nullable=False)
    protected = relationship('Protected', backref='verification', lazy=True)

class Protected(Base):
    __tablename__ = 'protected'
    pid = Column(Integer, primary_key=True)
    vid = Column(Integer, ForeignKey('verification.vid'), nullable=False)
    password = Column(String(100), nullable=False)

class Access(Base):
    __tablename__ = 'access'
    room_id = Column(Integer, primary_key=True)
    id = Column(Integer, ForeignKey('master.id'), nullable=False)
    room_number = Column(String(100), nullable=False)

class SecurityQuestion(Base):
    __tablename__ = 'security_question'
    question_id = Column(Integer, primary_key=True)
    question = Column(String(200), nullable=False)

def check_and_repair_db():
    inspector = inspect(engine)
    
    # Get existing tables
    existing_tables = inspector.get_table_names()
    
    # Define models
    models = [Master, Verification, Protected, Access, SecurityQuestion]
    
    # Check and create missing tables
    for model in models:
        if model.__tablename__ not in existing_tables:
            Base.metadata.create_all(bind=engine, tables=[model.__table__])
        else:
            # Check columns
            columns = [column['name'] for column in inspector.get_columns(model.__tablename__)]
            for column in model.__table__.columns:
                if column.name not in columns:
                    alter_statement = f'ALTER TABLE {model.__tablename__} ADD COLUMN {column.compile(dialect=engine.dialect)}'
                    session.execute(alter_statement)
    
    session.commit()

def initialize_database():
    if not os.path.exists('MieLockDatabase.db'):
        Base.metadata.create_all(engine)
    else:
        check_and_repair_db()

if __name__ == '__main__':
    initialize_database()
    print("Database is initialized and repaired (if needed).")
