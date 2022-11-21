from configparser import ConfigParser

from PyQt5.QtWidgets import QMainWindow, QTableWidget


# type == 0 is mainWindow, type == 1 is filterWindow, type == 2 is robotWindow
def translateToRUS(window, windowType):
    if windowType == 0:
        translateMainWindow(window, 'RU')


def translateToEN(window, windowType):
    if windowType == 0:
        translateMainWindow(window, 'EN')


def translateMainWindow(mainWindow: QMainWindow, language):
    parser = ConfigParser()
    parser.read(f'locales/{language}.ini', encoding='UTF-8')

    mainWindow.setWindowTitle(parser.get('LOCALE', 'windowTitle'))


    #QTreeWidget.
    mainWindow.menuSettings.setTitle(parser.get('LOCALE', 'settingsMenuText'))
    mainWindow.menuLanguage.setTitle(parser.get('LOCALE', 'languageMenuText'))
    mainWindow.actionRussian.setText(parser.get('LOCALE', 'russianLabel'))
    mainWindow.actionEnglish.setText(parser.get('LOCALE', 'englishLabel'))

    mainWindow.externalTab.setTabText(0, parser.get('LOCALE', 'exTabText0'))
    mainWindow.externalTab.setTabText(1, parser.get('LOCALE', 'exTabText1'))
    mainWindow.externalTab.setTabText(2, parser.get('LOCALE', 'exTabText2'))

    mainWindow.internalTab.setTabText(0, parser.get('LOCALE', 'inTabText0'))
    mainWindow.internalTab.setTabText(1, parser.get('LOCALE', 'inTabText1'))
    mainWindow.internalTab.setTabText(2, parser.get('LOCALE', 'inTabText2'))

    mainWindow.objectTree.headerItem().setText(0, parser.get('LOCALE', 'polyColumn0'))
    mainWindow.objectTree.headerItem().setText(1, parser.get('LOCALE', 'valueTitle'))
    mainWindow.robotTree.headerItem().setText(0, parser.get('LOCALE', 'robotColumn0'))
    mainWindow.robotTree.headerItem().setText(1, parser.get('LOCALE', 'valueTitle'))
    mainWindow.teamTree.headerItem().setText(0, parser.get('LOCALE', 'teamColumn0'))
    mainWindow.teamTree.headerItem().setText(1, parser.get('LOCALE', 'valueTitle'))
    mainWindow.playerTree.headerItem().setText(0, parser.get('LOCALE', 'playerColumn0'))
    mainWindow.playerTree.headerItem().setText(1, parser.get('LOCALE', 'valueTitle'))

    mainWindow.createPolygonJsonButton.setText(parser.get('LOCALE', 'createPolyJson'))
    mainWindow.loadPolygonJsonButton.setText(parser.get('LOCALE', 'loadPolyJson'))
    mainWindow.createRobotJsonButton.setText(parser.get('LOCALE', 'createRobotJson'))
    mainWindow.loadRobotJsonButton.setText(parser.get('LOCALE', 'loadRobotJson'))
    mainWindow.createTeamJsonButton.setText(parser.get('LOCALE', 'createTeamJson'))
    mainWindow.loadTeamJsonButton.setText(parser.get('LOCALE', 'loadTeamJson'))

    mainWindow.startGameButton.setText(parser.get('LOCALE', 'startGame'))
    mainWindow.restartGameButton.setText(parser.get('LOCALE', 'restartGame'))
    mainWindow.stopGameButton.setText(parser.get('LOCALE', 'stopGame'))
    mainWindow.resetAllButton.setText(parser.get('LOCALE', 'resetAll'))
    mainWindow.shutdownAllButton.setText(parser.get('LOCALE', 'shutdownAll'))

    mainWindow.delayComboBox.setItemText(0, parser.get('LOCALE', 'delay0'))
    mainWindow.delayComboBox.setItemText(1, parser.get('LOCALE', 'delay1'))
    mainWindow.delayComboBox.setItemText(2, parser.get('LOCALE', 'delay2'))
    mainWindow.delayComboBox.setItemText(3, parser.get('LOCALE', 'delay3'))

    mainWindow.infoTable.horizontalHeaderItem(0).setText(parser.get('LOCALE', 'info0'))
    mainWindow.infoTable.horizontalHeaderItem(1).setText(parser.get('LOCALE', 'info1'))
    mainWindow.infoTable.horizontalHeaderItem(2).setText(parser.get('LOCALE', 'info2'))

    mainWindow.commandTable.horizontalHeaderItem(0).setText(parser.get('LOCALE', 'command0'))
    mainWindow.commandTable.horizontalHeaderItem(1).setText(parser.get('LOCALE', 'command1'))
    mainWindow.commandTable.horizontalHeaderItem(2).setText(parser.get('LOCALE', 'command2'))
    mainWindow.commandTable.horizontalHeaderItem(3).setText(parser.get('LOCALE', 'command3'))
    mainWindow.commandTable.horizontalHeaderItem(4).setText(parser.get('LOCALE', 'command4'))
    mainWindow.commandTable.horizontalHeaderItem(5).setText(parser.get('LOCALE', 'command5'))
    mainWindow.commandTable.horizontalHeaderItem(6).setText(parser.get('LOCALE', 'command6'))
    mainWindow.commandTable.horizontalHeaderItem(7).setText(parser.get('LOCALE', 'command7'))
    mainWindow.commandTable.horizontalHeaderItem(8).setText(parser.get('LOCALE', 'command8'))


