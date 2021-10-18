"""
Data model declaration
"""
from sqlalchemy import Column, BigInteger, String

from db.base import Base


class EventTable(Base):
    __tablename__ = "event_table"

    event_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger)
    event_name = Column(String(50))
    event_header = Column(String(150))
    event_description = Column(String(300))
    event_media = Column(String(150))
    event_end_show_date = Column(String(50))    

    def __repr__(self):
        return "<Event(\
                        event_id='%s', \
                        user_id ='%s', \
                        event_name='%s', \
                        event_header='%s', \
                        event_description='%s', \
                        event_media='%s', \
                        event_end_show_date='%s', \
                        " % (
                            self.event_id,
                            self.user_id,
                            self.event_name,
                            self.event_header,
                            self.event_description,
                            self.event_media,
                            self.event_end_show_date,
                            )
