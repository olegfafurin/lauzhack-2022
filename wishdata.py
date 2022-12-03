class WishData:
    def __init__(self):
        self.name = None
        self.price = None
        self.photo = None
        self.desc = None

    def update_name(self, name):
        self.name = name

    def update_photo(self, photo):
        self.photo = photo

    def update_price(self, price):
        self.price = price

    def update_desc(self, desc):
        self.desc = desc
