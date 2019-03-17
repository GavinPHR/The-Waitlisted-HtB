data = [{"U" : "A", "KL" : ["B"], "UL" : ["C"]}, {"U" : "B", "KL" : ["B"], "UL" : ["D"]}, {"U" : "C", "KL" : ["D"], "UL" : ["B"]}]

def match(data):
    #[{user:[languages]}]
    matches = [{} for i in range(len(data))]
    for i in range(len(data)):
        #Username of user i
        u_i = data[i].get("U")
        #Unknown Languages for user i
        ul_i = data[i].get("UL")
        #Known Languages for user i
        kl_i = data[i].get("KL")
        for j in range(len(data)):
            if i == j:
                continue
            # Username of user j
            u_j = data[j].get("U")
            # Unknown Languages for user j
            ul_j = data[j].get("UL")
            # Known Languages for user j
            kl_j = data[j].get("KL")
            if len(set(ul_i) & set(kl_j)) != 0 and len(set(kl_i) & set(ul_j)) != 0:
                matches[i][u_j] = list(set(ul_i) & set(kl_j))

    return matches

print(match(data))








