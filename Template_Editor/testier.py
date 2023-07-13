
dict1 = {1: "2 4 -0.99180 $ outside of water pool 8:9:-10 tmp=2.747-8 imp:n,p=0"}
dict2 = {}
dict2[1] = dict1[1]

dict2[1] = dict2[1][1:]
print(dict1)
print(dict2)
