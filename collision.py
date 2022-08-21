class AABB:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __str__(self):
        return f"{self.x}, {self.y}, {self.w}, {self.h}"

    @staticmethod
    def check(rect1, rect2):
        return rect1.x < rect2.x + rect2.w and rect1.x + rect1.w > rect2.x and rect1.y < rect2.y + rect2.h and rect1.y + rect1.h > rect2.y
