# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS Full Motion Video (FMV)
                                 A QGIS plugin

 Analyze and manage georeferenced video data in your maps

                             -------------------
        begin                : 2018-03-13
        copyright            : (C) 2018 All4Gis.
        email                : franka1986@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 #   any later version.                                                    *
 *                                                                         *
 ***************************************************************************/
"""
import os.path

from qgis.PyQt.QtCore import (QSettings,
                          QCoreApplication,
                          QTranslator,
                          qVersion,
                          QThread, Qt)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QHBoxLayout, QSizePolicy
from QGIS_FMV.about.QgsFmvAbout import FmvAbout
from QGIS_FMV.manager.QgsManager import FmvManager
from QGIS_FMV.utils.QgsFmvLog import log
from qgis.PyQt.QtCore import Qt
from QGIS_FMV.utils.QgsUtils import QgsUtils as qgsu
from qgis.core import QgsApplication
from kadas.kadasgui import *

try:
    from pydevd import *
except ImportError:
    None


class Fmv:
    """ Main Class """

    def __init__(self, iface):
        """ Contructor """

        self.iface = KadasPluginInterface.cast( iface )
        log.initLogging()
        threadcount = QThread.idealThreadCount()
        # use all available cores and parallel rendering
        QgsApplication.setMaxThreads(threadcount)
        QSettings().setValue("/qgis/parallel_rendering", True)
        # OpenCL acceleration
        QSettings().setValue("/core/OpenClEnabled", True)

        self.plugin_dir = os.path.dirname(__file__)

        localeSetting = QSettings().value("locale//userLocale")
        if localeSetting:
            locale = localeSetting[0:2]
            localePath = os.path.join(
                self.plugin_dir, 'i18n', 'qgisfmv_{}.qm'.format(locale))
            if os.path.exists(localePath):
                self.translator = QTranslator()
                self.translator.load(localePath)

                if qVersion() > '5.0.0':
                    QCoreApplication.installTranslator(self.translator)

        self._FMVManager = None
        self.bottomBar = None

    def initGui(self):
        ''' FMV Action '''

        self.actionFMV = QAction(QIcon(":/imgFMV/images/icon.png"),
                                 "UAV", self.iface.mainWindow(),
                                 toggled=self.run)
        self.actionFMV.setCheckable( True )
        self.iface.addAction(self.actionFMV, self.iface.PLUGIN_MENU, self.iface.CUSTOM_TAB, "&Plugins")
        
    def unload(self):
        self.iface.removeAction(self.actionFMV, self.iface.PLUGIN_MENU, self.iface.CUSTOM_TAB, "&Plugins")

    def About(self):
        ''' Show About Dialog '''
        self.About = FmvAbout()
        self.About.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.About.exec_()

    def run(self, toggleState ):
        ''' Run method '''
        if toggleState:
            self.createManagerWidget()
        else:
            self.deleteManagerWidget()

    def createManagerWidget(self):
        ''' Create Manager Video QDockWidget '''
        if not self.bottomBar and not self._FMVManager:
            self.bottomBar = KadasBottomBar( self.iface.mapCanvas() )
            self.bottomBar.setLayout( QHBoxLayout() )
            self._FMVManager = FmvManager(self.iface, self.actionFMV )
            self.bottomBar.layout().addWidget( self._FMVManager )
            self.bottomBar.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )
            self.bottomBar.adjustSize()

        self.bottomBar.show()

    def deleteManagerWidget( self ):
        del self._FMVManager
        self._FMVManager = None
        del self.bottomBar
        self.bottomBar = None
