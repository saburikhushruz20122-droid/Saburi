a=int(input())
print("Yes" if a>1 and all(a%i for i in range(2,int(a**.5)+1)) else "No")
