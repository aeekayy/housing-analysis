# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text

class RedfinHouse(db.Model):
    __tablename__ = "redfin_house"

    redfin_house_id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=sa_text("uuid_generate_v4()"))
    address_1 = db.Column(db.String(256))
