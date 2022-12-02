import sqlite3

db = sqlite3.connect('database/db.sql')


def createObjectRolesDict():
    roles = getPolygonRoles()
    asserts = getPolygonAsserts()
    return dict(zip(asserts, roles))


def createPlayerRolesDict():
    roles = getPlayerRoles()
    asserts = getPlayerAsserts()
    return dict(zip(asserts, roles))


def getPolygonRoles():
    return [role[0] for role in db.cursor().execute('SELECT role from polygonRoles').fetchall()]


def getPolygonAsserts():
    return [assrt[0] for assrt in db.cursor().execute('SELECT assert from polygonRoles').fetchall()]


def getPlayerRoles():
    return [role[0] for role in db.cursor().execute('SELECT role from playerRoles').fetchall()]


def getPlayerAsserts():
    return [assrt[0] for assrt in db.cursor().execute('SELECT assert from playerRoles').fetchall()]

