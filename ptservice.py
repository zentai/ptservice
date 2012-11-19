import logging
import cherrypy
from pymongo import Connection
from bson.objectid import ObjectId
from pymongo.errors import InvalidId
from datetime import datetime
from utils import to_response, _result_to_dict

import re
MONGODB_PORT=27017
username = ""
password = ""

class MemberManager(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        connection = Connection('localhost', MONGODB_PORT)
        self.db = connection.ptservice
        # self.db.authenticate("admin", "zhijian.81")
        self.table = self.db.member
        self.logger.info("Freelancer init: Connection('%s', %s)" % ('localhost', MONGODB_PORT) )

    @cherrypy.expose
    def register(self, name, address, tel, email):
        member = {
            'name': name,
            'address': address,
            'tel': tel,
            'email': email,
            'total_point': 0,
            'active': True,
            'create_date': datetime.now(),
        }

        if self.table.find({'email': email}).count() > 0:
            msg = "MemberManager.register fail, email duplicate: %s" % email
            self.logger.error(msg)
            return to_response(500, {'msg': msg})

        _id = self.table.insert(member)
        self.logger.info("MemberRegister@%s" % member)
        return to_response(200, _result_to_dict(self.table.find({"_id": _id})))

    @cherrypy.expose
    def enable(self, id):
        user = self.table.find_one({'_id': ObjectId(id)})
        user["active"] = True
        self.table.save(user)
        return to_response(200, user)

    @cherrypy.expose
    def disable(self, id):
        user = self.table.find_one({'_id': ObjectId(id)})
        user["active"] = False
        self.table.save(user)
        return to_response(200, user)

    @cherrypy.expose
    def filter(self, keyword = None):
        if not keyword:
            return to_response(200, _result_to_dict(self.table.find()))

        records = {}
        regx = re.compile(".*%s.*" % keyword, re.IGNORECASE)
        search_dict = {"$or": [
            {"name": regx}, 
            {"email": regx}
        ]}
        return to_response(200, _result_to_dict(self.table.find(search_dict)))

    def fetch_member(self, id):
        member = None
        try:
            self.table.find_one({'_id': ObjectId(id)})
            member = Member(id)
        except InvalidId as e:
            self.logger.error("Customer ID not found: %s", id)
            raise e
        return member

    @cherrypy.expose
    def topup(self, id, point, free, paidtype):
        member = None
        try:
            member = self.fetch_member(id)
        except InvalidId:
            error_msg = "topup@fail: reason: id '%s' not foud" % id
            self.logger.error(error_msg)
            return to_response(500, error_msg)
        result = member.topup(int(point), int(free), paidtype)
        return to_response(200, { 'result': result})

    @cherrypy.expose
    def total(self, id):
        member = None
        try:
            member = self.fetch_member(id)
        except InvalidId:
            error_msg = "total@fail: reason: id '%s' not foud" % id
            self.logger.error(error_msg)
            return to_response(500, error_msg)
        result = member.recalc_point()
        return to_response(200, { 'result': result})

class Member(object):
    def __init__(self, id):
        self.id = id
        self.logger = logging.getLogger(__name__)
        connection = Connection('localhost', MONGODB_PORT)
        self.db = connection.ptservice
        # self.db.authenticate("admin", "zhijian.81")
        self.db_point = self.db.point
        self.db_member = self.db.member
        self.logger.info("member init: Connection('%s', %s)" % ('localhost', MONGODB_PORT) )

    def topup(self, point, free, paidtype = "cash", card_no = None):
        assert isinstance(point, int), "point should be int"
        assert isinstance(point, int), "free should be int"

        data = {
            "member_id": self.id,
            "point": point,
            "free": free,
            "paid_type": paidtype,
            "card_no": card_no,
            "active": True,
            "type": "income",
            "desp": "topup",
            "create_date": datetime.now(),
        }
        result = self.db_point.insert(data)
        self.logger.info("topup@%s" % data)
        member = self.db_member.find_one({'_id': ObjectId(self.id)})
        member['total_point'] = self.recalc_point()
        self.db_member.save(member)
        self.logger.info("member@%s" % member)
        return result

    #TODO
    # remember check to add redeem record
    def recalc_point(self):
        records = self.db_point.find({'member_id': self.id, 'active': True, 'type': 'income'})
        total = 0
        for record in records:
            total += record['point'] + record['free']

        records = self.db_point.find({'member_id': self.id, 'active': True, 'type': 'expense'})
        redeem = 0
        for record in records:
            total += record['point']

        return total - redeem

    def redeem(self, service, employee):
        pass
    def _transaction(self, point):
        pass
    def history(self, filter = None):
        pass