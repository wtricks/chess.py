from chess import Chess

c = Chess()
c.load()
c.print()

# c.getmoves()
# # print(c.getmoves())
for m in c.getmoves():
    print(m)