from itertools import compress
from typing import Mapping, Sequence

import numpy as np

def knapsack(items: Sequence[Mapping[str, int]], max_weight: int):
    n = len(items)
    # build matrix of max value for every weight up to max weight
    knapsack_matrix = np.zeros((n+1, max_weight+1), dtype=np.int16)

    i = 1
    for item in items:
        for w_max in range(max_weight+1):
            # this is the value if we have i - 1 items at the current capacity w_max
            value_without_add_new_item = knapsack_matrix[i-1, w_max]
            if item["weight"] > w_max:
                # can't add new item
                knapsack_matrix[i, w_max] = value_without_add_new_item
            else:
                # try to add new item to see if it increases total value.
                # basically we look for the maximum value with i - 1 items potentially selected
                # WITH the capacity we have left over by adding the current item (hence the
                # w_max - item["weight"] term) and then we add the current item value
                value_with_add_new_item = knapsack_matrix[i-1, w_max-item["weight"]] + item["value"]

                # which value is greater?
                knapsack_matrix[i, w_max] = np.maximum(value_without_add_new_item, value_with_add_new_item)
        i += 1
    
    # now that we have our matrix, we can recover the optimal solution
    items_selected = np.zeros(n, dtype=np.int8)
    w_max = max_weight
    i = len(items) # for iterating backwards
    for item in reversed(items):
        # basically here we check, first:
        # 1. Does the item weigh less than the capcity we have at present?
        # 2. If it does, was this the item added to the maximum value in our matrix with i-1 items potentially selected, in other words
        # was it the item that maximized value when we had i items?
        if (item["weight"] <= w_max) and (knapsack_matrix[i, w_max] - knapsack_matrix[i-1, w_max-item["weight"]] == item["value"]):
            # if yes, this item is in our knapsack
            items_selected[i-1] = 1

            # now we only have a capcity of w_max - item_weight to work with
            w_max -= item["weight"]
        
        i -= 1
    
    return items_selected

def maximum_value(maximum_weight, items):
    items_selected = knapsack(items, maximum_weight)
    total_value = 0
    for item in compress(items, items_selected.tolist()):
        total_value += item["value"]
    
    return total_value
