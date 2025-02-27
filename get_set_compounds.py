def get_compounds():
    with open( "./data/set_compounds.txt", "r") as file:
        list_compounds = file.readlines()
        
    list_compounds = [c.replace('\n', '') for c in list_compounds]
    return list_compounds

list_compounds = get_compounds() 

# list_compounds = list(set(list_compounds))

# print(len(list_compounds)) # 3938
# print(list_compounds[:3])

# with open( "./data/set_compounds.txt", "w") as file:
#     file.writelines(list_compounds) 

print(list_compounds[:3])
