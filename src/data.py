from datetime import datetime


def dt_as_str(dt: datetime) -> str:
    return dt.strftime("%m/%d/%Y")


class Food:
    """The name and number of calories for a food item"""

    def __init__(self, name: str, calories: int):
        self.name = name
        self.calories = calories

class Workout:
    """The PR weight, number of reps, and average rep weight for a workout"""
    def __init__(self, name: str, Reps:int|None, RepW: int|None, PRweight: int|None):
        self.name = name
        self.Reps = Reps
        self.RepW = RepW
        self.PRweight = PRweight

class User:
    """The information of a user"""

    def __init__(self, user_id: int):
        self.height: int | None = None
        self.weight: int | None = None
        self.foods: list[Food] = []
        self.workouts: list[Workout] = []
        self.records: list[(datetime, int)] = []
        self.user_id = user_id

    def get_height(self) -> int | None:
        """Return the current height of the user"""
        return self.height

    def get_weight(self) -> int | None:
        """Return the current weight of the user"""
        return self.weight

    def set_height(self, height: int):
        """Set the current height of the user to the provided value"""
        self.height = height

    def set_weight(self, dt: datetime, weight: int):
        """Set the current weight of the user to the provided value"""
        self.weight = weight
        self.records.append((dt, weight))


    def add_food(self, name: str, calories: int):
        """Add the provided number of calories"""
        food: Food = Food(name, calories)
        self.foods.append(food)

    def get_food(self, foodname: str) -> Food | None:
        """Returns the food object if it is in the foods array"""
        try:
            for obj in self.foods:
                if obj.name == foodname:
                    return obj
            return None
        except ValueError as e:
            return None

    def get_foods(self):
        """Returns the foods of the user"""
        return self.foods


    def add_workout(self, name: str, RepWeight: int|None, Reps: int|None, PRweight:int|None):
        """add the provided workout to the user's list of workouts"""
        workout = Workout(name, Reps, RepWeight, PRweight)
        self.workouts.append(workout)

    def get_workout(self, workoutName: str) -> Workout | None:
        """Returns a specific workout if it exists"""
        try:
            for obj in self.workouts:
                if obj.name == workoutName:
                    return obj
            return None
        except ValueError as e:
            return None
        
    def get_workouts(self) -> list[Workout]:
        """Return the workouts of the user"""
        return self.workouts

    def get_user_id(self) -> int:
        """Return the id of the user"""
        return self.user_id


 
    
    


class Database:
    """Stores and manages users"""

    def __init__(self):
        self.users: dict[int, User] = {}

    def new_user(self, user_id: int):
        """Instantiate the user into the database"""
        self.users.update({user_id: User(user_id)})

    def has_user(self, user_id: int) -> bool:
        """Determine if the user exists"""
        return user_id in self.users.keys()

    def get_user(self, user_id: int) -> User:
        """Return the user's information"""
        return self.users.get(user_id)
