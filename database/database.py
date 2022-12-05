import sqlite3

db = sqlite3.connect('database/db.sql')


def createObjectRolesDict(currentLocale: str):
    roles = getPolygonRoles()
    asserts = getPolygonAsserts(currentLocale)
    return dict(zip(asserts, roles))


def createPlayerRolesDict(currentLocale: str):
    roles = getPlayerRoles()
    asserts = getPlayerAsserts(currentLocale)
    return dict(zip(asserts, roles))


def getPolygonRoles():
    return [role[0] for role in db.cursor().execute('SELECT role from polygonRoles').fetchall()]


def getPolygonAsserts(currentLocale: str):
    return [assrt[0] for assrt in db.cursor().execute(f'SELECT assert{currentLocale} from polygonRoles').fetchall()]


def getPlayerRoles():
    return [role[0] for role in db.cursor().execute('SELECT role from playerRoles').fetchall()]


def getPlayerAsserts(currentLocale: str):
    return [assrt[0] for assrt in db.cursor().execute(f'SELECT assert{currentLocale} from playerRoles').fetchall()]


def getPathByAssert(currentLocale: str, role: str):
    result = db.cursor().execute(f'SELECT imgPath FROM polygonRoles WHERE assert{currentLocale} = ?', (role,)).fetchone()
    if result:
        return result[0]


def getRoleByAssert(currentLocale: str, assrt: str):
    result = db.cursor().execute(f'SELECT role from polygonRoles WHERE assert{currentLocale} = ?', (assrt,)).fetchone()
    if result:
        return result[0]


def getCreatedRobots():
    return [robot[0] for robot in db.cursor().execute('SELECT name from createdRobots').fetchall()]

