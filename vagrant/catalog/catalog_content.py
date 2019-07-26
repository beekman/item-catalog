#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy users
User1 = User(name="Ben Beekman", email="bbeekman@gmail.com",
             picture="")
session.add(User1)
session.commit()

User2 = User(name="Gizmo Beekman", email="gizmo@gmail.com",
             picture="")
session.add(User2)

session.commit()


category1 = Category(user_id=1, name="DJ Gear", slug="dj-gear")

session.add(category1)
session.commit()

category2 = Category(user_id=2, name="Music", slug="music")

session.add(category2)
session.commit()

item1 = Item(user_id=1, name="Serato Scratch Live", slug="serato-scratch-live",
             description="Vinyl emulation software", category=category1)
session.add(item1)
session.commit()

item2 = Item(user_id=2, name="CDJs", slug="cdjs",
             description="These DJ-quality systems allow you\
             to fluidly mix CDs and MP3s with \
             turntablist-grade precision.",
             category=category1)

session.add(item2)
session.commit()
item3 = Item(user_id=2, name="Carbon Based Life Forms",
             slug="carbon-based-life-forms",
             description="https://youtu.be/YzqiUi5-v5I",
             category=category2)
session.add(item3)

session.commit()
item = Item(user_id=2, name="Shpongle", slug="shpongle",
            description="https://youtu.be/8oL6u9eujSU",
            category=category2)
session.add(item)
session.commit()

item5 = Item(user_id=2, name="Brian Eno", slug="brian-eno",
             description="https://youtu.be/ggLTPyRXUKc",
             category=category2)
session.add(item5)
session.commit()
print("Populated the catalog!")
