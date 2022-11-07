import array

teamList = []
playerList = []  # first index -> team index from zero, second index -> player index from zero


def copyToList(data: array.array, list: array.array):
    for i in range(len(data)):
        data[i] = list[i]