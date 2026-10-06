import json

out = {}

for tipe in ['T', 'E', 'D', 'P']:
    for direction in ['U', 'D', 'S']:
        if(tipe == 'E' and direction == 'S'):
            break
        letter = input("Enter letter for type {} and direction {} (or _ to skip): ".format(tipe, direction))
        if letter != '_':
            out[letter] = {
                'type': tipe,
                'direction': direction
            }
        letter = input("Enter letter for type {} and direction {} filled (or _ to skip): ".format(tipe, direction))
        if letter != '_':
            out[letter] = {
                'type': tipe,
                'direction': direction,
                'filled': True
            }
        letter = input("Enter letter for type {} and direction {} center (or _ to skip): ".format(tipe, direction))
        if letter != '_':
            out[letter] = {
                'type': tipe,
                'direction': direction,
                'center': True
            }
        if tipe == 'D':
            break

with open('letters.txt', 'w') as file:
    file.write(json.dumps(out, indent=4))