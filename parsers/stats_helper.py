###  Author: Mark Crossfield <mark.crossfield@tradermedia.co.uk>, Mark Crossfield <mark@markcrossfield.co.uk>
###
###  A helper to assist with the calculation of statistical functions. This has probably been done better elsewhere but I wanted an easy import.
###  
###  Percentiles are calculated with linear interpolation between points.

def find_median(int_list):
    return find_percentile(int_list,50)


def find_percentile(int_list,percentile):
    int_list.sort()
    if len(int_list) == 0:
        return None
    if len(int_list) == 1:
        return int_list[0];
    elif len(int_list) % 10 != 1:
        left_index = percentile * (len(int_list) - 1) / 100
        number_one = int_list[left_index ]
        number_two = int_list[left_index + 1]
        return number_one + ( number_two - number_one) * (((float(percentile)/100)*(len(int_list)-1)%1))
    else:
        return int_list[percentile*len(int_list)/100]

def find_mean(number_list):
    return None if len(number_list) == 0 else sum(number_list,0.0) / len(number_list)