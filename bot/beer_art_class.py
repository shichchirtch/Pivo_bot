cat= ['Odin-Trunk', 'Einfelbräu Helles Landbier', 'Lauterbacher','Maxl helles','Chiemseer','Duckstein','Störterbeker',
'Veltins','Traugott Simon','Hansa','Pülleken','Fischer','Alt','Rothaus Tannenzäpfle','Мышь Соня','Жигули EXPORT',
'NATAKHTARI GOLD','Quick Dip','Оболонь','Светлячок','Чешский старовар','Букет Чувашии пшеничное','Букет Чувашии Чебоксарское',
'Лвiвске', 'Три столицы','Букет Чувашии Леди ночь','Чепецкое Dark','Augustinerbräu München',
'Corona Extra','Тагильской Karlovsbad','Paulaner Weissbier','Тагильское Bergauer Classic','Richmodis Kölsch',
'Guinness Draught','Харбин Премиум','ICY','Leffe','Bolten','Microhistory','Kayaki','Franziskaner','MiXery','LAV',
'Nikšićko tamno','Ursus','Ciucas','Früh Kölsch','Балтика 7','Tatra','Leikeim',
'Allgäuer Büble Bier EdelWeissBie',
'Reichenberger']


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


