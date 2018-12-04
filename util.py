


def convert_str_to_num(q_str):
    if q_str.isdigit():
        return int(q_str)
    elif q_str.endswith("m"):
        return float(0.001)*int(q_str[:-1])
    elif q_str.endswith("Ki"):
        return 1024*int(q_str[:-2])
    elif q_str.endswith("K"):
        return 1024*int(q_str[:-1])
    elif q_str.endswith("Mi"):
        return 1024*1024*int(q_str[:-2])
    elif q_str.endswith("M"):
        return 1024*1024*int(q_str[:-1])
    elif q_str.endswith("Gi"):
        return 1024*1024*1024*int(q_str[:-2])
    elif q_str.endswith("G"):
        return 1024*1024*1024*int(q_str[:-1])
    else:
        return 0