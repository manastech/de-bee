from google.appengine.ext import db
from model import Membership

class Registration:
    
    def IsRegistered(self, user):
        query = Membership.gql("WHERE user = :1",user)
        return query.count() > 0  

    
