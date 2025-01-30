# n=int(input("enter no."))
# for i in range(1,n+1):
#     print(" "*(n-i),end=" ")
#     print("*"*((i*2)-1))
    
n=int(input("enter no."))
for i in range(n):
    print("")
    for j in range(n):
        if(i==0 or j==0 or i==n-1 or j==n-1 ):
            print("*",end=" ")
        else:
            print(" ",end=" ")    