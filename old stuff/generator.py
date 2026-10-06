import turtle
import math
import json
import random
from svg_turtle import SvgTurtle

_cell_size_ = 175

_initial_layer_ = 2
_layer_size_ = 20
_triangle_angle_ = 75
_standart_fill_value_ = 6
_standart_unfill_value_ = 2

initial_x = 0
initial_y = 0

def standart_fill_value(layer_size):
    return min(_standart_fill_value_, layer_size//4)

def standart_unfill_value(layer_size):
    return min(_standart_unfill_value_, layer_size//10)

class DraWord:
    def __init__(self, word, letters, initial_layer = _initial_layer_, layer_size = _layer_size_):
        self.x_offset = 0
        self.y_offset = 0
        self.__initial_layer = initial_layer
        self.layer_size = layer_size
        self.__initial = {
            'U': self.__initial_pos_up,
            'R': self.__initial_pos_right,
            'L': self.__initial_pos_left,
            'D': self.__initial_pos_down
        }
        self.__code = {
            'T': self.__draw_triangle,
            'E': self.__draw_empty_triangle,
            'D': self.__draw_diamon,
            'P': self.__draw_pentagon
        }
        self.word=word
        self.letters=letters

    def set_offsets(self, x_offset, y_offset):
        self.x_offset = x_offset
        self.y_offset = y_offset
        return self

    def set_initial_layer(self, initial_layer):
        self.__initial_layer = initial_layer
        return self

    def __home(self, t):
        t.goto(self.x_offset, self.y_offset)
        t.setheading(0)

    def __get_size(self, layer):
        return self.layer_size*(layer+self.__initial_layer)

    def __get_length(self, layer):
        return 2**(1/2)*self.__get_size(layer)/2/math.cos(math.degrees(-_triangle_angle_))

    def __initial_pos_up(self, t, layer):
        t.penup()
        self.__home(t)
        t.left(90)
        t.forward(self.__get_length(layer))

    def __initial_pos_right(self, t, layer):
        t.penup()
        self.__home(t)
        t.forward(self.__get_length(layer))

    def __initial_pos_left(self, t, layer):
        t.penup()
        self.__home(t)
        t.left(180)
        t.forward(self.__get_length(layer))

    def __initial_pos_down(self, t, layer):
        t.penup()
        self.__home(t)
        t.right(90)
        t.forward(self.__get_length(layer))

    def __initial_pos(self, t):
        t.penup()
        self.__home(t)
        t.left(90)

    def __draw_center(self, t, layer=0):
        t.forward(self.__get_length(layer))
        t.pendown()
        t.right(90+45)
        t.begin_fill()
        for _ in range(4):
            t.forward(2*self.__get_size(layer)/2/math.cos(math.degrees(-75)))
            t.right(90)
        t.end_fill()
        self.__initial_pos(t)

    def __draw_triangle(self, t, layer, dir, filled = _standart_unfill_value_, center = False):
        
        t.pensize(filled)

        if dir=='S':
            self.__draw_triangle(t, layer, 'L', filled, center)
            self.__draw_triangle(t, layer, 'R', filled, center)
            return
        
        self.__initial[dir](t, layer)
        t.pendown()
        t.left(90+45)
        t.forward(self.__get_size(layer))
        self.__initial[dir](t, layer)
        t.pendown()
        t.right(90+45)
        t.forward(self.__get_size(layer))
        
        if center:
            self.__initial[dir](t, layer)
            t.pendown()
            t.backward(self.__get_size(layer)-self.__get_size(layer-1))

        self.__initial_pos(t)

    def __draw_empty_triangle(self, t, layer, dir, filled = _standart_unfill_value_, center = False):
        t.pensize(filled)

        if dir=='S':
            self.__draw_empty_triangle(t, layer, 'L', filled, center)
            self.__draw_empty_triangle(t, layer, 'R', filled, center)
            return
        
        self.__initial[dir](t, layer)
        t.left(90+45)
        t.penup()
        t.forward(self.__get_size(layer)*0.1)
        t.pendown()
        t.forward(self.__get_size(layer)*0.8)
        self.__initial[dir](t, layer)
        t.right(90+45)
        t.penup()
        t.forward(self.__get_size(layer)*0.1)
        t.pendown()
        t.forward(self.__get_size(layer)*0.8)
        
        if center:
            t.pensize(standart_unfill_value(self.layer_size))
            self.__initial[dir](t, layer)
            t.pendown()
            t.backward(self.__get_size(layer)-self.__get_size(layer-1))

        self.__initial_pos(t)

    def __draw_diamon(self, t, layer, _, filled = _standart_unfill_value_, center = False):
        self.__draw_triangle(t, layer, 'U', filled, center)
        self.__draw_triangle(t, layer, 'D', filled, center)
        self.__draw_triangle(t, layer, 'S', filled, center)

    def __draw_pentagon(self, t, layer, dir, filled = _standart_unfill_value_, center = False):
        t.pensize(filled)

        if dir=='S':
            self.__draw_pentagon(t, layer, 'L', filled, center)
            self.__draw_pentagon(t, layer, 'R', filled, center)
            return
        
        length = (self.__get_length(layer)-self.__get_length(layer-1))/math.sqrt(2)

        self.__initial[dir](t, layer)
        t.pendown()
        t.left(90+45)
        t.forward(length*2)
        t.left(90)
        t.forward(length)
        self.__initial[dir](t, layer)
        t.pendown()
        t.right(90+45)
        t.forward(length*2)
        t.right(90)
        t.forward(length)
        
        if center:
            self.__initial[dir](t, layer)
            t.pendown()
            t.backward(self.__get_size(layer)-self.__get_size(layer-1))

        self.__initial_pos(t)
    
    def draw_word(self, t, letters):
        self.__initial_pos(t)
        self.__draw_center(t)
        layer = 1
        last_dir = 'L'
        for letter in self.word:
            if letter in letters:
                shape = letters[letter]
                shape_type = shape['type']
                direction = shape['direction']
                if direction == 'D' and last_dir == 'U':
                    layer -= 1
                last_dir = direction
                filled = shape.get('filled', False)
                if filled:
                    filled = standart_fill_value(self.layer_size)
                else:
                    filled = standart_unfill_value(self.layer_size)
                    
                center = shape.get('center', False)
                if shape_type in self.__code:
                    self.__code[shape_type](t, layer, direction, filled, center)
                layer += 1
        self.__draw_diamon(t, layer, '', filled=standart_fill_value(self.layer_size)*1.5)
        return self
    
    def __get_n_layers(self, letters):
        layer = 1
        last_dir = 'L'
        for letter in self.word:
            if letter in letters:
                shape = letters[letter]
                direction = shape['direction']
                if direction == 'D' and last_dir == 'U':
                    layer -= 1
                last_dir = direction
                layer += 1
        return layer
    
    def get_distance_from_center(self, letters):
        return self.__get_length(self.__get_n_layers(letters))

def generate_json( file = 'NEW.dict'):
    with open(file, 'r') as file:
        entry=json.loads(file.read())
    return entry

letters = generate_json()
def generate_sentence(sentence, letters):
    sentence = sentence.replace('V', 'B').replace('LL', 'Y')

    turtle.TurtleScreen._RUNNING=True
    _turtle = turtle.Turtle()
    turtle.tracer(0, 0) 
    _turtle.hideturtle()

    _turtle.speed(10)

    #initial_y = 0
    words = [DraWord(word, letters, random.randint(1,3), random.randint(10, 30)) for word in sentence.split(' ')]
    heigh = sum([word.get_distance_from_center(letters)*2 for word in words])
    width = max([word.get_distance_from_center(letters)*2 for word in words])
    current_x = 0
    current_y = heigh/2

    for word in words:
        word.set_offsets(current_x, current_y - word.get_distance_from_center(letters)).draw_word(_turtle, letters)
        current_y -= word.get_distance_from_center(letters)*2

    #
    #t.hide_turtle()
    turtle.update()
    _turtle.ht()
    input()
    #_turtle.getscreen().getcanvas().postscript(
    #    file="./out/{}.eps".format(sentence.replace(' ', '_')), 
    #    heigh = heigh+20, y=-heigh/2-10, 
    #    width = width+20, x = -width/2-10
    #    )
generate_sentence(input(), generate_json())
#
#with open('NEW.dict', 'r') as file:
#    letters=json.loads(file.read())
#
#sentence=input("Enter a sentence: ").upper()
#s = turtle.getscreen()
#t = turtle.Turtle()
#turtle.tracer(0, 0) 
#t.hideturtle()
#
#t.speed(10)
#
#initial_y = 0
#words = [DraWord(word, letters) for word in sentence.split(' ')]
#heigh = sum([word.get_distance_from_center()*2 for word in words])
#width = max([word.get_distance_from_center()*2 for word in words])
#current_x = 0
#current_y = heigh/2
#
#for word in words:
#    word.set_offsets(current_x, current_y - word.get_distance_from_center()).draw_word(t, letters)
#    current_y -= word.get_distance_from_center()*2
#
#turtle.update()
#turtle.getscreen().getcanvas().postscript(
#    file="./imgs/{}.eps".format(sentence.replace(' ', '_')), 
#    heigh = heigh+20, y=-heigh/2-10, 
#    width = width+20, x = -width/2-10
#    )

#draw_triangle(t, 3, 'U')
#draw_empty_triangle(t, 4, 'D')
#draw_triangle(t, 5, 'U', filled=4)
#draw_pentagon(t, 6, 'U')
#draw_triangle(t, 5, 'D', center=True)
#draw_empty_triangle(t, 6, 'D')
#draw_pentagon(t, 7, 'S', filled=4)
#draw_diamon(t, 8, filled=5)