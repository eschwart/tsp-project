class User:
    def __init__(self):
        self.calories = None,
        self.height = None,
        self.weight = None,

    def set_height(self, height: int):
        self.height = height
    
    def set_weight(self, weight: int):
        pass

    def add_calories(calories: int):
        pass

    def add_workout(workout: str):
        pass


class Database:
    def __init__(self):
        self.users: dict[int, User] = {}
    
    def get_user(self, author_id: int) -> User:
        user = self.users.get(author_id)

        if user == None:
            self.users.update({author_id: User()})
        return self.users.get(author_id)