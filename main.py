from language.core import interpret

while True:
    inp = input('shell >>> ')
    if inp == 'exit': break
    res = interpret('main.py', inp)
    print(res, '\n')
