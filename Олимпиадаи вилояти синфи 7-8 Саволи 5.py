import bisect as bbb
a = list(map(int, input().split()))
b = list(map(int, input().split()))
a.sort()
for x in b: print(bbb.bisect_left(a,x))
