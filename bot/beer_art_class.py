cat= []


bier_dict = {'beer_keys':[], 'cat': cat}  # База данных ПИВА

class Beer_Art:
    def __init__(self, name:str, foto:str, descripion:str):
        self.name = name
        self.foto = foto
        self.description = descripion
        self.rating = 0
        self.comments = []
        self.like = 0
        self.total = 0


