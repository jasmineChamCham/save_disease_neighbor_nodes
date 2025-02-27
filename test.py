def get_compounds():
    with open( "./data/set_compounds.txt", "r") as file:
        list_compounds = file.readlines()
    list_compounds = [c.replace('\n', '') for c in list_compounds]
    return list_compounds

list_compounds = get_compounds() 
index = list_compounds.index('Pranlukast')
print(index)