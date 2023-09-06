from LocalData.Soundscape import Soundscape
'''

scale patterns :
MAJOR:
[ C
F
Bb
Eb
Ab
Db
Gb
B
E
A
D
G
]


MINOR:
[a, 
d,
g,
c,
f,
bb,
eb,
g#,
c#,
f#,
b,
e]





'''

if __name__ == '__main__':
    db = Soundscape()
    db.extract_and_store_new_audio()
    print(len(db.get_all_audio()))
    db.close()

