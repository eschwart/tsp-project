class User:
    """A simple class for structuring the information of a user"""

    def __init__(self):
        self.calories: int = 0
        self.height: int | None = None
        self.weight: int | None = None

    def get_height(self) -> int | None:
        """Return the current height of the user"""
        return self.height

    def get_weight(self) -> int | None:
        """Return the current weight of the user"""
        return self.weight

    def set_height(self, height: int):
        """Set the current height of the user to the provided value"""
        self.height = height

    def set_weight(self, weight: int):
        """Set the current weight of the user to the provided value"""
        self.weight = weight

    def add_calories(self, calories: int):
        """Add the provided number of calories"""
        self.calories += calories

    # TODO: figure out what we want to do with this
    def add_workout(self, workout: str):
        pass


class Database:
    """A simple class for storing and managing users"""

    def __init__(self):
        self.users: dict[int, User] = {}

    def new_user(self, user_id: int):
        """Instantiate the user into the database"""
        self.users.update({user_id: User()})

    def has_user(self, user_id: int) -> bool:
        """Determine if the user exists"""
        return user_id in self.users.keys()

    def get_user(self, user_id: int) -> User:
        """Return the user's information"""
        return self.users.get(user_id)
