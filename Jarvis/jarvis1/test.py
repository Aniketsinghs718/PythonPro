# print("hello")
import os
# f=open("demo.txt","r")
# print(f.read())

f=open("demo.txt","a")
f.write("goog morning!!")
f.close()

f=open("demo.txt","r")
print(f.read())

f.close()

