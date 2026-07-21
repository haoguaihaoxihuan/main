"""【程序18】
题目：两个乒乓球队进行比赛，各出三人。甲队为a,b,c三人，乙队为x,y,z三人。
已抽签决定比赛名单。有人向队员打听比赛的名单。a说他不和x比，c说他不和x,z比，
请编程序找出三队赛手的名单。  """

import itertools

def game():
    team_b = ["x", 'y', 'z']
    for i in itertools.permutations(team_b):
        a, b, c = i
        if a != 'x' and c != 'x' and c != 'z':
            return{'a':a, 'b':b, 'c':c}
    return None

print(game())