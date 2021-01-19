import json
from json.decoder import JSONDecodeError


class TrackingUser:
    """
    This class represents a user, which is being tracked by someone, in general.

    Attributes
    ----------
    user_id : int
        telegram user id
    first_name : str
        telegram user first name (is Required)
    username : str
        telegram user username (is Optional)
    online_timeline : List[bool]
        boolean array representation on user's online status.
        True means user was online at given point of time.
        Values are offset with default timeout.
    """
    def __init__(self, entity=None):
        if entity:
            self.user_id = entity.id
            self.first_name = entity.first_name
            self.username = entity.username
        else:
            self.user_id = 0
            self.first_name = 'none'
            self.username = None
        self.online_timeline = []

    @staticmethod
    def from_dict(de_dict):
        user = TrackingUser()

        user.user_id = de_dict['user_id']
        user.first_name = de_dict['first_name']
        user.username = de_dict['username']
        user.online_timeline = de_dict['online']
        return user

    @staticmethod
    def from_json(de_json):
        try:
            obj = json.loads(de_json)
            user = TrackingUser.from_dict(obj)

            return user
        except JSONDecodeError as err:
            raise err

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "username": self.username,
            "online": self.online_timeline
        }

    def to_json(self):
        return json.dumps(
            self.to_dict()
        )

    """
    Implementing custom serialization assets in order to use in peewee.JsonField
    """
    @staticmethod
    def custom_dumps(obj):
        return json.dumps([el.to_dict() for el in obj])

    @staticmethod
    def custom_loads(de_json):
        obj = json.loads(de_json)
        return [TrackingUser.from_dict(el) for el in obj]