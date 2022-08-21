class AABB:
    def __init__(self, x, y, w, h):
        self.x_pos = x
        self.y_pos = y
        self.width = w
        self.height = h

    def __str__(self):
        return f"{self.x_pos}, {self.y_pos}, {self.width}, {self.height}"

    @staticmethod
    def check(rect1, rect2):
        return (rect1.x_pos < rect2.x_pos + rect2.width and
                rect1.x_pos + rect1.width > rect2.x_pos and
                rect1.y_pos < rect2.y_pos + rect2.height and
                rect1.y_pos + rect1.height > rect2.y_pos)
