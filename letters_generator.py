from ast import Tuple
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import json
import turtle
import math
import random
from typing import List, Literal, Tuple
from PIL import Image, ImageTk
import pyglet, os
import os.path

#pato@name@com@3 comida@verb@ind-Fut@imp-Past

pyglet.font.add_file(os.path.join('fonts','AutobusOmnibus-K7127.ttf'))
pyglet.font.add_file(os.path.join('fonts','FairfaxHD.ttf'))

_cell_size_ = 175

_initial_layer_ = 2
_layer_size_ = 20
_triangle_angle_ = 75
_standart_fill_value_ = 6
_standart_unfill_value_ = 2

initial_x = 0
initial_y = 0


def standart_fill_value(layer_size):
    return max(min(_standart_fill_value_, layer_size//4),3)

def standart_unfill_value(layer_size):
    return max(min(_standart_unfill_value_, layer_size//10),1)

class DraWord:

    class WordModifiers:
        def __init__(self, 
                     #wrap: Literal["sub", "comp"] = None, 
                     #wrap_ending: Tuple[Literal["U", "D"], Literal["C", "CC", "composition", None]] = None,
                     negation: bool = False
                     ):
            self.negation = negation
            self.modifiers = []
            #if wrap is not None:
            #    self.modifiers.append((1, 1 if wrap=="sub" else 0, wrap, "S"))
            #if wrap_ending is not None:
            #    self.modifiers.append((1, 1 if wrap_ending[0]=="CC" else 0, wrap_ending[1], wrap_ending[0]))

        def add_modifier(self, priority, symbol, dir):
            self.modifiers.append((priority, symbol, dir))
        
        #def get_layers(self, dir):
        #    return len(set([m[0] for m in self.modifiers if m[3]==dir]))

        def get_max_priority(self, dir = None):
            print(self.modifiers)
            return max([m[0] for m in self.modifiers if dir is None or m[2]==dir], default=0)

        def get_layers(self, dir):
            return self.get_max_priority(dir)

        def get_modifiers(self):
            self.modifiers.sort(key=lambda x: x[0], reverse=True)
            return self.modifiers

    class NameModifiers(WordModifiers):
        def __init__(self, 
                     name: Literal["ind", "com", "prop"] = [],
                     num: int = 0,
                     negation: bool = False):
            super().__init__(negation=negation)
            #a bit of a hack
            priority = self.get_max_priority("U")+1
            if name[0]!="i":
                self.add_modifier(priority, "E", "U")
                priority += 1
            if name[1]=="r":
                self.add_modifier(priority, "E", "U")
                
            priority = self.get_max_priority("D")+1
            if num >= 1:
                self.add_modifier(priority, "E", "D")
                priority += 1
            if num >= 2:
                self.add_modifier(priority, "E", "D")

    class AdModifiers(WordModifiers):
        def __init__(self, 
                     adv: bool = False,
                     negation: bool = False
                    ):
            super().__init__(negation=negation)
            self.adv = adv
            self.add_modifier(self.get_max_priority("S")+2, "t", "S")

        def get_max_priority(self, dir = None):
            if (dir is None or dir == "S") and self.adv:
                return super().get_max_priority(dir)-2
            else:
                return super().get_max_priority(dir)

    class VerbModifiers(WordModifiers):
        def __init__(self, 
                     time = None, #List[Tuple[Literal["ind", "sub", "imp"], Literal["past", "pres", "fut"]]]
                     negation: bool = False
                    ):
            super().__init__(negation=negation)
            if time is None or len(time) == 0:
                self.add_modifier(self.get_max_priority()+1, "D", "U")
            else:
                modes = {"ind": "Tl", "sub": "Ll", "imp": "tI"}
                times = {"past": "U", "pres": "S", "fut": "D"}
                sizes = {"U": 0, "S": 0, "D": 0}
                for i,t in enumerate(time):
                    sizes[times[t[1]]] = 2*i
                print(sizes)
                print(time)
                for t in time:
                    i = max(self.get_max_priority("D"), self.get_max_priority("U"))
                    for m in modes[t[0]]:
                        i+=1
                        self.add_modifier(i, m, times[t[1]])
                    for dir in ["U", "D", "S"]:
                        if dir != times[t[1]] and sizes[dir] > i-2:
                            self.add_modifier(i-1, "l", dir)

    def __init__(self, word, letters, initial_layer = _initial_layer_, layer_size = _layer_size_, modifiers: WordModifiers = None):
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
            'T': self.__draw_triangle, #\/
            't': self.__draw_small_triangle,
            'E': self.__draw_empty_triangle, #\ /
            'D': self.__draw_diamond, #<>
            'P': self.__draw_pentagon,  #--------------->/  \
            'L': self.__draw_line, #---                 #\  /
            'l': self.__draw_small_line, #-             # \/
            'I': self.__draw_closed_small_triangle #| |
                                                   #\/
        }
        self.word=word
        self.letters=letters
        self.modifiers = modifiers

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

    def __get_layers_modifier(self, dir = None):
        if self.modifiers is None:
            return 0
        return self.modifiers.get_layers(dir)

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

    def __draw_small_triangle(self, t, layer, dir, filled = _standart_unfill_value_, center = False):        
        t.pensize(filled)

        if dir=='S':
            self.__draw_small_triangle(t, layer, 'L', filled, center)
            self.__draw_small_triangle(t, layer, 'R', filled, center)
            return
        
        self.__initial[dir](t, layer)
        t.pendown()
        t.left(90+45)
        t.forward(self.__get_size(layer)/2)
        self.__initial[dir](t, layer)
        t.pendown()
        t.right(90+45)
        t.forward(self.__get_size(layer)/2)
        
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

    def __draw_diamond(self, t, layer, _, filled = _standart_unfill_value_, center = False):
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

    def __draw_closed_small_triangle(self, t, layer, dir, filled = _standart_unfill_value_, center = False):
        t.pensize(filled)

        if dir=='S':
            self.__draw_closed_small_triangle(t, layer, 'L', filled, center)
            self.__draw_closed_small_triangle(t, layer, 'R', filled, center)
            return
        
        length = (self.__get_length(layer)-self.__get_length(layer-1))/math.sqrt(2)

        self.__initial[dir](t, layer)
        t.pendown()
        t.left(90+45)
        t.forward(length*2)
        t.left(90-45)
        t.forward(length*2)
        self.__initial[dir](t, layer)
        t.pendown()
        t.right(90+45)
        t.forward(length*2)
        t.right(90-45)
        t.forward(length*2)
        
        if center:
            self.__initial[dir](t, layer)
            t.pendown()
            t.backward(self.__get_size(layer)-self.__get_size(layer-1))

        self.__initial_pos(t)

    def __draw_line(self, t, layer, dir, filled = _standart_unfill_value_, center = False):   
        t.pensize(filled)

        if dir=='S':
            self.__draw_line(t, layer, 'L', filled, center)
            self.__draw_line(t, layer, 'R', filled, center)
            return
        
        self.__initial[dir](t, layer)
        t.pendown()
        t.left(90)
        t.forward(self.__get_size(layer)/2)
        self.__initial[dir](t, layer)
        t.pendown()
        t.right(90)
        t.forward(self.__get_size(layer)/2)
        
        if center:
            self.__initial[dir](t, layer)
            t.pendown()
            t.backward(self.__get_size(layer)-self.__get_size(layer-1))

        self.__initial_pos(t)

    def __draw_small_line(self, t, layer, dir, filled = _standart_unfill_value_, center = False):          
        t.pensize(filled)

        if dir=='S':
            self.__draw_small_line(t, layer, 'L', filled, center)
            self.__draw_small_line(t, layer, 'R', filled, center)
            return
        
        self.__initial[dir](t, layer)
        t.pendown()
        t.left(90)
        t.forward(self.__get_size(layer)/16)
        self.__initial[dir](t, layer)
        t.pendown()
        t.right(90)
        t.forward(self.__get_size(layer)/16)
        
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
        self.__draw_diamond(t, layer, '', filled=standart_fill_value(self.layer_size)*1.5)
        if self.modifiers is not None:
            for extra_layer, shape, dir in self.modifiers.get_modifiers():
                if shape in self.__code:
                    self.__code[shape](t, layer+extra_layer, dir, filled=standart_unfill_value(self.layer_size), center=True) 
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
    
    def get_distance_from_center(self, letters, dir = None):
        return self.__get_length(self.__get_n_layers(letters)+self.__get_layers_modifier(dir))

window = tk.Tk()

table_entry = {}
entry = {}
image = {}

row = 0
col = 0

for direction in ['U', 'D', 'S']:
    for tipe in ['T', 'E', 'D', 'P']:
        if tipe == 'D' and direction != 'S':
                continue
        if(tipe == 'E' and direction == 'S'):
                continue
        col += 1
        table_entry[(direction, tipe)] = tk.Frame(
            master=window,
            relief=tk.RAISED,
            borderwidth=1
        )
        table_entry[(direction, tipe)].grid(row=row, column=col)
        image[(direction, tipe)] = ImageTk.PhotoImage(Image.open(os.path.join('imgs',"{}{}.jpg".format( direction, tipe))).resize((_cell_size_,_cell_size_)))
        label = tk.Label(
            master=table_entry[(direction, tipe)],
            image=image[(direction, tipe)],
            width=_cell_size_,
            height=_cell_size_
        )
        label.pack()

for format in ['N', 'F', 'C']:
    col=0
    row+=1
    if format == 'D':
        continue
    table_entry[('Header', format)] = tk.Frame(
        master=window,
        relief=tk.RAISED,
        borderwidth=1
    )
    table_entry[('Header', format)].grid(row=row, column=col)
    image[format] = ImageTk.PhotoImage(Image.open(os.path.join("imgs","'{}'.jpg".format(format))).resize((_cell_size_,_cell_size_)))
    label = tk.Label(
        master=table_entry[('Header', format)],
        image=image[format],
        width=_cell_size_,
        height=_cell_size_
    )
    label.pack(fill = "both", expand = "yes")
    for direction in ['U', 'D', 'S']:
        for tipe in ['T', 'E', 'D', 'P']:
            if tipe == 'D' and direction != 'S':
                    continue
            if(tipe == 'E' and direction == 'S'):
                continue
            col+=1
            if tipe == 'D' and format == 'F':
                continue
            table_entry[(tipe, format, direction)] = tk.Frame(
                master=window,
                relief=tk.RAISED,
                borderwidth=1,
                width=_cell_size_,
                height=_cell_size_
            )
            table_entry[(tipe, format, direction)].grid(row=row, column=col)
            entry[(tipe, format, direction)] = tk.Entry(
                master=table_entry[(tipe, format, direction)], 
                width=1,
                font=("AutobusOmnibus-K7127", 50)
                
            )
            window.grid_columnconfigure(col, minsize=_cell_size_, weight=1)
            entry[(tipe, format, direction)].pack(expand=True, fill='both')

def generate_json():
    out = {}
    for key in entry:
        value = entry[key].get()
        if value != '':
            tipe = key[0]
            format = key[1]
            direction = key[2]
            out[value] = {
                'type': tipe,
                'direction': direction
            }
            if format == 'F':
                out[value]['filled'] = True
            elif format == 'C':
                out[value]['center'] = True
    return out

def load():
    filepath = askopenfilename(
        filetypes=[("Dictionary files", "*.dict"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    with open(filepath, 'r') as input_file:
        data = input_file.read()
        dictionary = json.loads(data)
        for key in dictionary:
            tipe = dictionary[key]['type']
            direction = dictionary[key]['direction']
            filled = 'filled' in dictionary[key] and dictionary[key]['filled']
            center = 'center' in dictionary[key] and dictionary[key]['center']
            format = 'N'
            if filled:
                format = 'F'
            elif center:
                format = 'C'
            if (tipe, format, direction) in entry:
                entry[(tipe, format, direction)].delete(0, tk.END)
                entry[(tipe, format, direction)].insert(0, key)

def save():
    out = generate_json()
    filepath = asksaveasfilename(
        filetypes=[("Dictionary files", "*.dict"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    with open(filepath, 'w') as output_file:
        output_file.write(json.dumps(out, indent=4))

def generate_modifiers(word: str) -> DraWord.WordModifiers:
    data = word.lower().split('@')
    print(data)
    if len(data) == 1:
        return None
    if data[1] == 'name':
        return DraWord.NameModifiers(name=data[2] if len(data) > 2 else None, num=int(data[3]) if len(data) > 3 else 0)
    elif data[1] in ['adv', 'adj']:
        return DraWord.AdModifiers(adv=data[1] == 'adv' if len(data) >= 2 else False)
    elif data[1] == 'verb':
        time = None
        if len(data) > 2:
            time = []
            for t in data[2:]:
                mode, tense = t.split('-')
                time.append((mode, tense))
        return DraWord.VerbModifiers(time=time)
    return None

def generate():
    letters = generate_json()
    sentence_window = tk.Tk()
    sentence_entry = tk.Entry(
        master=sentence_window, 
        width=50,
        font=("FairfaxHD", 24)
    )
    label = tk.Label(
        master=sentence_window,
        text="Enter a sentence:"
    )
    label.pack()
    sentence_entry.pack()
    def generate_sentence():
        sentence = sentence_entry.get().upper()

        turtle.TurtleScreen._RUNNING=True
        _turtle = turtle.Turtle()
        turtle.tracer(0, 0) 
        _turtle.hideturtle()

        _turtle.speed(10)

        #initial_y = 0
        words = [DraWord(word.split('@')[0].replace('V', 'B').replace('LL', 'Y'), letters, random.randint(1,3), random.randint(10, 30), modifiers = generate_modifiers(word)) for word in sentence.split(' ')]
        heigh = sum([word.get_distance_from_center(letters, "U")*2 for word in words])
        width = max([word.get_distance_from_center(letters, "U")*2 for word in words])
        current_x = 0
        current_y = heigh/2

        for word in words:
            word.set_offsets(current_x, current_y - word.get_distance_from_center(letters, "U")).draw_word(_turtle, letters)
            current_y -= word.get_distance_from_center(letters, "U")*2

        #
        #t.hide_turtle()
        turtle.update()
        _turtle.ht()
        _turtle.getscreen().getcanvas().postscript(
            file="./out/{}.eps".format(sentence.replace(' ', '_')), 
            heigh = heigh+20, y=-heigh/2-10, 
            width = width+20, x = -width/2-10
            )
        #turtle.resetscreen()
        #_turtle.clear()
        #turtle.bye()
        sentence_window.destroy()

    generate_button = tk.Button(
        master=sentence_window,
        text="Generate",
        width=10,
        height=2,
        bg="blue",
        fg="white",
        command=generate_sentence
    )
    generate_button.pack()

    

frame = tk.Frame(
    master=window,
    relief=tk.RAISED,
    borderwidth=1
)
frame.grid(row=row+1, column=8)
load_button = tk.Button(
    master=frame,
    text="Load",
    width=_cell_size_//10,
    height=_cell_size_//25,
    bg="white",
    fg="black",
    command=load
)

frame = tk.Frame(
    master=window,
    relief=tk.RAISED,
    borderwidth=1
)
frame.grid(row=row+1, column=9)
save_button = tk.Button(
    master=frame,
    text="Save",
    width=_cell_size_//10,
    height=_cell_size_//25,
    bg="black",
    fg="white",
    command=save
)

frame = tk.Frame(
    master=window,
    relief=tk.RAISED,
    borderwidth=1
)
frame.grid(row=row+1, column=0)
generate_button = tk.Button(
    master=frame,
    text="Generate text",
    width=_cell_size_//10,
    height=_cell_size_//25,
    bg="green",
    fg="white",
    command=generate
)

generate_button.pack()
save_button.pack()
load_button.pack()
window.mainloop()
            
