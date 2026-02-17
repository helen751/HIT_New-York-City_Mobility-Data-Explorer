def quicksort(trips):

    if len(trips) <= 1:
        return trips

    pivot = trips[len(trips) // 2]["fare_amount"]

    left = []
    middle = []
    right = []

    for trip in trips:
        if trip["fare_amount"] > pivot:
            left.append(trip)
        elif trip["fare_amount"] < pivot:
            right.append(trip)
        else:
            middle.append(trip)

    return quicksort(left) + middle + quicksort(right)
