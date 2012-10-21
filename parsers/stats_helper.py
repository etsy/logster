###  Author: Mark Crossfield <mark.crossfield@tradermedia.co.uk>, Mark Crossfield <mark@markcrossfield.co.uk>
###
###  A helper to assist with the calculation of statistical functions. This has probably been done better elsewhere but I wanted an easy import.
###
###  Percentiles are calculated with linear interpolation between points.

def find_median(numbers):
    return find_percentile(numbers,50)


def find_percentile(numbers,percentile):
    numbers.sort()
    if len(numbers) == 0:
        return None
    if len(numbers) == 1:
        return numbers[0];
    elif (float(percentile) / float(100))*float(len(numbers)-1) %1 != 0:
        left_index = int(percentile * (len(numbers) - 1) / 100)
        number_one = numbers[left_index ]
        number_two = numbers[left_index + 1]
        return number_one + ( number_two - number_one) * (((float(percentile)/100)*(len(numbers)-1)%1))
    else:
        return numbers[int(percentile*(len(numbers)-1)/100)]

def find_mean(numbers):
    if len(numbers) == 0:
        return None
    else:
        return sum(numbers,0.0) / len(numbers)
