import array

teamList = []
playerList = []  # first index -> team index from zero, second index -> player index from zero


def saveToFile(filename, data):
    with open(filename, 'w') as file:
        file.write(data)
        file.close()