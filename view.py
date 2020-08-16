# -*- coding: utf-8 -*-

 ##############################################
 ##                                            ##
 ##               Products Package              ##
 ##                     View                    ##
 ##                                             ##
 ##              from Basiq Series              ##
 ##           by Críptidos Digitales            ##
 ##                 GPL (c)2008                 ##
  ##                                            ##
	##############################################

"""
"""

from __future__ import print_function

import sys
from decimal import Decimal


from PyQt4 import QtCore, QtGui

from cdWidgets import cdComboBox, cdFrame, cdLineEdit, cdNumberEdit, cdTableWidgetItem, cdTextEdit
from cdWidgets import cdTableWidgetItem

from products import frame_ui
from products import manager_ui
from products import capture_ui
from products import aceptions_ui
from products import aception_ui
from products import details_ui
from products import kardex_ui
from products import tools_ui


## STATE VALUES
IDLE, BUSY, BLOQUED = [100, 103, 105]


class Master(QtGui.QFrame):
	""" This widget acts as an accesspoint to all view related widgets and methods for this module.
		It acts as a container and layout manager for basic widgets too, like Manager(list), Capture(edit), Details(Consult)
	"""

	def __init__(self, *args, **kwds):
		"""        products.view.Master.__init__()"""

		self.cnt = kwds.pop('cnt')

		args = args[:-1]

		QtGui.QFrame.__init__(self, *args)

		self.container = self.parent()
		self.layoutZoom = self.container.layoutZoom
		self.eventRouter = self.container.eventRouter

		self._localAceptionIsHidden = False

		self.ui = frame_ui.Ui_Form()
		self.ui.setupUi(self)

		self.ui.frame1.close()
		self.ui.frame2.close()
		self.ui.frame3.close()

		## ~~~  Manager  ~~~~~~
		self.manager = Manager(self)

		## ~~~  Captura  ~~~~~~
		self.capture = Capture(self)
		self.connect(self.capture, QtCore.SIGNAL('captureClosed()'), self.captureClosed)
		self.capture.hide()

		## ~~~  Details  ~~~~~~
		# Se crean al ser solicitados

		## ~~~  OuterSplitter  ~~~~~~
		self.ui.outerSplitter = Splitter(QtCore.Qt.Vertical, self)

		## ~~~  InnerSplitter  ~~~~~~
		self.ui.innerSplitter = Splitter(QtCore.Qt.Horizontal, self.ui.outerSplitter)
		self.ui.innerSplitter.insertWidget(0, self.manager)
		self.ui.innerSplitter.setSizes([0, 1])
		#~ self.ui.verticalLayout.addWidget(self.ui.innerSplitter)

		self.ui.outerSplitter.insertWidget(0, self.ui.innerSplitter)
		self.ui.outerSplitter.insertWidget(1, self.capture)
		self.connect(self.ui.outerSplitter.handle(1), QtCore.SIGNAL('handlePressed'), self.outerHandlePressed)
		self.ui.outerSplitter.setSizes([1, 1])

		self.ui.verticalLayout.addWidget(self.ui.outerSplitter)

		self.connect(self.eventRouter, QtCore.SIGNAL('addProduct(QString)'), self.addProduct)
		# self.connect(self.eventRouter, QtCore.SIGNAL('productLines_changed()'), self.loadProductLines)


	def appCursor_set(self, *args):
		self.cnt.app.master.setCursor(*args)


	def form_show(self):
		"""        products.view.Master.form_show()"""

		self.container.form_show(title=u'ADMINISTRACIÓN DE {}'.format(self.cnt.title.upper()), textColor="#00C000", backgroundColor1="#A0F040", backgroundColor2="#E0FFB0", widget=self)


	def init(self):
		self.cnt.app.log2sys ( 'trace', "			Master.init()									@ products.view" )

		## ~~~  Tools Form  ~~~~
		toolsFR = OptionsFR ( None, mst=self )
		self.cnt.app.master.tools_addForm ( toolsFR, u"Productos" )

		self.manager.init()
		self.capture.init()

		self.cnt.loadProductLines()

		# self.details.init()
		# self.toolsFR.init()

		style="background-color:QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D0F8D0, stop:1 #A0F0A0);"

		self.container.menu.item_add(self.cnt.title, slot=self.form_show, style=style)

		self.container.form_add(self)

		self.cnt.app.log2sys ( 'trace', "			Master.init() - end							@ products.view\n" )


	def addProduct(self, data=''):
		# print("""    products.view.Master.addProduct()""")

		# print(123, data)
		# print(124, self.cnt.app.master)
		# print(125, self.cnt.app.master.container.currentWidget())

		self.capture.new(data)

		# if data:
			# self.caller = self.cnt.app.master.container.currentWidget()
		# else:
			# self.caller = None

		# self.showForm()

		# print("""    products.view.Master.addProduct() - END""")


	def captureClosed(self):
		self.setInnerStatus("visible")

		# self.manager.updateBotones()

		self.manager.emit(QtCore.SIGNAL("status_changed()"))


	def editProduct(self, id):
		self.capture.edit(id)

	def innerHandlePressed(self):
		# self.toggleDetails()
		pass

	def outerHandlePressed(self):
		if self.ui.outerSplitter.sizes()[0] == 0:
			self.setInnerStatus('visible')
		else:
			self.setInnerStatus('hidden')

	def setInnerStatus(self, value):
		if value == 'visible':
			self.manager.show()

		elif value == 'hidden':
			self.manager.hide()

		elif value == 'disabled':
			print ('disables')

	def showProduct(self, *args):
		"""        products.view.Master.showProduct()"""
		details = Details(self, id=args[0])
		self.cnt.app.master.addDockWidget(QtCore.Qt.RightDockWidgetArea, details)
		details.show()



class Manager(cdFrame.CDFrame):

	styleSheet = []
	styleSheet.append("")
	styleSheet.append("")
	styleSheet.append("QFrame#displayFR{border:1px outset #908878; border-top-left-radius:12px; border-top-right-radius:12px; border-bottom-left-radius:6px; border-bottom-right-radius:6px; background-color:#FFFFFF;}")
	styleSheet.append("border-radius:9px; background-color:#F0F8F0;")
	styleSheet.append("")


	def state_get(self):
		return self._state[-1]
	def state_set(self, value):
		self._state.append(value)
	state = property(state_get, state_set)
	def state_reset(self):
		self._state.pop()


	def __init__(self, *args, **kwds):

		self.mst = args[0]
		self.cnt = self.mst.cnt
		self.app = self.cnt.app

		self.app.log2sys ( 'debug', "				Manager.__init__()						@ products.view" )

		self._state = [IDLE]
		self._localAceptionIsHidden = None

		cdFrame.CDFrame.__init__(self, *args)

		self.ui = manager_ui.Ui_Form()
		self.ui.setupUi(self)

		radius = 20 + 4

		tabPosition = "BOTTOM"

		if tabPosition == "TOP":
			cornersRadius = (0, 0, radius, radius)
			cornersRadius2 = (radius, radius, 0, 0)
			self.ui.mainLayout.removeWidget(self.ui.dataFR)
			self.ui.mainLayout.addWidget(self.ui.dataFR)

		elif tabPosition == "BOTTOM":
			cornersRadius = (radius, radius, 0, 0)
			cornersRadius2 = (0, 0, radius, radius)
			self.ui.mainLayout.removeWidget(self.ui.buttonsFR)
			self.ui.mainLayout.addWidget(self.ui.buttonsFR)


		self.ui.dataFR.setStyleSheet("QFrame#dataFR{border:2px outset #908878;  border-bottom:0px; border-top-left-radius:%spx; border-top-right-radius:%spx; border-bottom-right-radius:%spx; border-bottom-left-radius:%spx; background-color:qradialgradient(cx:.5, cy:.5, radius:1.25,fx:.5, fy:.25, stop:0 #A0F0A0, stop:1 #FFFFFF);}" % cornersRadius)

		# self.buttonsStyle = "border:2px outset #908878; border-top:0px; border-top-left-radius:%spx; border-top-right-radius:%spx; border-bottom-right-radius:%spx; border-bottom-left-radius:%spx; background-color:qradialgradient(cx:.5, cy:.5, radius:1.25,fx:.5, fy:.25, stop: 0 #A0F0A0, stop:1 #FFFFFF);" % cornersRadius2
		self.buttonsStyle = "border:2px outset #908878; border-top:0px; border-top-left-radius:%spx; border-top-right-radius:%spx; border-bottom-right-radius:%spx; border-bottom-left-radius:%spx; background-color:qradialgradient(cx:.5, cy:.75, radius:1.5,fx:.5, fy:.75, stop: 0 #A0F0A0, stop:1 #FFFFFF);" % cornersRadius2

		self.ui.displayFR.setStyleSheet(self.styleSheet[2])
		self.ui.displayTA.setStyleSheet(self.styleSheet[3])

		## FILTROS
		self.ui.originCB.setStyleSheet("border-top:1px solid #908878; border-bottom:1px solid #908878;")
		self.connect(self.ui.originCB, QtCore.SIGNAL("currentIndexChanged(int)"), self.currentOriginChanged)

		self.ui.cbProveedor.setMaxVisibleItems(15)
		self.ui.cbProveedor.setStyleSheet("border-top:1px solid #908878; border-bottom:1px solid #908878;")
		self.connect(self.ui.cbProveedor, QtCore.SIGNAL("currentIndexChanged(int)"), self.currentProveedorChanged)

		## LÍNEA
		self.connect(self.ui.cbLinea, QtCore.SIGNAL("currentIndexChanged(int)"), self.selectedLineChanged)

		## CLASIFICACION
		self.ui.frClasificacion.hide()
		self.connect(self.ui.cbClasificacion, QtCore.SIGNAL('currentIndexChanged(int)'), self.currentClasificacionChanged)

		## TIPO
		# self.ui.cbTipo.setStyleSheet("background-color:#F8F8F8;")
		# self.connect(self.ui.cbTipo, QtCore.SIGNAL("currentIndexChanged(int)"), self.currentTipoChanged)
		# self.ui.kindFR

		## TABLA DE CONSULTA
		self.ui.displayTA.setShowGrid(True)
		self.ui.displayTA.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		self.ui.displayTA.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.ui.displayTA.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		labels = [u"Código", u"Nombre", u"Línea", u"Clasificación", u"Costo", u"Descuento", u"Precio", u"Existencia", u"Status"]
		self.ui.displayTA.setColumnCount(len(labels))
		self.ui.displayTA.setHorizontalHeaderLabels(labels)

		self.connect(self.ui.displayTA, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem *)"), self.itemSelected)
		self.connect(self.ui.displayTA, QtCore.SIGNAL("itemSelectionChanged()"), self.selectionChanged)
		self.connect(self.ui.displayTA, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.mostrarMenuConsulta)
		self.connect(self.ui.displayTA, QtCore.SIGNAL("resized(QEvent)"), self.resizeddisplayTA)

		self.menudisplayTA = QtGui.QMenu(self)

		font = QtGui.QFont()
		font.setPointSize(10 * self.mst.layoutZoom)
		font.setBold(True)

		self.menudisplayTA.setFont(font)

		self.menudisplayTA.setStyleSheet("QMenu{background-color:QRadialGradient(cx:.5, cy:.5, radius:1, fx:.5, fy:.5, stop:0 #FFFFFF, stop:1 #A0F0A0);} QMenu::item{color:#202020;} QMenu::item:selected{color:#000000; background-color:#90E090;}")

		## BUTTONS
		self.iconSize = QtCore.QSize(40, 40)

		self.buttonIconTextLayout = QtCore.Qt.ToolButtonTextBesideIcon

		self.font = QtGui.QFont()
		self.font.setPointSize(10 * self.mst.layoutZoom)
		self.font.setBold(True)

		## Agregar
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/Plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.aAdd = QtGui.QAction(icon, u"&Nuevo", self)
		self.aAdd.setCheckable(True)
		self.aAdd.setIconText(u"&Nuevo")
		self.connect(self.aAdd, QtCore.SIGNAL("triggered()"), self.mst.addProduct)

		self.ui.toAgregar.setStyleSheet(self.buttonsStyle)
		self.ui.toAgregar.setDefaultAction(self.aAdd)
		self.ui.toAgregar.setIconSize(self.iconSize)
		self.ui.toAgregar.setFont(self.font)
		self.ui.toAgregar.setToolButtonStyle(self.buttonIconTextLayout)

		## Edit
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/Redo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.aEdit = QtGui.QAction(icon, u"Modificar", self)
		self.aEdit.setCheckable(True)
		self.aEdit.setIconText(u"&Modificar")
		self.connect(self.aEdit, QtCore.SIGNAL("triggered()"), self.edit)

		self.ui.toModificar.setStyleSheet(self.buttonsStyle)
		self.ui.toModificar.setDefaultAction(self.aEdit)
		self.ui.toModificar.setIconSize(self.iconSize)
		self.ui.toModificar.setFont(self.font)
		self.ui.toModificar.setToolButtonStyle(self.buttonIconTextLayout)

		## Eliminar
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/Minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.aEliminar = QtGui.QAction(icon, u"Eliminar", self)
		self.aEliminar.setCheckable(True)
		self.aEliminar.setIconText(u"&Eliminar")
		self.connect(self.aEliminar, QtCore.SIGNAL("triggered()"), self.elimina)

		self.ui.toEliminar.setStyleSheet(self.buttonsStyle)
		self.ui.toEliminar.setDefaultAction(self.aEliminar)
		self.ui.toEliminar.setIconSize(self.iconSize)
		self.ui.toEliminar.setFont(self.font)
		self.ui.toEliminar.setToolButtonStyle(self.buttonIconTextLayout)

		'''
		stock_enabled = not not self.cnt.attribute(name='stock_enabled')

		if stock_enabled:

			## Kardex
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(":/Info.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
			# icon.addPixmap(QtGui.QPixmap(":/Folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
			self.aKardex = QtGui.QAction(icon, u"Kardex", self)
			self.aKardex.setCheckable(True)
			self.aKardex.setIconText(u"Kardex")
			self.connect(self.aKardex, QtCore.SIGNAL("triggered()"), self.kardex)

			self.ui.toKardex = QtGui.QToolButton(self.ui.buttonsFR)

			sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
			sizePolicy.setHorizontalStretch(3)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.ui.toKardex.sizePolicy().hasHeightForWidth())

			self.ui.toKardex.setSizePolicy(sizePolicy)

			self.ui.toKardex.setMinimumSize(QtCore.QSize(100, 0))
			self.ui.toKardex.setCheckable(True)

			self.ui.toKardex.setStyleSheet(self.buttonsStyle)
			self.ui.toKardex.setDefaultAction(self.aKardex)
			self.ui.toKardex.setIconSize(self.iconSize)
			self.ui.toKardex.setFont(self.font)
			self.ui.toKardex.setToolButtonStyle(self.buttonIconTextLayout)

			self.ui.horizontalLayout.insertWidget(4, self.ui.toKardex)

			spacerFrame = QtGui.QFrame(self.ui.buttonsFR)
			sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(1)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(spacerFrame.sizePolicy().hasHeightForWidth())
			spacerFrame.setSizePolicy(sizePolicy)
			spacerFrame.setMinimumSize(QtCore.QSize(6, 0))
			spacerFrame.setStyleSheet("border-top:2 solid #A09888;")

			self.ui.horizontalLayout.insertWidget(5, spacerFrame)



			# spacerItem2 = QtGui.QSpacerItem(36, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
			# spacerItem2.setStyleSheet("border-top:2 solid #A09888;")
			# self.ui.horizontalLayout.insertSpacerItem(5, spacerItem2)

			self.menudisplayTA.addAction(self.aKardex)

			self.connect(self, QtCore.SIGNAL('status_changed()'), self.status_update_extra)
		'''

		self.menudisplayTA.addAction(self.aAdd)
		self.menudisplayTA.addAction(self.aEdit)
		self.menudisplayTA.addAction(self.aEliminar)

		## Imprimir
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/Print.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.aImprimir = QtGui.QAction(icon, u"Imprimir", self)
		self.aImprimir.setIconText(u"&Imprimir")
		self.connect(self.aImprimir, QtCore.SIGNAL("triggered()"), self.imprime)

		self.ui.toImprimir.setStyleSheet(self.buttonsStyle)
		self.ui.toImprimir.setDefaultAction(self.aImprimir)
		self.ui.toImprimir.setIconSize(self.iconSize)
		self.ui.toImprimir.setFont(self.font)
		self.ui.toImprimir.setToolButtonStyle(self.buttonIconTextLayout)

		self.impresor = QtGui.QPrinter()

		self.connect(self.mst.eventRouter, QtCore.SIGNAL('classificationsChanged()'), self.updateClassifications)
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('productsChanged()'), self.loadConsulta)
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('suppliersChanged()'), self.loadSuppliers)
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('addProduct()'), self.mst.addProduct)

		self.connect(self, QtCore.SIGNAL('status_changed()'), self.updateBotones)

		self.ui.displayTA.sortItems(0, QtCore.Qt.AscendingOrder)

		self.upToDate = False

		self.connect(self, QtCore.SIGNAL('showed()'), self.showed)

		self.app.log2sys ( 'debug', "				Manager.__init__() - end					@ products.view" )


	def init(self):

		self.app.log2sys ( 'trace', "				Manager.init()							@ products.view" )

		stock_enabled = not not self.cnt.attribute(name='stock_enabled')

		if stock_enabled:

			## Kardex
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(":/Info.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
			# icon.addPixmap(QtGui.QPixmap(":/Folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
			self.aKardex = QtGui.QAction(icon, u"Kardex", self)
			self.aKardex.setCheckable(True)
			self.aKardex.setIconText(u"Kardex")
			self.connect(self.aKardex, QtCore.SIGNAL("triggered()"), self.kardex)

			self.ui.toKardex = QtGui.QToolButton(self.ui.buttonsFR)

			sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
			sizePolicy.setHorizontalStretch(3)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.ui.toKardex.sizePolicy().hasHeightForWidth())

			self.ui.toKardex.setSizePolicy(sizePolicy)

			self.ui.toKardex.setMinimumSize(QtCore.QSize(100, 0))
			self.ui.toKardex.setCheckable(True)

			self.ui.toKardex.setStyleSheet(self.buttonsStyle)
			self.ui.toKardex.setDefaultAction(self.aKardex)
			self.ui.toKardex.setIconSize(self.iconSize)
			self.ui.toKardex.setFont(self.font)
			self.ui.toKardex.setToolButtonStyle(self.buttonIconTextLayout)

			self.ui.horizontalLayout.insertWidget(4, self.ui.toKardex)

			spacerFrame = QtGui.QFrame(self.ui.buttonsFR)
			sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(1)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(spacerFrame.sizePolicy().hasHeightForWidth())
			spacerFrame.setSizePolicy(sizePolicy)
			spacerFrame.setMinimumSize(QtCore.QSize(6, 0))
			spacerFrame.setStyleSheet("border-top:2 solid #A09888;")

			self.ui.horizontalLayout.insertWidget(5, spacerFrame)

			# spacerItem2 = QtGui.QSpacerItem(36, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
			# spacerItem2.setStyleSheet("border-top:2 solid #A09888;")
			# self.ui.horizontalLayout.insertSpacerItem(5, spacerItem2)

			self.menudisplayTA.addAction(self.aKardex)

			self.connect(self, QtCore.SIGNAL('status_changed()'), self.status_update_extra)


		self.loadOrigins()

		self.loadSuppliers()

		self.updateClassifications()

		self.cnt.loadProductLines()

		self.productKinds_load()

		self.productStatus_load()

		self.app.log2sys ( 'trace', "				Manager.init() - end					@ products.view" )


	def currentId(self):
		if self.ui.displayTA.currentRow() != -1:
			id = self.ui.displayTA.item(self.ui.displayTA.currentRow(), 0).data(1000)
		else:
			id = None
		return id

	def currentClasificacionChanged(self, index):
		self.upToDate = False
		self.data_update()

	def currentOriginChanged(self, index):
		self.upToDate = False
		self.data_update()

	def currentProveedorChanged(self, index):
		self.upToDate = False
		self.data_update()

	def currentTipoChanged(self, index):
		self.upToDate = False
		self.data_update()

	def edit(self):
		"""products.view.Manager.edit()"""
		if self.ui.displayTA.currentRow() < 0:
			result = QtGui.QMessageBox.information(self, u"Empresa Básica - Modificar producto", u"Selecciona el PRODUCTO que quieres Modificar", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
		else:
			self.setCursor(QtCore.Qt.WaitCursor)
			id = self.ui.displayTA.item(self.ui.displayTA.currentRow(), 0).data(1000)
			self.mst.editProduct(id)
			self.setCursor(QtCore.Qt.ArrowCursor)

	def elimina(self):
		if self.ui.displayTA.currentRow() < 0:
			result = QtGui.QMessageBox.information(self, u"Empresa Básica - Eliminar producto", u"Selecciona el PRODUCTO que quieres eliminar", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
		else:
			id = self.ui.displayTA.item(self.ui.displayTA.currentRow(), 0).data(1000)
			aception = self.cnt.model.getAception(id=id)
			result = QtGui.QMessageBox.warning(self, u"Empresa Básica - Eliminar producto", u"¿Realmente quieres eliminar el Producto\n\n%s?" % aception['name'], QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if result == QtGui.QMessageBox.Yes:
				self.cnt.model.elimina(id=id)
				self.mst.eventRouter.emit(QtCore.SIGNAL("productsChanged()"))

	def findData(self, data):
		index = -1
		for row in range(self.ui.displayTA.rowCount()):
			if self.ui.displayTA.item(row, 0).data(1000)==data:
				index = row
		return index

	def imprime(self):
		dialogoImpresora = QtGui.QPrintDialog(self.impresor)
		if dialogoImpresora.exec_() == QtGui.QDialog.Accepted:
			margenHorizontal, margenVertical = [10, 10]
			pageNo = 1
			# result = QtGui.QMessageBox.information(self, u"Empresa Básica - Impresión de pedido", u"Imprimiendo ...", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
			painter = QtGui.QPainter(self.impresor)
			font1 = QtGui.QFont("courier", 10)
			font1.setBold(True)
			font2 = QtGui.QFont("courier", 9)
			font3 = QtGui.QFont("Courier", 12)
			font3.setBold(True)

			header = []
			margenX, margenY = [25, 75]
			## HEADER
			x, y = [25, 0]
			header.append([self.impresor.paperRect().width()/2-100, margenY+y, u"Catálogo de Productos", font3])
			x, y = [400, 50]
			header.append([self.impresor.paperRect().width()-200, margenY+y, u"Fecha: %s" % QtCore.QDate().currentDate().toString('dd MMM yyyy'), font1])

			x, y = [0, 100]
			header.append([margenX+x, margenY+y, u"    Código        Nombre                       Clasificación       Cantidad   Precio    Exist", font1])

			tabla = self.ui.displayTA

			x, y = [0, 125]
			contenido = []
			footer = []
			offset = 0
			for row in range(tabla.rowCount()):
				if offset == 0:
					contenido.extend(header)
				contenido.append([margenX+x    , margenY+y+offset, str(row+1), font2])
				contenido.append([margenX+x+40 , margenY+y+offset, tabla.item(row, 0).text(), font2])      # Código
				contenido.append([margenX+x+150, margenY+y+offset, tabla.item(row, 1).text(), font2])      # Nombre
				contenido.append([margenX+x+375, margenY+y+offset, tabla.item(row, 2).text(), font2])      # Clasificación
				contenido.append([margenX+x+550, margenY+y+offset, tabla.item(row, 3).text(), font2])      # Cantidad
				contenido.append([margenX+x+625, margenY+y+offset, tabla.item(row, 4).text(), font2])      # Precio
				if tabla.item(row, 5):
					contenido.append([margenX+x+675, margenY+y+offset, tabla.item(row, 5).text(), font2])      # Importe
				offset += 20

				if margenY+y+offset+75 >= self.impresor.paperRect().height():
					contenido.append([self.impresor.paperRect().width()/2-50, self.impresor.paperRect().height()-50, "Hoja %s" % pageNo, font2])
					for item in contenido:
						painter.setFont(item[3])
						painter.drawText(QtCore.QPoint(margenHorizontal + item[0], margenVertical + item[1]), item[2])
					offset = 0
					contenido = []
					footer = []
					pageNo += 1
					self.impresor.newPage()

			contenido.append([self.impresor.paperRect().width()/2-50, self.impresor.paperRect().height()-50, "Hoja %s" % pageNo, font2])
			for item in contenido:
				painter.setFont(item[3])
				painter.drawText(QtCore.QPoint(margenHorizontal + item[0], margenVertical + item[1]), item[2])


	def itemSelected(self, item):
		"""products.view.Manager.itemSelected()"""
		data = self.ui.displayTA.item(item.row(), 0).data(1000)
		self.mst.showProduct(data)


	def kardex(self):
		##
		id = self.ui.displayTA.item(self.ui.displayTA.currentRow(), 0).data(1000)
		kardex = Kardex(self.mst, id=id)
		self.cnt.app.master.addDockWidget(QtCore.Qt.RightDockWidgetArea, kardex)
		result = kardex.show()


	def loadConsulta(self):
		self.upToDate = False
		self.data_update()

	def loadLines(self, lines):
		old = self.ui.cbLinea.currentIndex()    # Must change this for id or code

		self.ui.cbLinea.clear()
		self.ui.cbLinea.addItem("")
		for line in lines:
			self.ui.cbLinea.addItem(line['name'], line['id'])
		self.ui.cbLinea.setCurrentIndex(-1)

		if old > 0:
			self.ui.cbLinea.setCurrentIndex(self.ui.cbLinea.findText(old))
		else:
			self.ui.cbLinea.setCurrentIndex(0)


	def productKinds_load(self):

		self.app.log2sys ( 'debug', "				Manager.productKinds_load()				@ products.view" )

		kinds = self.cnt.productKinds()

		selected = self.cnt.app.config.pull ( 'settings', 'productList_kind' )

		# self.ui.cbTipo.clear()
		self.ui.kindCH = []
		row = 0
		col = 0
		for index, kind in enumerate(kinds):
			row = index % 2
			col = index / 2
			self.ui.kindCH.append((QtGui.QCheckBox(u'{}'.format(kind['name'])), kind['code']))
			self.ui.kindFRLY.addWidget(self.ui.kindCH[index][0], row, col)
			if selected and "{}".format(self.ui.kindCH[index][1]) in selected:
				self.ui.kindCH[index][0].setChecked(True)
			self.connect(self.ui.kindCH[index][0], QtCore.SIGNAL('stateChanged(int)'), self.selectedKindChanged)
			# self.ui.cbTipo.addItem(kind['name'], kind['code'])

		self.app.log2sys ( 'debug', "				Manager.productKinds_load() - end		@ products.view" )


	def productStatus_load(self):

		self.app.log2sys ( 'debug', "				Manager.productStatus_load()			@ products.view" )

		statuss = self.cnt.productStatuss()

		selected = self.cnt.app.config.pull ( 'settings', 'productList_status' )

		# self.ui.cbTipo.clear()
		self.ui.statusCH = []
		row = 0
		col = 0
		for index, status in enumerate(statuss):
			row = index % 2
			col = index / 2
			self.ui.statusCH.append((QtGui.QCheckBox(u'{}'.format(status['name'])), status['code']))
			self.ui.statusFRLY.addWidget(self.ui.statusCH[index][0], row, col)
			if selected and "{}".format(self.ui.statusCH[index][1]) in selected:
				self.ui.statusCH[index][0].setChecked(True)
			self.connect(self.ui.statusCH[index][0], QtCore.SIGNAL('stateChanged(int)'), self.selectedStatusChanged)
			# self.ui.cbTipo.addItem(kind['name'], kind['code'])

		self.app.log2sys ( 'debug', "				Manager.productStatus_load() - end		@ products.view" )


	def loadOrigins(self):
		# origins = self.cnt.origins()
		self.ui.originCB.clear()

		# origins = self.cnt.rols(kind='proveedor', order='name')
		# for origin in origins:
			# self.ui.originCB.addItem("%s %s" % (origin['name'], origin['name2']), origin['id'])


	def loadSuppliers(self):
		suppliers = self.cnt.suppliers()
		self.ui.cbProveedor.clear()
		if not self.mst._localAceptionIsHidden:
			self.ui.cbProveedor.addItem("Local", self.app.holder['id'])
		for supplier in suppliers:
			self.ui.cbProveedor.addItem("%s %s" % (supplier['person']['name'], supplier['person']['name2']), supplier['id'])


	def mostrarMenuConsulta(self, pos):
		pos = self.ui.displayTA.mapToGlobal(pos)
		self.menudisplayTA.popup(pos)


	def resizeddisplayTA(self, event):
		"""products.view.Manager.resizeddisplayTA()"""
		headerWidth = self.ui.displayTA.width()-self.ui.displayTA.verticalHeader().width()-self.ui.displayTA.verticalScrollBar().width()
		self.ui.displayTA.horizontalHeader().setMinimumWidth(headerWidth)

		porcentajes = [12, 24, 12, 12, 9, 8, 8, 6, 6]
		overflow = 0

		x = 0

		for index in range(self.ui.displayTA.horizontalHeader().count()):
			if not self.ui.displayTA.isColumnHidden(index):
				self.ui.displayTA.resizeColumnToContents(index)
				porContenido = self.ui.displayTA.columnWidth(index)
				calculado = headerWidth * porcentajes[index] / 100
				if porContenido < calculado:
					if overflow:
						offset = calculado - porContenido
						if offset > overflow:
							calculado = calculado - overflow
							overflow = 0
						else:
							overflow -= offset
							calculado = porContenido
					x += calculado
					self.ui.displayTA.setColumnWidth(index, calculado)
				else:
					overflow += porContenido - calculado


	def selectedLineChanged(self):
		self.upToDate = False
		self.data_update()

	def selectedKindChanged(self):
		# print "products.Manager.selectedKindChanged()"
		kinds = self.cnt.productKinds()
		kindList = ""
		for kind in self.ui.kindCH:
			if kind[0].isChecked():
				kindList += "{}, ".format(kind[1])
		kindList = kindList.rstrip(', ')
		selected = self.cnt.app.config.push('settings', 'productList_kind', kindList)
		self.upToDate = False
		self.data_update()

	def selectedStatusChanged(self):
		# print "products.Manager.selectedStatusChanged()"
		statuss = self.cnt.productStatuss()
		statusList = ""
		for status in self.ui.statusCH:
			if status[0].isChecked():
				statusList += "{}, ".format(status[1])
		statusList = statusList.rstrip(', ')
		selected = self.cnt.app.config.push('settings', 'productList_status', statusList)
		self.upToDate = False
		self.data_update()

	def selectionChanged(self):
		if self.ui.displayTA.currentRow() != -1:
			id = self.ui.displayTA.item(self.ui.displayTA.currentRow(), 0).data(1000)
			if self.mst.capture.isVisible():
				if self.mst.capture.mode() == 'edit':
					diferent = True
					if self.mst.capture.old['id'] == id:
						diferent = False
					else:
						pass
						# if len(self.mst.capture.old)-1:
							# if self.mst.capture.old[1].id == id:
								# diferent = False
							# else:
								# if self.mst.capture.isModified():
									# result = QtGui.QMessageBox.warning(self, u"Empresa Básica - Modificación de Producto", u"La captura de Producto tiene cambios\n\n¿Quieres Guardar los cambios para %s %s %s?" % (self.mst.capture.old.code, self.mst.capture.old.name, self.mst.capture.old.product.clasificacion), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
									# if result == QtGui.QMessageBox.Yes:
										# self.mst.capture.save(hide=False)
										# self.emit(QtCore.SIGNAL("changed()"))
					if diferent:
						self.mst.editProduct(id)

		# self.updateBotones()

		self.emit(QtCore.SIGNAL("status_changed()"))


	def setCurrentId(self, id):
		if not id is None:
			self.ui.displayTA.setCurrentItem(self.ui.displayTA.item(self.findData(id), 0))


	def showed(self):
		# print "products.igu.Manager.showed()"
		self.data_update()
		self.cnt.information_set(u"")


	def status_update_extra(self):
		self.aKardex.setChecked(False)

		mensajesKardex = u""

		if self.cnt.productsCount() == 0:
			mensajesKardex += u"No hay productos registrados\n"

		if self.ui.displayTA.rowCount() == 0:
			mensajesKardex += u"No hay productos desplegados\n"
		else:
			if self.ui.displayTA.currentRow() == -1:
				mensajesKardex += u"Selecciona el producto para mostrar el kardex\n"

		if mensajesKardex:
			self.aKardex.setEnabled(False)
			self.aKardex.setToolTip(mensajesKardex.rstrip("\n"))
		else:
			self.aKardex.setEnabled(True)
			self.aKardex.setToolTip(u"Presiona para mostrar el kardex")




	def updateBotones(self):
		if not self.mst.capture.isVisible():
			self.aAdd.setChecked(False)
			self.aEdit.setChecked(False)
		self.aEliminar.setChecked(False)

		mensajesFiltros = u""
		mensajesAdd = u""
		mensajesModificar = u""
		mensajesEliminar = u""
		mensajesImprimir = u""

		supplierKind = self.cnt.attribute(category='rolKind', name=u'supplier')

		if self.cnt.suppliersCount() == 0:
			self.ui.frProveedor.setEnabled(False)
			self.ui.cbProveedor.setToolTip(u"No hay proveedores registrados")
		else:
			self.ui.frProveedor.setEnabled(True)
			self.ui.cbProveedor.setToolTip(u"")

		if self.cnt.productsCount() == 0:
			mensajesFiltros += u"No hay productos registrados\n"
			mensajesModificar += u"No hay Productos registrados\n"
			mensajesEliminar += u"No hay productos registrados\n"

		if self.ui.displayTA.rowCount() == 0:
			mensajesModificar += u"No hay productos desplegados\n"
			mensajesEliminar += u"No hay Productos desplegados\n"
			mensajesImprimir += u"No hay productos desplegados\n"
		else:
			if self.ui.displayTA.currentRow() == -1:
				mensajesModificar += u"Selecciona el Producto que quieres modificar\n"
				mensajesEliminar += u"Selecciona el Producto que quieres eliminar\n"

		if mensajesFiltros:
			self.ui.frFiltros.setEnabled(False)
			self.ui.frFiltros.setToolTip(mensajesFiltros.rstrip("\n"))
		else:
			self.ui.frFiltros.setEnabled(True)
			self.ui.frFiltros.setToolTip(u"")

		if mensajesAdd:
			self.aAdd.setEnabled(False)
			self.aAdd.setToolTip(mensajesAdd.rstrip("\n"))
		else:
			self.aAdd.setEnabled(True)
			self.aAdd.setToolTip(u"Presiona para registrar un Producto nuevo")

		if mensajesModificar:
			self.aEdit.setEnabled(False)
			self.aEdit.setToolTip(mensajesModificar.rstrip("\n"))
		else:
			self.aEdit.setEnabled(True)
			self.aEdit.setToolTip(u"Presiona para modificar los datos del Producto seleccionado")

		if mensajesEliminar:
			self.aEliminar.setEnabled(False)
			self.aEliminar.setToolTip(mensajesEliminar.rstrip("\n"))
		else:
			self.aEliminar.setEnabled(True)
			self.aEliminar.setToolTip(u"Presiona para eliminar el producto seleccionado")

		if mensajesImprimir:
			self.aImprimir.setEnabled(False)
			self.aImprimir.setToolTip(mensajesImprimir.rstrip("\n"))
		else:
			self.aImprimir.setEnabled(True)
			self.aImprimir.setToolTip(u"Presiona para Imprimir los productos mostrados")


	def updateClassifications(self):
		classifications = self.cnt.productClassifications()

		old = self.ui.cbClasificacion.currentIndex()
		self.ui.cbClasificacion.clear()
		self.ui.cbClasificacion.addItem("")
		for classification in classifications:
			self.ui.cbClasificacion.addItem(classification['name'], classification['id'])

		if old > 0:
			self.ui.cbClasificacion.setCurrentIndex(self.ui.cbClasificacion.findText(old))
		else:
			self.ui.cbClasificacion.setCurrentIndex(0)


	def data_update(self):
		# print("""\n    products.view.Manager.data_update()""")

		if self.isVisible() and not self.upToDate and self.state is IDLE:
			self.mst.appCursor_set(QtCore.Qt.WaitCursor)

			filtros = {}

			if self.ui.originCB.currentIndex() >= 0:
				filtros['origin_id'] = self.ui.originCB.currentData()

			if self.ui.cbProveedor.currentIndex() > 0:
				filtros['rol_id'] = self.ui.cbProveedor.currentData()
			else:
				filtros['rol_id'] = self.cnt.app.holder['id']

			## Line
			if self.ui.cbLinea.currentIndex() > 0:
				filtros['line'] = self.ui.cbLinea.currentData()

			if self.ui.cbClasificacion.currentIndex() > 0:
				filtros['clasificacion_id'] = self.ui.cbClasificacion.currentData()


			## TIPO
			filter = []
			for index in range(self.ui.kindFRLY.count()):
				if self.ui.kindCH[index][0].isChecked():
					filter.append(self.ui.kindCH[index][1])
			if filter:
				filtros['kind'] = {'code':filter}

			## status
			filter = []
			for index in range(self.ui.statusFRLY.count()):
				if self.ui.statusCH[index][0].isChecked():
					filter.append(self.ui.statusCH[index][1])
			if filter:
				filtros['status'] = {'code':filter}

			old = self.currentId()

			# print(45001, filtros)

			products = self.cnt.aceptionsForSelect(**filtros)

			# print(len(products))

			self.ui.displayTA.setRowCount(0)
			self.ui.displayTA.setSortingEnabled(False)

			for row, product in enumerate(products):

				# print(row, product)

				aception = [ x for x in product['aceptions'] if x['rol']['id'] == self.ui.cbProveedor.currentData() ][0]

				try:
					self.ui.displayTA.insertRow(row)

					col = 0
					item = cdTableWidgetItem.CDTableWidgetItem(aception['code'])
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					item.setData(1000, aception['product_id'])
					self.ui.displayTA.setItem(row, 0, item)

					col = 1
					item = cdTableWidgetItem.CDTableWidgetItem(aception['name'])
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					self.ui.displayTA.setItem(row, 1, item)

					col = 2
					if product['lines']:
						item = QtGui.QTableWidgetItem(product['lines'][0]['name'])
						item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
						self.ui.displayTA.setItem(row, 2, item)

					col = 3
					# if aception['classification']:
						# item = QtGui.QTableWidgetItem(aception['classification']['name'])
						# item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
						# self.ui.displayTA.setItem(row, 3, item)

					col = 4
					## COSTO
					if filtros['rol_id'] == self.cnt.app.holder['id']:
						item = QtGui.QTableWidgetItem("{}".format(Decimal(product['meancost']).quantize(Decimal('0.0001'))))
					elif aception['cost']:
						item = QtGui.QTableWidgetItem("%8.4f" % aception['cost'])
					else:
						item = QtGui.QTableWidgetItem("")
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
					self.ui.displayTA.setItem(row, 4, item)

					col = 5
					## Descuento
					if aception['rol']['id'] == self.cnt.app.holder['id']:
						if aception['individualdiscount']:
							item = QtGui.QTableWidgetItem("%8.2f" % aception['individualdiscount'])
						else:
							item = QtGui.QTableWidgetItem("0")
					else:
						if aception['generaldiscount']:
							item = QtGui.QTableWidgetItem("%8.2f" % aception['generaldiscount'])
						else:
							item = QtGui.QTableWidgetItem("0")
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
					self.ui.displayTA.setItem(row, 5, item)

					col = 6
					## PRECIOS
					priceText = ""
					if 'prices' in product:
						for index, rango in enumerate ( self.cnt.activePriceRules ) :
							priceZero = [price for price in product['prices'] if int(price['reference'])==rango['id']]

							if priceZero:
								price = priceZero[0]

								# priceText += "%8.4f, " % price['value']
								priceText += "{}".format(Decimal(price['value']).quantize(Decimal('0.0001')))

					col = 6.5
					if priceText:
						item = QtGui.QTableWidgetItem(priceText.rstrip(', '))
					else:
						item = QtGui.QTableWidgetItem("")

					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
					self.ui.displayTA.setItem(row, 6, item)

					col = 7
					if 'current' in product:
						item = QtGui.QTableWidgetItem("%8.f" % product['current'])
					else:
						item = QtGui.QTableWidgetItem("")
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
					self.ui.displayTA.setItem(row, 7, item)

					col = 8
					if product['status']:
						item = QtGui.QTableWidgetItem('{}'.format(product['status']['name']))
					else:
						item = QtGui.QTableWidgetItem('')
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
					self.ui.displayTA.setItem(row, 8, item)


				except:
					print ("ERROR @ products.view.Manager.data_update()")
					print (sys.exc_info())
					print (col)
					# print product
					print (aception)
					print

			self.ui.displayTA.setSortingEnabled(True)

			self.setCurrentId(old)

			# self.updateBotones()

			self.emit(QtCore.SIGNAL("status_changed()"))

			self.upToDate = True

			self.mst.appCursor_set(QtCore.Qt.ArrowCursor)

		# print("""    products.view.Manager.data_update() - END""")



class Capture(QtGui.QFrame):

	def __init__(self, *args, **kwds):

		self.mst = args[0]
		self.cnt = self.mst.cnt
		self.app = self.cnt.app

		self._state = [IDLE]
		self.setMode(None)

		QtGui.QFrame.__init__(self, *args)

		self.ui = capture_ui.Ui_Form()

		self.ui.setupUi(self)

		self.old = None

		self.ui.aceptionsFR = Aceptions(self)

		self.ui.contentsLY.addWidget(self.ui.aceptionsFR)


		self.font = QtGui.QFont()
		self.font.setBold(True)
		self.font.setPointSize(11 * self.mst.layoutZoom)

		labelFont = QtGui.QFont()
		labelFont.setBold(True)
		labelFont.setPointSize(10 * self.mst.layoutZoom)

		style = "background-color:qlineargradient(x1:.5, y1:0, x2:.5, y2:1, stop:0 #E0E0F0, stop:.2 #F8F8FF, stop:.8 #F4F4FC, stop:1 #D0D0E0); border-radius:0px;"
		self.style2 = "background-color:qlineargradient(x1:0, y1:.5, x2:1, y2:.5, stop:0 #E0E0F0, stop:.2 #F8F8FF, stop:.8 #F4F4FC, stop:1 #D0D0E0); border-radius:0px;"
		self.style3 = "background-color:qlineargradient(x1:0, y1:.5, x2:1, y2:.5, stop:0 #D0C8D0, stop:.2 #E0E0E0, stop:.8 #DCDCDC, stop:1 #C0B8C0); border-radius:0px;"
		labelStyle = "color:#FFFFFF; background-color:qlineargradient(x1:.5, y1:0, x2:.5, y2:1, stop:0 #80A0FF, stop:.2 #90B0FF, stop:.8 #90B0FF, stop:1 #7080F0); border-top-left-radius:4px; border-bottom-left-radius:4px;"
		labelStyle2 = "color:#FFFFFF; background-color:qlineargradient(x1:0, y1:.5, x2:1, y2:.5, stop:0 #80A0FF, stop:.2 #90B0FF, stop:.8 #90B0FF, stop:1 #7080F0); border-top-left-radius:4px; border-top-right-radius:4px;"

		self.ui.titulo.setFrameShape(QtGui.QFrame.Panel)
		self.ui.titulo.setFrameShadow(QtGui.QFrame.Sunken)
		self.ui.titulo.setStyleSheet("background-color:qlineargradient(x1:.5, y1:0, x2:.5, y2:1, stop:0 #F0F0E0, stop:.5 #D0D0D0, stop:1 #F0F0E0); border-top-left-radius: 3px; border-top-right-radius: 3px;")

		## ORIGEN
		self.ui.originLA.setFont(labelFont)
		self.ui.originLA.setStyleSheet(labelStyle)
		self.ui.originLA.setText('Fabricante')

		self.ui.originCB.setFont(self.font)
		self.ui.originCB.setStyleSheet(style)
		self.connect(self.ui.originCB, QtCore.SIGNAL('currentIndexChanged(int)'), self.originChanged)

		## AUXILIARY CODE
		self.ui.laCodigo2.setFont(labelFont)
		self.ui.laCodigo2.setStyleSheet(labelStyle)

		self.ui.edCodigo2.setFont(self.font)
		self.ui.edCodigo2.setAllowedLengths(2, 20)
		self.ui.edCodigo2.setMessagePrefix(u"El código auxiliar")
		self.ui.edCodigo2.setStyleSheet(style)
		self.ui.edCodigo2.setSymbols('-_/" ')
		self.connect(self.ui.edCodigo2, QtCore.SIGNAL("textEdited(QString)"), self.updateStatus)

		## OWN CODE
		# self.ui.grCodigo.setStyleSheet("color:#4040C0")
		self.ui.laCodigo.setFont(labelFont)
		self.ui.laCodigo.setStyleSheet(labelStyle)
		self.ui.laCodigo.setText(u'Código\npropio')

		self.ui.edCodigo.setFont(self.font)
		self.ui.edCodigo.setAllowedLengths(2, 20)
		self.ui.edCodigo.setMessagePrefix(u"El código propio")
		self.ui.edCodigo.setStyleSheet(style)
		self.ui.edCodigo.setSymbols('-_/" ')
		self.connect(self.ui.edCodigo, QtCore.SIGNAL("textEdited(QString)"), self.updateStatus)

		## UNIVERSAL CODE
		self.ui.upcLA.setFont(labelFont)
		self.ui.upcLA.setStyleSheet(labelStyle)
		self.ui.upcLA.setText(u'Código\nuniversal')

		self.ui.upcED.setFont(self.font)
		self.ui.upcED.setAllowedLengths(10, 20)
		self.ui.upcED.setMessagePrefix(u"El código universal")
		self.ui.upcED.setStyleSheet(style)
		self.ui.upcED.setOnlyNumbers(True)
		self.connect(self.ui.upcED, QtCore.SIGNAL("textEdited(QString)"), self.updateStatus)

		## Nombre
		self.ui.nameLA.setFont(labelFont)
		self.ui.nameLA.setStyleSheet(labelStyle)

		self.ui.edNombre.setFont(self.font)
		self.ui.edNombre.setAllowedLengths(4, 60)
		self.ui.edNombre.setCapitalized(True)
		self.ui.edNombre.setMessagePrefix(u"El nombre")
		self.ui.edNombre.setStyleSheet(style)
		self.ui.edNombre.setSymbols(u"""-+_.,#"'/*°|$%&()[] """)
		self.connect(self.ui.edNombre, QtCore.SIGNAL("textEdited(QString)"), self.nombreEditado)

		## ~~~~  STATUS  ~~~~
		self.ui.statusLA.setFont(labelFont)
		self.ui.statusLA.setStyleSheet(labelStyle)
		# self.ui.statusCBstatusCB.hide()
		# self.ui.statusCB.setFont(self.font)
		# self.connect(self.ui.statusCB, QtCore.SIGNAL('currentIndexChanged(int)'), self.updateStatus)
		self.ui.statusSE.setStyleSheet(style)
		# self.ui.statusSE.setMaximumWidth(150)
		self.connect(self.ui.statusSE, QtCore.SIGNAL('changed()'), self.updateStatus)

		# self.ui.statusSE.hide()


		## ~~~~  CLASSIFICATION  ~~~~
		self.ui.classificationCB.setStyleSheet(style)
		self.ui.divisionLA.setStyleSheet(labelStyle)
		self.ui.divisionCB.setStyleSheet(style)
		self.connect(self.ui.divisionCB, QtCore.SIGNAL("currentIndexChanged(int)"), self.division_update)
		self.ui.brandLA.setStyleSheet(labelStyle)
		self.ui.brandCB.setStyleSheet(style)
		self.connect(self.ui.brandCB, QtCore.SIGNAL("currentIndexChanged(int)"), self.brand_update)
		self.ui.lineLA.setStyleSheet(labelStyle)
		self.ui.lineCB.setStyleSheet(style)
		self.connect(self.ui.lineCB, QtCore.SIGNAL("currentIndexChanged(int)"), self.line_update)
		self.ui.familyLA.setStyleSheet(labelStyle)
		self.ui.familyCB.setStyleSheet(style)
		self.connect(self.ui.familyCB, QtCore.SIGNAL("currentIndexChanged(int)"), self.family_update)
		self.ui.modelLA.setStyleSheet(labelStyle)
		self.ui.modelCB.setStyleSheet(style)
		self.connect(self.ui.modelCB, QtCore.SIGNAL("currentIndexChanged(int)"), self.model_update)


		## ~~~  KINDS  ~~~~~~
		self.ui.kindLA.setFont(labelFont)
		self.ui.kindLA.setStyleSheet(labelStyle)

		self.ui.kindCB.setFont(self.font)
		self.ui.kindCB.setStyleSheet(style)
		self.connect(self.ui.kindCB, QtCore.SIGNAL('currentIndexChanged(int)'), self.tipoSeleccionado)

		## ~~~  UNITS  ~~~~~~
		self.ui.unitLA.setFont(labelFont)
		self.ui.unitLA.setStyleSheet(labelStyle)

		self.ui.unitCB.setFont(self.font)
		self.ui.unitCB.setStyleSheet(style)
		self.connect(self.ui.unitCB, QtCore.SIGNAL('currentIndexChanged(int)'), self.unitChanged)


		## ~~~  STOCK LEVELS  ~~~~~~

		## ~~~  Mínimum
		self.ui.minimumLA.setFont(labelFont)
		self.ui.minimumLA.setStyleSheet(labelStyle)

		self.ui.minimumED.setFont(self.font)
		self.ui.minimumED.setStyleSheet(style)
		self.ui.minimumED.setRange(0.00, 9999.99)
		self.connect(self.ui.minimumED, QtCore.SIGNAL("editingFinished()"), self.updateStatus)

		## ~~~  Maximum
		self.ui.maximumLA.setFont(labelFont)
		self.ui.maximumLA.setStyleSheet(labelStyle)

		self.ui.maximumED.setFont(self.font)
		self.ui.maximumED.setStyleSheet(style)
		self.ui.maximumED.setRange(0.00, 9999.99)
		self.connect(self.ui.maximumED, QtCore.SIGNAL('editingFinished()'), self.updateStatus)

		## ~~~  Current stock
		self.ui.laActual.setFont(labelFont)
		self.ui.laActual.setStyleSheet(labelStyle)

		self.ui.actualED.setFont(self.font)
		self.ui.actualED.setStyleSheet(style)
		self.connect(self.ui.actualED, QtCore.SIGNAL('editingFinished()'), self.updateStatus)


		## ~~~  COSTS  ~~~~~~
		self.ui.meanCostLA.setFont(labelFont)
		self.ui.meanCostLA.setStyleSheet(labelStyle)

		self.ui.edCostoPromedio.setFont(self.font)
		self.ui.edCostoPromedio.setStyleSheet(self.style2)
		self.ui.edCostoPromedio.setDecimals(4)
		self.ui.edCostoPromedio.setRange(0.00, 99999.9999)
		self.connect(self.ui.edCostoPromedio, QtCore.SIGNAL('editingFinished()'), self.calcularCosto)

		## ~~~  Net costo
		self.ui.netCostLA.setFont(labelFont)
		self.ui.netCostLA.setStyleSheet(labelStyle)

		self.ui.edCostoNeto.setFont(self.font)
		self.ui.edCostoNeto.setStyleSheet(self.style2)
		self.ui.edCostoNeto.setDecimals(4)
		self.connect(self.ui.edCostoNeto, QtCore.SIGNAL('textEdited(QString)'), self.calculatePrice)

		## ~~~  TAXES  ~~~~~~
		self.ui.taxesLA.setStyleSheet(labelStyle)
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.ui.taxesCH.sizePolicy().hasHeightForWidth())
		self.ui.taxesCH.setSizePolicy(sizePolicy)
		self.connect(self.ui.taxesCH, QtCore.SIGNAL('changed()'), self.calcularCosto)

		##  ~~~  MARGIN  ~~~~~~
		self.ui.baseMarginLA.setFont(labelFont)
		self.ui.baseMarginLA.setStyleSheet(labelStyle)

		self.ui.baseED.setFont(self.font)
		self.ui.baseED.setStyleSheet(self.style2)
		self.connect(self.ui.baseED, QtCore.SIGNAL('textEdited(QString)'), self.calculatePrice)


		## ~~~  PRICES  ~~~~~~
		global MARGIN_ADJUST, MARGIN_DISCOUNT, MARGIN_CALC, PRICE_CALC, MARGIN_FINAL, PRICE_FINAL

		MARGIN_ADJUST, MARGIN_DISCOUNT, MARGIN_CALC, PRICE_CALC, MARGIN_FINAL, PRICE_FINAL = range(6)

		self.ui.priceAdjustmentLA.setStyleSheet(labelStyle)
		self.ui.priceDiscountLA.setStyleSheet(labelStyle)
		self.ui.calculatedMarginFR.setStyleSheet(labelStyle)
		self.ui.calculatedPriceLA.setStyleSheet(labelStyle)
		self.ui.finalMargenLA.setStyleSheet(labelStyle)
		self.ui.finalPriceLA.setStyleSheet(labelStyle)

		self.marginAdjust = []

		## ~~~  COMMENT  ~~~~~~
		self.ui.comentarios.show()

		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/Info.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.ui.boComentarios.setIcon(icon)
		self.ui.boComentarios.setIconSize(QtCore.QSize(32, 32))
		# self.ui.boComentarios.setText(u"Ocultar información")
		self.ui.boComentarios.status = 'on'
		self.connect(self.ui.boComentarios, QtCore.SIGNAL('clicked()'), self.toggleComentarios)

		self.toggleComentarios()

		## ~~~  SAVE  ~~~~~~
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/Check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.ui.boGuardar.setIcon(icon)
		self.ui.boGuardar.setIconSize(QtCore.QSize(32, 32))
		self.ui.boGuardar.setDefault(True)
		self.ui.boGuardar.setEnabled(False)
		self.connect(self.ui.boGuardar, QtCore.SIGNAL("clicked()"), self.save)

		## ~~~  CANCEL  ~~~~~~
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/Cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.ui.boCancelar.setIcon(icon)
		self.ui.boCancelar.setIconSize(QtCore.QSize(32, 32))
		self.connect(self.ui.boCancelar, QtCore.SIGNAL("clicked()"), self.cancela)

		## ~~~  BROADCAST  ~~~~~~
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('supppliersChanged()'), self.updateOrigins)
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('useLine_changedTo(bool)'), self.useProductLine_update)

		self.connect(self.mst.eventRouter, QtCore.SIGNAL('mustCaptureClassificationChanged()'), self.mustCaptureClassification_update)
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('priceRangeChanged()'), self.priceRangeChanged)

		self.connect(self.mst.eventRouter, QtCore.SIGNAL('productAuxiliaryCodeUsageChanged()'), self.useAuxiliaryCode_update)
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('productOwnCodeUsageChanged()'), self.useOwnCode_update)
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('productUniversalCodeUsageChanged()'), self.useUniversalCode_update)

		self.connect(self.mst.eventRouter, QtCore.SIGNAL('captureActualPermitidaChanged'), self.canEditCurrentStock_update)

		self.setTabOrder(self.ui.originCB, self.ui.edNombre)
		self.setTabOrder(self.ui.edNombre, self.ui.edCodigo)
		self.setTabOrder(self.ui.edCodigo, self.ui.upcED)
		self.setTabOrder(self.ui.upcED, self.ui.kindCB)
		self.setTabOrder(self.ui.kindCB, self.ui.edCodigo2)
		self.setTabOrder(self.ui.edCodigo2, self.ui.unitCB)
		self.setTabOrder(self.ui.unitCB, self.ui.minimumED)
		self.setTabOrder(self.ui.minimumED, self.ui.maximumED)
		self.setTabOrder(self.ui.maximumED, self.ui.edCostoPromedio)
		self.setTabOrder(self.ui.edCostoPromedio, self.ui.taxesCH)
		self.setTabOrder(self.ui.taxesCH, self.ui.edCostoNeto)
		self.setTabOrder(self.ui.edCostoNeto, self.ui.baseED)
		self.setTabOrder(self.ui.baseED, self.ui.boCancelar)
		self.setTabOrder(self.ui.boCancelar, self.ui.boGuardar)
		self.setTabOrder(self.ui.boGuardar, self.ui.boComentarios)
		self.setTabOrder(self.ui.boComentarios, self.ui.comentarios)

		# self.state_reset()


	def model_update(self):
		self.updateStatus()

	def models_load(self):
		family_code = self.ui.familyCB.currentData()

		models = self.cnt.models_pull(reference="000{}".format(family_code)[-3:])

		self.ui.modelCB.clear()

		for model in models:

			self.ui.modelCB.addItem(models['name'], models['code'])


	def mode(self):
		return self._mode
	def setMode(self, value):
		self._mode = value


	def useServer(self):
		return self._useServer
	def setUseServer(self, value):
		self._useServer = value


	# _taxCount = 1
	# taxes = []
	# def taxAddRequested(self):
		# f=g
		# self.taxes.ED = QtGui.QLineEdit(self.taxesCH)
		# sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
		# sizePolicy.setHorizontalStretch(0)
		# sizePolicy.setVerticalStretch(0)
		# sizePolicy.setHeightForWidth(self.taxED.sizePolicy().hasHeightForWidth())
		# self.taxED.setSizePolicy(sizePolicy)
		# self.taxED.setFrame(False)
		# self.taxED.setObjectName(_fromUtf8("taxED"))
		# self.horizontalLayout_5.addWidget(self.taxED)


	def init(self):
		self.app.log2sys ( 'trace', "				Capture.init()							@ products.view" )

		self.state = BUSY

		self.cost_id = None
		self.stock_id = None

		self.mensajes = u""
		self.mensajes2 = u""
		self.acepciones = {}

		self.setUseServer(0)

		self.useAuxiliaryCode_update()
		self.useOwnCode_update()
		self.useUniversalCode_update()
		self.canEditCurrentStock_update()

		pricesStartRow = 17
		self.marginAdjust = []
		self.marginDiscount = []
		self.marginCalc = []
		self.priceCalc = []
		self.marginFinal = []
		self.priceFinal = []

		for index, priceRule in enumerate ( self.cnt.activePriceRules ) :

			self.marginAdjust.append(cdNumberEdit.CDNumberEdit(self.ui.pricesFR))

			sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.marginAdjust[index].sizePolicy().hasHeightForWidth())

			self.marginAdjust[index].setSizePolicy(sizePolicy)

			self.marginAdjust[index].setFont(self.font)
			self.marginAdjust[index].setFrame(False)
			self.marginAdjust[index].setAlignment(QtCore.Qt.AlignCenter)
			self.marginAdjust[index].setStyleSheet(self.style2)
			self.connect(self.marginAdjust[index], QtCore.SIGNAL('textEdited(QString)'), self.calculatePrice)
			self.ui.pricesLY.addWidget(self.marginAdjust[index], 0, index+1)

			self.marginDiscount.append(cdNumberEdit.CDNumberEdit(self.ui.pricesFR))

			sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.marginDiscount[index].sizePolicy().hasHeightForWidth())

			self.marginDiscount[index].setSizePolicy(sizePolicy)

			self.marginDiscount[index].setFont(self.font)
			self.marginDiscount[index].setFrame(False)
			self.marginDiscount[index].setAlignment(QtCore.Qt.AlignCenter)
			self.marginDiscount[index].setStyleSheet(self.style2)
			self.connect(self.marginDiscount[index], QtCore.SIGNAL('textEdited(QString)'), self.calculatePrice)
			self.ui.pricesLY.addWidget(self.marginDiscount[index], 1, index+1)

			self.marginCalc.append(QtGui.QLabel(self.ui.pricesFR))

			sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.marginCalc[index].sizePolicy().hasHeightForWidth())

			self.marginCalc[index].setSizePolicy(sizePolicy)

			self.marginCalc[index].setFont(self.font)
			self.marginCalc[index].setAlignment(QtCore.Qt.AlignCenter)
			self.marginCalc[index].setStyleSheet(self.style3)

			self.ui.pricesLY.addWidget(self.marginCalc[index], 2, index+1)

			self.priceCalc.append(QtGui.QLabel(self.ui.pricesFR))

			sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.marginAdjust[index].sizePolicy().hasHeightForWidth())

			self.priceCalc[index].setSizePolicy(sizePolicy)

			self.priceCalc[index].setFont(self.font)
			self.priceCalc[index].setAlignment(QtCore.Qt.AlignCenter)
			self.priceCalc[index].setStyleSheet(self.style3)

			self.ui.pricesLY.addWidget(self.priceCalc[index], 3, index+1)

			self.marginFinal.append(QtGui.QLabel(self.ui.pricesFR))

			sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.marginAdjust[index].sizePolicy().hasHeightForWidth())

			self.marginFinal[index].setSizePolicy(sizePolicy)

			self.marginFinal[index].setFont(self.font)
			self.marginFinal[index].setAlignment(QtCore.Qt.AlignCenter)
			self.marginFinal[index].setStyleSheet(self.style3)

			self.ui.pricesLY.addWidget(self.marginFinal[index], 4, index+1)

			self.priceFinal.append(cdNumberEdit.CDNumberEdit(self.ui.pricesFR))

			sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.marginAdjust[index].sizePolicy().hasHeightForWidth())

			self.priceFinal[index].setSizePolicy(sizePolicy)

			self.priceFinal[index].setFont(self.font)
			self.priceFinal[index].setFrame(False)
			self.priceFinal[index].setAlignment(QtCore.Qt.AlignCenter)
			self.priceFinal[index].setStyleSheet(self.style2)
			self.priceFinal[index].data = None
			self.priceFinal[index].data2 = priceRule['code']

			self.connect(self.priceFinal[index], QtCore.SIGNAL('textEdited(QString)'), self.calculatePrice)

			self.ui.pricesLY.addWidget(self.priceFinal[index], 5, index+1)

		widget = self.ui.baseED

		for index, priceRule in enumerate ( self.cnt.activePriceRules ) :
			self.setTabOrder(widget, self.marginAdjust[index])
			self.setTabOrder(self.marginAdjust[index], self.marginDiscount[index])
			self.setTabOrder(self.marginDiscount[index], self.priceFinal[index])
			widget = self.priceFinal[index]

		self.updateOrigins()

		self.productKinds_load()

		self.updateUnits()

		self.updateProductStatuss()

		self.load_divisions()

		self.caller = None

		self.state_reset()

		self.clear()

		self.app.log2sys ( 'trace', "				Capture.init() - end						@ products.view" )


	def toggleServerAccess(self):
		# print "products.view.Capture.toggleServerAccess()"
		if self.ui.serverAccessTO.isChecked():
			self.setUseServer(1)
		else:
			self.setUseServer(0)


	def addLine(self):
		# print  "products.view.Capture.addLine()"

		linesStartRow = 7

		font = QtGui.QFont()
		font.setWeight(75)
		font.setBold(True)
		font.setPointSize(10 * self.mst.layoutZoom)

		rowNumber = len(self.ui.lineCBs)

		lineCB = cdComboBox.CDComboBox(self.ui.generalFR)

		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
#        sizePolicy.setHeightForWidth(lineCB.sizePolicy().hasHeightForWidth())
		lineCB.setSizePolicy(sizePolicy)

		lineCB.setEditable(True)
		lineCB.lineEdit().setStyleSheet("background-color:qlineargradient(x1:.5, y1:0, x2:.5, y2:1, stop:0 #E0E0F0, stop:.2 #F8F8Ff, stop:.8 #F4F4FC, stop:1 #D0D0E0); border-radius:0px;")
		lineCB.lineEdit().setFont(font)
		lineCB.setStyleSheet("color:#000080; background-color:#F8F8F8;")

		self.ui.generalLY.addWidget(lineCB, linesStartRow + rowNumber, 1)

		self.connect(lineCB, QtCore.SIGNAL('currentIndexChanged(int)'), self.lineaChanged)
		self.connect(lineCB.lineEdit(), QtCore.SIGNAL('editingFinished()'), self.updateStatus)

		if rowNumber > 1:
			deleteLineBU = QtGui.QPushButton(self.ui.generalFR)

			deleteLineBU.setMaximumSize(QtCore.QSize(32, 16777215))
			deleteLineBU.setMaximumSize(QtCore.QSize(24, 16777215))

			sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(deleteLineBU.sizePolicy().hasHeightForWidth())
			deleteLineBU.setSizePolicy(sizePolicy)

			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(":/Minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
			deleteLineBU.setIcon(icon)
			deleteLineBU.setIconSize(QtCore.QSize(24, 24))

			font = QtGui.QFont()
			font.setWeight(75)
			font.setBold(True)
			deleteLineBU.setFont(font)

			self.ui.generalLY.addWidget(deleteLineBU, linesStartRow + rowNumber, 1)

			self.connect(deleteLineBU, QtCore.SIGNAL('clicked()'), self.deleteLine)

			self.ui.deleteLineBUs.append(deleteLineBU)

		lineCB.data = None

		self.ui.lineCBs.append(lineCB)

		self.loadLineCBs(rowNumber)

		lineCB.setCurrentText('', initialToo=True)


	def brand_update(self):
		self.app.log2sys ( 'debug', "		Capture.brand_update()			@ products.view" )

		if self.state == IDLE:

			self.loadLines()

			brand_code = self.ui.brandCB.currentData()

			default = self.cnt.lines_pull(value='default', reference=str(brand_code)[-3:])
			if default:
				self.ui.lineCB.setCurrentData(default[0]['code'], initialToo=True)

		self.app.log2sys ( 'debug', "		Capture.brand_update() - end	@ products.view" )


	def brands_load(self):
		# print("""        products.Capture.brands_load()""")

		self.state = BUSY

		division_code = self.ui.divisionCB.currentData()

		brands = self.cnt.brands_pull(reference=["{}".format(division_code)[-3:], '000'])

		self.ui.brandCB.clear()

		for brand in brands:

			self.ui.brandCB.addItem(brand['name'], brand['code'])

		self.state_reset()

		self.brand_update()

		# print("""        products.Capture.brands_load() - END""")


	def codeEdited(self):
		# print "products.view.Capture.codeEdited()"
		self.updateStatus()

	def cancela(self):
		self.clear()
		self.hide()
		# self.ui.frLocal.setEnabled(True)
		# self.ui.frLocal.setToolTip(u"")
		self.emit(QtCore.SIGNAL("captureClosed()"))


	def calcularCosto(self):
		# print("""products.Capture.calcularCosto()""")

		general = Decimal('0.00')
		special = Decimal('0.00')

		"""
		for tax in product['taxes']:
			self.ui.taxesCH.add(tax['code'], initialToo=True)
			if tax['reference'] == 'default':
				general = tax['value']
			if tax['reference'] == 'special':
				special = tax['value']
		self.ui.edCostoNeto.setValue(product['meancost']/(100+special)*(100+general), initialToo=True)
		"""

		taxes = self.cnt.taxes()
		# print(taxes)
		# print(self.ui.taxesCH.data())

		general0 = [x for x in taxes if 'default' in x['reference'] and x['code'] in self.ui.taxesCH.data()]
		# print(general0)
		if general0:
			general = general0[0]['value']
		#! Asumes only one special tax
		special0 = [x for x in taxes if x['reference'] == 'special' and x['code'] in self.ui.taxesCH.data()]
		# print(special0)
		if special0:
			special = special0[0]['value']

		# print(general, special)

		costoNeto = self.ui.edCostoPromedio.value() / (100+special) * (100+general)

		self.ui.edCostoNeto.setValue(costoNeto)

		self.calculatePrice()

		# print("""products.Capture.calcularCosto() - END""")


	def calcularPrecio(self, data=None):
		# print "\nproducts.igu.Capture.calcularPrecio() interveened"
		#!
		f=g

		if self.state is IDLE:
			costoNeto = self.ui.edCostoNeto.value()

			# if self.ui.chImpuesto.isChecked():
				# impuesto = self.ui.edImpuesto.value()
			# else:
			impuesto = Decimal("0.00")

			margin = self.ui.baseED.value()

			for index, priceRange in enumerate(self.cnt.activePriceRanges()):
				descuento = self.ui.discountED[index].value()
				marginF = ((100+self.ui.baseED.value()) * (100+self.ui.adjustED[index].value())/100 * (100-self.ui.discountED[index].value())/100)-100
				self.ui.netED[index].setValue(marginF)
				precio = costoNeto * (100+marginF) / 100
				oldFocused = self.focusWidget()
				old = self.ui.calcED[index].text()
				self.ui.calcED[index].setValue(precio)

			self.updateStatus()


	def calculatePrice(self, text=None):
		# print("""    products.view.Capture.calculatePrice()""")
		# print self.status

		if self.state is IDLE:
			costoNeto = self.ui.edCostoNeto.value()

			# if self.ui.chImpuesto.isChecked():
				# impuesto = self.ui.edImpuesto.value()
			# else:
			impuesto = Decimal("0.00")

			marginKind = self.cnt.attribute(category=u'system', name=u'priceMarginKind')['value']

			margin = self.ui.baseED.value()

			recalcular = self.cnt.attribute(name=u'recalcularPrecioAlComprar', reference=u'product',)['value']==u'1'
			sentido = self.cnt.attribute(name=u'sentidoDeCambio', reference=u'product')['value']
			allowedMarginDiff = Decimal(self.cnt.attribute(name=u'margenDeCambio', reference=u'product')['value'])
			# if sentido == u'+/-':
				# self.ui.raMasMenos.setChecked(True)
			# elif sentido == u'+':
				# self.ui.raMas.setChecked(True)

			for index, priceRule in enumerate(self.cnt.activePriceRules()):

				## Margin calculations
				base = self.ui.baseED.value()
				adjust = self.marginAdjust[index].value()
				discount = self.marginDiscount[index].value()

				if marginKind == '40421':
					calculated = ( (100+base)/100 ) / ( (100-discount)/100 ) * 100 - 100
				else:
					calculated = ( (100+base) * (100+adjust)/100 * (100-discount)/100 ) - 100

				self.marginCalc[index].setText("{}".format( calculated.quantize(Decimal('0.01')) ))

				oldFocused = self.focusWidget()
				oldPrice = self.priceCalc[index].text()

				priceCalc = (costoNeto * (100+Decimal("{}".format(self.marginCalc[index].text()))) / 100).quantize(Decimal('0.0001'))
				self.priceCalc[index].setText("{}".format(priceCalc))

				if recalcular:
					priceFinal = self.priceFinal[index].value()
					if priceFinal:
						diff = ( priceFinal - priceCalc ) / priceFinal * Decimal('100')

						if abs(diff) > allowedMarginDiff:
							if not (diff < 0 and "-" not in sentido):
								self.priceFinal[index].setStyleSheet("background-color:qlineargradient(x1:0, y1:.5, x2:1, y2:.5, stop:0 #FFE0F0, stop:.2 #FFF8FF, stop:.8 #FFF4FC, stop:1 #FFD0E0); border-radius:0px;")
						else:
							self.priceFinal[index].setStyleSheet("background-color:qlineargradient(x1:0, y1:.5, x2:1, y2:.5, stop:0 #E0E0F0, stop:.2 #F8F8FF, stop:.8 #F4F4FC, stop:1 #D0D0E0); border-radius:0px;")
					else:
						self.priceFinal[index].setValue(priceCalc)
						self.priceFinal[index].setStyleSheet("background-color:qlineargradient(x1:0, y1:.5, x2:1, y2:.5, stop:0 #E0E0F0, stop:.2 #F8F8FF, stop:.8 #F4F4FC, stop:1 #D0D0E0); border-radius:0px;")

				if costoNeto:
					marginFinal = (self.priceFinal[index].value() / costoNeto * 100).quantize(Decimal('0.01'))-Decimal('100')
				else:
					marginFinal = Decimal('0')

				self.marginFinal[index].setText("{}".format(marginFinal))

#            self.ui.pricesTA.resizeColumnToContents(3)
#            self.ui.pricesTA.resizeColumnToContents(5)

			self.updateStatus()

		# print("""    products.view.Capture.calculatePrice() - END""")


	def classification_update(self):
		# print("""        products.Capture.classification_update()""")

		# 2 steps: load classifications for context, select current

		self.state = BUSY

		division_code = self.ui.divisionCB.currentData()
		brand_code = self.ui.brandCB.currentData()
		line_code = self.ui.lineCB.currentData()
		family_code = self.ui.familyCB.currentData()

		if self.ui.familyCB.currentIndex() != -1:
			reference = '{}{}{}{}'.format(str(division_code)[-3:], str(brand_code)[-3:], str(line_code)[-3:], str(family_code)[-3:])
		elif self.ui.lineCB.currentIndex() != -1:
			reference = '{}{}{}'.format(str(division_code)[-3:], str(brand_code)[-3:], str(line_code)[-3:])
		elif self.ui.brandCB.currentIndex() != -1:
			reference = '{}{}'.format(str(division_code)[-3:], str(brand_code)[-3:])
		else:
			reference = '{}'.format(str(division_code)[-3:])

		classifications = self.cnt.classifications_pull(**{'referenceLIKE':reference})

		## Set classifications available
		self.ui.classificationCB.clear()
		for classification in classifications:
			self.ui.classificationCB.addItem(classification['name'], classification['id'])

		## Select current
		classification0 = self.cnt.classifications_pull(reference=reference)
		if classification0:
			self.ui.classificationCB.setCurrentData(classification0[0]['id'])
		else:
			self.ui.classificationCB.setCurrentText(u'{} {} {} {}'.format(self.ui.lineCB.currentText(), self.ui.brandCB.currentText(), self.ui.familyCB.currentText(), self.ui.modelCB.currentText()).rstrip())

		self.state_reset()

		# print("""        products.Capture.classification_update() - END""")


	def clasificacionSeleccionada(self, completerModelIndex=None):
		if self.state is IDLE:
			self.updateStatus()
		# else:
			# print 'skipped'


	def clear(self):
		# print("""        products.Capture.clear()""")

		self.state = BUSY

		self.ui.originCB.setCurrentIndex(-1, initialToo=True)
		self.ui.edNombre.clear()
		self.ui.edCodigo.clear()
		self.ui.edCodigo2.clear()
		self.ui.upcED.clear()

		self.ui.classificationCB.clear()

		reference = ''
		reference += str(self.ui.brandCB.currentData())[-3:]
		reference += str(self.ui.lineCB.currentData())[-3:]

		# classifications = self.cnt.classifications_pull()
		classifications = self.cnt.app.model.attributes_get(**{'category':'productLine', 'referenceLIKE':reference})

		# print(777000, classifications)

		for classification in classifications:

			self.ui.classificationCB.addItem(classification['name'], classification['id'])


		# self.brands_load()

		# default = self.cnt.brands_load(value='default')
		# if default:
			# self.ui.brandCB.setCurrentData(default[0]['code'], initialToo=True)

		self.ui.kindCB.setCurrentData(self.cnt.defaultProductKind(), initialToo=True)

		self.ui.unitCB.setCurrentData(self.cnt.defaultUnitKind()['code'])
		self.ui.minimumED.setText("0")
		self.ui.maximumED.setText("0")
		self.ui.actualED.setText("0")

		self.ui.edCostoPromedio.setText("0.00")

		self.ui.taxesCH.clear()

		self.taxes_load()

		# print(""" Must reset taxes here""")

		self.ui.edCostoNeto.setText("0.00")
		margin = self.cnt.attribute(name='defaultBaseMargin', cast_='product')
		self.ui.baseED.setValue( Decimal(margin['value']) )

		## PRECIOS
		for index, rule in enumerate ( self.cnt.activePriceRules ) :
			self.marginAdjust[index].setValue(Decimal('0'), initialToo=True)
			self.marginDiscount[index].setValue(Decimal('0'), initialToo=True)
			self.marginCalc[index].setText('')
			self.priceCalc[index].setText('')
			self.marginFinal[index].setText('')
			self.priceFinal[index].setValue(Decimal('0'), initialToo=True)
			self.priceFinal[index].setStyleSheet('background-color:qlineargradient(x1:0, y1:.5, x2:1, y2:.5, stop:0 #E0E0F0, stop:.2 #F8F8FF, stop:.8 #F4F4FC, stop:1 #D0D0E0); border-radius:0px;')

		self.ui.aceptionsFR.clear()

		self.state_reset()


		default = self.cnt.divisions_pull(value='default')

		if default:
			self.ui.divisionCB.setCurrentData(default[0]['code'], initialToo=True)

		# print("""        products.Capture.clear() - END""")


	def data(self):
		""" Regresa los datos contenidos en los widgets de captura (en
		algunos casos sólo si estan modificados), y un estatus de validez de
		formato generado por los mismos."""
		# print "    products.view.Capture.data()"

		data = {}

		# print self.mode()
		# print self.old

		if self.mode() == 'edit':
			data['id'] = self.old['id']

		if self.ui.statusSE.isModified() or self.mode() == 'add':
			data['status'] = self.ui.statusSE.currentData()
		if self.ui.originCB.isModified():
			data['origin_id'] = self.ui.originCB.currentData()

		if self.ui.edNombre.isModified():
			data['name'] = unicode(self.ui.edNombre.text())

		if self.cnt.useOwnCode:
			if self.ui.edCodigo.isModified():
				data['code'] = unicode(self.ui.edCodigo.text())

		if self.cnt.useUniversalCode():
			if self.ui.upcED.isModified():
				data['upc'] = unicode(self.ui.upcED.text())

		if self.cnt.useAuxiliaryCode():
			if self.ui.edCodigo2.isModified():
				data['code2'] = unicode(self.ui.edCodigo2.text())

		if self.ui.kindCB.isModified() or self.mode() == 'add':
			data['kind'] = {'code':self.ui.kindCB.currentData()}

		if self.ui.unitCB.isModified() or self.mode() == 'add':
			data['unit_code'] = self.ui.unitCB.currentData()

		'''
		## CLASSIFICATION
		if self.ui.cbClasificacion.isModified() or self.mode() == 'add':
			if not self.ui.cbClasificacion.isHidden():
				if self.ui.cbClasificacion.findText(self.ui.cbClasificacion.currentText()) == -1:
					data['classification'] = unicode(self.ui.cbClasificacion.currentText())
				else:
					data['classification_id'] = self.ui.cbClasificacion.currentData()


		## LINES
		lines = []

		for index, active in enumerate(self.activeLines):
			if active:
				line = {}

				widget = "self.ui.line{}CB".format(index)

				if eval("{}.isModified()".format(widget)):

					if eval("{}.currentText() == {}.itemText({}.currentIndex())".format(widget, widget, widget)):
						exec("line['id'] = {}.currentData()".format(widget))
					else:
						exec("line['name'] = unicode({}.currentText())".format(widget))

					# if eval("{}.data".format(widget)):
						# exec("line['attributeId'] = {}.data".format(widget))

					lines.append(line)

		if lines:
			data['lines'] = lines
		'''

		## LINES
		# lines = []

		# for index, lineCB in enumerate(self.ui.lineCBs):

			# line = {}

			# if lineCB.isModified():
				# if lineCB.currentText() == lineCB.itemText(lineCB.currentIndex()):
					# line['id'] = lineCB.currentData()
				# else:
					# line['name'] = unicode(lineCB.currentText())

				# if lineCB.data:
					# line['attributeId'] = lineCB.data

				# lines.append(line)

		# if lines:
			# data['lines'] = lines


		data['classification_id'] = 155

		lines = []

		if self.ui.classificationCB.isModified() or self.mode() == 'add':

			classification = {}

			if self.ui.classificationCB.currentData():
				classification['id'] = self.ui.classificationCB.currentData()
			else:
				classification['name'] = u"{}".format(self.ui.classificationCB.currentText())

				reference = "{}".format(self.ui.divisionCB.currentData())[-3:]

				if self.ui.brandCB.currentIndex() != -1:
					reference += "{}".format(self.ui.brandCB.currentData())[-3:]

				if self.ui.lineCB.currentIndex() != -1:
					reference += "{}".format(self.ui.lineCB.currentData())[-3:]

				if self.ui.familyCB.currentIndex() != -1:
					reference += "{}".format(self.ui.familyCB.currentData())[-3:]

				if self.ui.modelCB.currentIndex() != -1:
					reference += "{}".format(self.ui.modelCB.currentData())[-3:]

				classification['reference'] = reference

			lines.append(classification)

		if lines:
			data['lines'] = lines


		## STOCK
		stockChanged = False
		if self.ui.minimumED.isModified() or self.mode() == 'add':
			data['minimum'] = self.ui.minimumED.value()
			stockChanged = True

		if self.ui.maximumED.isModified() or self.mode() == 'add':
			data['maximum'] = self.ui.maximumED.value()
			stockChanged = True

		if self.ui.actualED.isModified() or self.mode() == 'add':
			data['current'] = self.ui.actualED.value()
			stockChanged = True

#        if stockChanged and self.stock_id:
#            data['stockChanged'] = self.stock_id

		## COST
		costChanged = False
		if self.ui.edCostoPromedio.isModified():
			data['meancost'] = self.ui.edCostoPromedio.value()
			costChanged = True

		## TAXES
		if self.ui.taxesCH.isModified() or self.mode() == 'add':
			if self.ui.taxesCH.data():
				taxes = []
				for code in self.ui.taxesCH.modifiedData():
					tax0 = [x for x in self.cnt.taxes() if x['code'] == code]
					if tax0:
						taxes.append({'code': code, 'value':tax0[0]['value'], 'reference':tax0[0]['reference']})
				data['taxes'] = taxes
				costChanged = True

		if self.ui.baseED.isModified() or self.mode() == 'add':
			data['margin'] = self.ui.baseED.value()
			costChanged = True

		## PRICES
		prices = []
		for index in range(len(self.priceFinal)):
			price = {}
			if self.marginAdjust[index].isModified() or self.mode() == u'add':
				price['factor1'] = self.marginAdjust[index].value()
			if self.marginDiscount[index].isModified() or self.mode() == u'add':
				price['factor2'] = self.marginDiscount[index].value()
			if self.priceFinal[index].isModified() or self.mode() == u'add':
				price['value'] = self.priceFinal[index].value()

			if price:
#                if self.priceFinal[index].data:
#                    price['id'] = self.priceFinal[index].data
				price['reference'] = self.priceFinal[index].data2
				prices.append(price)
		if prices:
			data['prices'] = prices

		## ACEPTIONS
		if self.ui.aceptionsFR.isModified():
			aceptions = self.ui.aceptionsFR.data()

			if aceptions:
				data['aceptions'] = aceptions


		return data



		'''
		## LINES
		# Ya contempla sólo datos modificados
		lines = []
		for lineCB in self.ui.lineCBs:
			line = {}
			if lineCB.isModified():
				if lineCB.currentIndex() == -1:
					line['name'] = unicode(lineCB.currentText())
				else:
					line['id'] = lineCB.currentData()
			if lineCB.data:
				line['id'] = lineCB.data
			lines.append(line)
		if lines:
			data['lines'] = lines
		'''

		## PRICES
		# Ya contempla sólo datos modificados
		prices = []
		for price in self.ui.priceFinal:
			price = {}
#        self.marginAdjust = []
#        self.marginDiscount = []
#        self.marginCalc = []
#        self.priceCalc = []
#        self.marginFinal = []
#        self.priceFinal = []

		'''
		if self.ui.lineCB.isModified():
			if lineCB.currentIndex() == -1:
				line['name'] = unicode(lineCB.currentText())
			else:
				line['id'] = lineCB.currentData()
		if lineCB.data:
			line['id'] = lineCB.data
		lines.append(line)
		if lines:
			product['lines'] = lines
		'''





		## ==== PRECIOS
		"""
		# Ya contempla sólo datos modificados
		prices = []
		for row in range(self.ui.pricesTA.rowCount()):
			price = {}
			if self.ui.pricesTA.cellWidget(row, MARGIN_ADJUST).isModified or self.mode() == 'add':
				price['factor1'] = self.ui.pricesTA.cellWidget(row, MARGIN_ADJUST).value()
			if self.ui.pricesTA.cellWidget(row, MARGIN_DISCOUNT).isModified or self.mode() == 'add':
				price['factor2'] = self.ui.pricesTA.cellWidget(row, MARGIN_DISCOUNT).value()
			if self.ui.pricesTA.cellWidget(row, PRICE_FINAL).isModified():
				price['value'] = self.ui.pricesTA.cellWidget(row, PRICE_FINAL).value()
			if price:
				if self.ui.pricesTA.item(row, 3).data(1000).toInt()[0]:
					price['id'] = self.ui.pricesTA.item(row, 3).data(1000).toInt()[0]
				price['attribute_id'] = self.ui.pricesTA.item(row, 2).data(1000).toInt()[0]
				prices.append(price)
		if prices:
			datos['prices'] = prices
		"""
		"""
		aceptions = self.ui.aceptionsTB.modifiedData()
		if aceptions:
			datos['aceptions'] = aceptions
		"""
		return data


	# def deleteLine(self):
		# index = self.ui.deleteLineBUs.index(self.sender())
		# lineCB = self.ui.lineCBs.pop(index+1)
		# self.ui.localLY.removeWidget(lineCB)
		# lineCB.setParent(None)
		# del lineCB

		# deleteBU = self.ui.deleteLineBUs.pop(index)
		# self.ui.localLY.removeWidget(deleteBU)
		# deleteBU.setParent(None)
		# del deleteBU


	def division_update(self):
		# print("""        products.Capture.division_update()""")

		if self.state is IDLE:

			self.brands_load()

			division_code = self.ui.divisionCB.currentData()

			default = self.cnt.brands_pull(value='default', reference="{}".format(division_code)[-3:])

			if default:

				self.ui.brandCB.setCurrentData(default[0]['code'], initialToo=True)

		# print("""        products.Capture.division_update() - END""")


	def load_divisions(self):
		self.app.log2sys ( 'debug', "			Capture.load_divisions()						@ products.view" )

		self.state = BUSY

		divisions = self.cnt.divisions_pull()

		self.ui.divisionCB.clear()

		for division in divisions:

			self.ui.divisionCB.addItem(division['name'], division['code'])

		self.state_reset()

		self.app.log2sys ( 'debug', "			Capture.load_divisions() - end				@ products.view" )


	def edit(self, product_id):
		# print "\n    products.view.Capture.edit()"

		self.setCursor(QtCore.Qt.WaitCursor)

		self.ui.titulo.setText(QtGui.QApplication.translate("Empresa Básica", "Modificación de Producto", None, QtGui.QApplication.UnicodeUTF8))

		self.setMode('edit')

		self.clear()

		product = self.cnt.product(id=product_id)

		self.setData(product)

		self.mst.setInnerStatus('hidden')

		self.show()

		self.mst.manager.ui.displayTA.scrollToItem(self.mst.manager.ui.displayTA.item(self.mst.manager.findData(id), 1), QtGui.QAbstractItemView.EnsureVisible)

		self.setCursor(QtCore.Qt.ArrowCursor)


	def family_update(self):
		# print("""    products.Capture.family_update()""")

		if self.state == IDLE:

			self.state = BUSY

			if self.ui.familyCB.count():

				if self.ui.familyCB.currentText() == 'reset':

					self.families_load()

				elif self.ui.familyCB.currentText() != '':

					if self.ui.familyCB.itemText(0) != 'reset':

						self.ui.familyCB.insertItem(0, 'reset')

				else:

					self.families_load()

			self.state_reset()

			self.models_load()

			self.classification_update()

		# print("""    products.Capture.family_update() - END""")


	def families_load(self):
		# print("""        products.Capture.families_load()""")

		self.state = BUSY

		brand_code = self.ui.brandCB.currentData()
		line_code = self.ui.lineCB.currentData()

		# print("{}{}".format("{}".format(brand_code)[-3:], "{}".format(line_code)[-3:]))

		families = self.cnt.families_pull(reference="{}{}".format("{}".format(brand_code)[-3:], "{}".format(line_code)[-3:]))

		self.ui.familyCB.clear()

		# noFamily = self.cnt.families_pull(reference='', name='')[0]

		# self.ui.familyCB.addItem(noFamily['name'], noFamily['code'])

		for family in families:

			self.ui.familyCB.addItem(family['name'], family['code'])

		self.ui.familyCB.setCurrentIndex(-1)

		self.state_reset()

		self.family_update()

		# print("""        products.Capture.famlies_load() - END""")


	def finished(self):
		# print "products.view.Capture.finished()"
		if not self.ui.aceptionFR_layout.slideStatus:
			# self.ui.frTituloExterno2.hide()
		# else:
			self.ui.frTituloExterno2.show()


	def isModified(self):
		# print "products.view.Capture.isModified()"

		productIsModified = False
		self.mensajes2 = u""

		if self.ui.statusSE.isModified():
			productIsModified = True
			self.mensajes2 += u'Status modificado\n'

		if self.ui.edCodigo.isModified():
			productIsModified = True
			self.mensajes2 += u"Código modificado\n"

		if self.cnt.useOwnCode:
			if self.ui.edCodigo.isModified():
				productIsModified = True
				self.mensajes2 += u'Código propio modificado\n'

		if self.cnt.useUniversalCode():
			if self.ui.upcED.isModified():
				productIsModified = True
				self.mensajes2 += u'Código universal modificado\n'

		if self.cnt.useAuxiliaryCode():
			if self.ui.edCodigo2.isModified():
				productIsModified = True
				self.mensajes2 += u'Código auxiliar modificado\n'

		if self.ui.edNombre.isModified():
			productIsModified = True
			self.mensajes2 += u"Nombre modificado\n"

		'''
		## Clasificacion - Se asume una sola clasificacion
		if self.ui.cbClasificacion.isModified():
		# if 'clasificacion' in data.keys() or data['clasificacion_id'] != oldProduct.clasificacion_id:
			productIsModified = True
			self.mensajes2 += u"Clasificación modificada\n"

		## LINES
		count = self.activeLines.count(True)
		for index, active in enumerate(self.activeLines):
			if active:
				if eval("self.ui.line{}CB.isModified()".format(index)):
					productIsModified = True
					if count == 1:
						self.mensajes2 += u"Línea modificada\n"
					else:
						self.mensajes2 += u"Línea {} modificada\n".format(index)
		'''

		# Línea - Se asume una sola línea
		# for lineCB in self.ui.lineCBs:

			# if lineCB.isModified():
				# productIsModified = True
				# self.mensajes2 += u"Linea modificada\n"

			# lineaList = [x for x in oldProduct.atributos if x.nombre==u'linea']
			# if lineaList:
				# linea = lineaList[0]
				# if data['linea'][1] != int(linea.valor):
					# testProduct = True
					# self.mensajes2 += u"Linea modificada\n"
			# else:
				# if data['linea'][0]:
					# testProduct = True
					# self.mensajes2 += u"Linea modificada\n"


		if self.ui.kindCB.isModified():
			productIsModified = True
			self.mensajes2 += u"Tipo de producto modificado\n"

		if self.ui.unitCB.isModified():
			productIsModified = True
			self.mensajes2 += u"Unidad modificada\n"

		if self.ui.minimumED.isModified():
			self.ui.minimumED.setToolTip(self.ui.minimumED.initialText())
			productIsModified = True
			self.mensajes2 += u"Inventario mínimo modificado\n"
		else:
			self.ui.minimumED.setToolTip(u"")

		if self.ui.maximumED.isModified():
			productIsModified = True
			self.mensajes2 += u"Inventario máximo modificado\n"
			self.ui.maximumED.setToolTip(self.ui.maximumED.initialText())
		else:
			self.ui.maximumED.setToolTip(u"")

		if self.ui.actualED.isModified():
			productIsModified = True
			self.mensajes2 += u"Inventario actual modificado\n"

		if self.ui.edCostoPromedio.isModified():
			productIsModified = True
			self.mensajes2 += u"Costo promedio modificado\n"
		# print(self.ui.taxesCH.isModified())
		if self.ui.taxesCH.isModified():
			productIsModified = True
			self.mensajes2 += u"Impuesto modificado\n"

		if self.ui.baseED.isModified():
			productIsModified = True
			self.mensajes2 += u"Margen base modificado\n"

		## PRECIOS
		for index, rule in enumerate(self.cnt.activePriceRules()):

			if self.marginAdjust[index].isModified():
				productIsModified = True
				self.mensajes2 += u"Ajuste de margen %s modificado\n" % rule['name']

			if self.marginDiscount[index].isModified():
				productIsModified = True
				self.mensajes2 += u"Descuento en margen %s modificado\n" % rule['name']

			if self.priceFinal[index].isModified():
				productIsModified = True
				self.mensajes2 += u"Precio final %s modificado\n" % rule['name']


		## Aceptions
		# print "products.view.Capture.isModified - aceptions"
		# print self.aceptionsCount

		if self.ui.aceptionsFR.isModified():
			productIsModified = True
			self.mensajes2 += self.ui.aceptionsFR.modifiedMessages

		self.mensajes2 = self.mensajes2.rstrip(u"\n")

		# print "products.view.Capture.isModified() }", productIsModified, self.mensajes2

		return productIsModified


	def isValid(self):
		# print "products.view.Capture.isValid()"

		valida = True
		self.mensajes = ""

		if self.ui.edCodigo.isEmpty():
			valida = False
			self.mensajes += u"Falta el código\n"
		else:
			self.validarCodigo()
			if not self.ui.edCodigo.isValid():
				valida = False
				self.mensajes += u"%s\n" % self.ui.edCodigo.message()

		if self.cnt.useOwnCode:
			self.validarCodigo()
			if not self.ui.edCodigo.isValid():
				valida = False
				self.mensajes += u"%s\n" % self.ui.edCodigo.message()

		if self.cnt.useUniversalCode():
			if not self.ui.upcED.isValid():
				valida = False
				self.mensajes += u"%s\n" % self.ui.upcED.message()

		if self.cnt.useAuxiliaryCode():
			self.validarCodigo()
			if not self.ui.edCodigo2.isValid:
				valida = False
				self.mensajes += u"%s\n" % self.ui.edCodigo2.message()

		if self.ui.edNombre.isEmpty():
			valida = False
			self.mensajes += u"Falta el nombre\n"
		else:
			if not self.ui.edNombre.isValid():
				valida = False
				self.mensajes += u"%s\n" % self.ui.edNombre.message()

		# if not self.ui.cbClasificacion.isValid:
			# valida = False
			# if self.ui.edClasificacion.isEmpty:
				# self.mensajes += u"Debes capturar una clasificación\n"
			# else:
				# self.mensajes += u"%s\n" % self.ui.edClasificacion.message()

		if self.cnt.mustCaptureClassification():
			if not self.ui.cbClasificacion.currentText():
				valida = False
				self.mensajes += u"Debes capturar una clasificación\n"

		'''
		## LINES
		count = self.activeLines.count(True)

		for index, active in enumerate(self.activeLines):
			if active:
				if not eval("self.ui.line{}CB.isValid()".format(index)):
					valida = False
					if count == 1:
						self.mensajes += u"El dato de línea no es válido\n"
					else:
						self.mensajes += u"El dato de la línea {} no es válido\n".format(index)
		'''

		# Líneas
		# for lineCB in self.ui.lineCBs:
			# if not lineCB.isValid():
				# valida = False
				# self.mensajes += u"El dato de línea no es válido\n"


		if not self.ui.edCostoPromedio.isValid():
			valida = False
			self.mensajes += u"El costo promedio no es válido\n"

		"""
		for index, rule in enumerate ( self.cnt.activePriceRules ) :
			if not self.ui.pricesTA.cellWidget(index, PRICE_FINAL).value():
				valida = False
				self.mensajes += u"Falta definir el precio %s\n" % rule['name']
		"""

		# if self.ui.edPrecio1.value() == dec("0"):
			# valida = False
			# self.mensajes += u"Falta el Precio\n"
		# else:
			# if not self.ui.edPrecio1.isValid:
				# valida = False
				# self.mensajes += u"El precio no es válido\n"

		## Aceptions
		# for index in range(self.aceptionsCount):
			# if not self.aceptionIsValid(index):
				# valida = False
				# self.mensajes += self.aceptionValidityMessages()

		if not self.ui.aceptionsFR.isValid():
			valida = False
			self.mensajes += self.ui.aceptionsFR.validityMessages

		"""
		if self.ui.chHabilitar.isChecked():
			if not self.ui.aceptionsTB.isValid:
				valida = False
				self.mensajes += self.ui.aceptionsTB.messages
		"""

		validaTemp, mensajes = self.cnt.validateProduct(self.data(), self.mode())
		if not validaTemp:
			valida = False
			self.mensajes += mensajes

		self.mensajes = self.mensajes.rstrip("\n")

		return valida


	def lineaChanged(self):
		self.updateStatus()


	def lineSelected(self, index):
		self.updateStatus()


	def lineaEdited(self):
		if self.ui.cbLinea.findText(self.ui.cbLinea.currentText(), QtCore.Qt.MatchStartsWith) == -1:
			self.ui.cbLinea.setStyleSheet("background-color:#FFFF60;")
		else:
			self.ui.cbLinea.setStyleSheet("background-color:#FFFFFF;")
		self.updateStatus()



	def lineaLostFocus(self):
		if self.ui.cbLinea.findText(self.ui.cbLinea.currentText(), QtCore.Qt.MatchStartsWith) == -1:
			self.ui.cbLinea.setStyleSheet("background-color:#FFFF60;")
		else:
			self.ui.cbLinea.setStyleSheet("background-color:#FFFFFF;")
			self.ui.cbLinea.setCurrentIndex(self.ui.cbLinea.findText(self.ui.cbLinea.currentText(), QtCore.Qt.MatchStartsWith))
		self.updateStatus()


	def line_update(self):
		# print("""        products.Capture.line_update()""")

		# print(self.state == IDLE)

		if self.state == IDLE:
			self.families_load()

		# print("""        products.Capture.line_update() - END""")


	def loadLines(self):
		self.app.log2sys ( 'debug', "			Capture.loadLines()							@ products.view" )

		self.state = BUSY

		division_code = self.ui.divisionCB.currentData()

		lines = self.cnt.lines_pull(reference="000{}".format(division_code)[-3:])

		if not lines:
			self.app.log2sys ( 'error', "				WARNING: {} No lines".format(lines) )

		self.ui.lineCB.clear()

		for line in lines:

			self.ui.lineCB.addItem(line['name'], line['code'])

		self.state_reset()

		self.line_update()

		self.app.log2sys ( 'debug', "			Capture.loadLines()	- end					@ products.view" )


	def new(self, data=''):
		# print("    products.view.Capture.new()")


		# if data:
			# self.caller = self.cnt.app.master.container.currentWidget()


		# if ( not data and not self.caller ) or data:

			self.ui.titulo.setText(QtGui.QApplication.translate("Empresa Básica", "Producto nuevo", None, QtGui.QApplication.UnicodeUTF8))

			self.setMode('add')

			self.clear()

			# self.addLine()

			if data:
				data = eval(u"{}".format(data))

				self.ui.aceptionsFR.add(**data)

			self.ui.edCodigo.setFocus()

			self.updateStatus()

			self.mst.setInnerStatus('hidden')

			self.show()

		# elif self.caller:

			# caller = self.caller

			# self.caller = None

			# self.cnt.app.master.form_show('', '', '', '', caller)

		# print("    products.view.Capture.new() - END")


	def nombreEditado(self, texto):
		# if len(self.ui.edNombre.text()) == 1:
			# self.ui.edNombre.setText(unicode(self.ui.edNombre.text()).capitalize())
		self.updateStatus()


	def originChanged(self):
#        if self.ui.originCB.currentIndex() == self.ui.originCB.initialIndex():
#            self.ui.originCB.isModified = False
#        else:
#            self.ui.originCB.isModified = True
		pass


	def precioEdited(self, text):
		# print "\nproducts.view.Capture.precioEdited(%s)" % text
		self.updateStatus()


	def priceRangeChanged(self):
		# print "\nproducts.igu.Capture.priceRangeChanged()"

		for index, priceRange in enumerate(self.cnt.priceRanges()):
			if priceRange.reference[1]==u'a':
				exec('''self.ui.edAjuste%s.show()''' % (index+1))
				exec('''self.ui.edDescuento%s.show()''' % (index+1))
				exec('''self.ui.edMargenF%s.show()''' % (index+1))
				exec('''self.ui.edPrecio%s.show()''' % (index+1))
			else:
				exec('''self.ui.edAjuste%s.hide()''' % (index+1))
				exec('''self.ui.edDescuento%s.hide()''' % (index+1))
				exec('''self.ui.edMargenF%s.hide()''' % (index+1))
				exec('''self.ui.edPrecio%s.hide()''' % (index+1))
		self.calcularPrecio()


	def productKinds_load(self):
		self.ui.kindCB.clear()
		for kind in self.cnt.productKinds():
			self.ui.kindCB.addItem(kind['name'], kind['code'])


	def returnPressed(self):
		if self.ui.boGuardar.isEnabled():
			self.save()


	def save(self, **kwds):
		# print("\n\nproducts.view.Capture.save()")
		# print("\n    ", self.mode())

		## No se revisa validez de datos, para llegar aquí se tuvo que haber hecho
		self.setCursor(QtCore.Qt.WaitCursor)

		product = self.data()

		# print(product)

		try:
			if self.mode() == 'add':
				id = self.cnt.product_push(**product)

				product = self.cnt.product(id=id)

				self.new()
			else:
				self.cnt.product_push(**product)

			if 'classification' in product.keys():
				self.mst.eventRouter.emit(QtCore.SIGNAL("classificationsChanged()"))

			if 'lines' in product.keys():
				# self.mst.eventRouter.emit(QtCore.SIGNAL("productLines_changed()"))
				self.app.log2sys ( 'error', "    products Capture.save()\n        WARNING: lines changed\n        {}".format(product) )
				self.cnt.productLineChanged

			if kwds.has_key('hide'):
				if kwds['hide']:
					self.hide()
					self.emit(QtCore.SIGNAL('captureClosed()'))
			else:
				self.hide()
				self.emit(QtCore.SIGNAL('captureClosed()'))

			self.mst.eventRouter.emit(QtCore.SIGNAL("productsChanged()"))
			self.mst.eventRouter.emit(QtCore.SIGNAL("productAdded"), product)

			# self.cnt.app.pullFromStack()

		except:
			print ("\nException @ products.view.Capture.save() - \n    {}".format(sys.exc_info()[1]))
			self.cnt.app.showMessage('critical', u'No pude registrar los cambios', u'Repórtelo con el administrador de sistemas')

		self.setCursor(QtCore.Qt.ArrowCursor)


	def show(self):
		# print('    products.view.Capture.show()')
		if self.mst.isHidden():
			self.mst.form_show()
		QtGui.QFrame.show(self)


	def setData(self, product):
		# print("""\nproducts.view.Capture.setData()""")

		# print(product)

		self.old = product

		self.state = BUSY

		if product['status']:
			self.ui.statusSE.setCurrentData(product['status']['code'], initialToo=True)
		else:
			self.ui.statusSE.setCurrentData(int(self.cnt.productStatus_default()['value']), initialToo=True)

		## Clasificación
		# if product['classification_id']:
			# self.ui.cbClasificacion.setCurrentData(product['classification_id'], initialToo=True)



		## LINES
		# if product['lines']:
			# for index, line in enumerate(product['lines']):
				# exec("self.ui.line{}CB.data = product['lines'][index]['id']".format(index))
				# exec("self.ui.line{}CB.setCurrentData(int(product['lines'][index]['reference']), initialToo=True)".format(index))

		## LINES
		# if product['lines']:
			# for index, line in enumerate(product['lines']):
				# self.addLine()
				# self.ui.lineCBs[index].data = product['lines'][index]['id']
				# self.ui.lineCBs[index].setCurrentData(int(product['lines'][index]['reference']), initialToo=True)

		if product['lines']:

			classification = self.cnt.attribute(id=product['lines'][0]['reference'])

			# print('classification', classification)

			reference = classification['reference']

			self.state = IDLE

			if len( reference ) > 2:
				division_code = 82000 + int( reference[0:3] )

				self.ui.divisionCB.setCurrentData( division_code )

			if len( reference ) > 5:
				brand_code = 81000 + int( reference[3:6] )
				try:
					self.ui.brandCB.setCurrentData( brand_code )
				except:
					print ("products.Capture.setData() Could not set brand")

			if len( reference ) > 8:
				line_code = 82000 + int( reference[6:9] )
				self.ui.lineCB.setCurrentData( line_code )

			self.state_reset()

			self.ui.classificationCB.clear()

			classifications = self.cnt.app.model.attributes_get(**{'category':'productLine', 'referenceLIKE':reference})

			# print(888000, classifications)
			# print(888001, classification['id'])

			for item in classifications:
				self.ui.classificationCB.addItem(item['name'], item['id'])

			self.ui.classificationCB.setCurrentData(classification['id'])

		if 'code' in product['kind']:
			self.ui.kindCB.setCurrentData(product['kind']['code'], initialToo=True)

		if product['unit_code']:
			self.ui.unitCB.setCurrentData(product['unit_code'], initialToo=True)

		#! Stock data
		if 'minimum' in product:
			self.ui.minimumED.setValue(product['minimum'], initialToo=True)
			self.ui.maximumED.setValue(product['maximum'], initialToo=True)
			self.ui.actualED.setValue(product['current'], initialToo=True)

		# print(product)

		## COST
		if 'meancost' in product:
			self.ui.edCostoPromedio.setValue(product['meancost'], initialToo=True)

		## TAXES
		general = Decimal('0.00')
		special = Decimal('0.00')

		# print("===> product['taxes']: {}".format(product['taxes']))

		for tax in product['taxes']:
			try:
				if tax['code'] not in self.ui.taxesCH.data():
					self.ui.taxesCH.add(tax['code'], initialToo=True)
				if tax['code'] == 51:
					general = tax['factor']
				if tax['code'] in [53]:
					special = tax['factor']
			except:
				print ("""ERROR @ products.Capture.setData()""")
				print ("tax:", tax)
				raise

		self.ui.edCostoNeto.setValue(product['meancost']/(100+special)*(100+general), initialToo=True)

		# if data[0].descuentoindividual:
			# self.ui.edDescuento.setText("%.2f" % data[0].descuentoindividual)

#        if product['margin']:
		self.ui.baseED.setValue(product['margin'], initialToo=True)

		# print ( 7700, self.cnt.activePriceRules )
		# print ( 7701, product['prices'] )

		## PRECIOS      [ ajuste, descuento, margenNeto, precio ]
		for row, priceRule in enumerate ( self.cnt.activePriceRules ) :
			# priceZero = [price for price in product['prices'] if int(price['reference'])==priceRule['code']]
			priceZero = [price for price in product['prices'] if int(price['code'])==priceRule['code']]
			if priceZero:
				price = priceZero[0]
#                try:
				if True:
					netCost = self.ui.edCostoNeto.value()
					marginCalc = (((100+product['margin']) * (100+Decimal(price['factor1']))/100 * (100-Decimal(price['factor2']))/100)-100).quantize(Decimal('0.01'))

					priceCalc = (netCost * (100 + marginCalc) / 100).quantize(Decimal('0.0001'))

					self.marginAdjust[row].setValue(Decimal(price['factor1']), initialToo=True)
					self.marginDiscount[row].setValue(Decimal(price['factor2']), initialToo=True)
					self.marginCalc[row].setText("%s" % marginCalc)

					self.priceCalc[row].setText("%s" % priceCalc)

					if netCost:
						marginFinal = ((Decimal(price['value']) / netCost - 1 ) * Decimal('100')).quantize(Decimal('0.01'))
					else:
						marginFinal = Decimal('0.01')

					self.marginFinal[row].setText("%s" % marginFinal)

					self.priceFinal[row].setValue(Decimal(price['value']), initialToo=True)
#                except:
#                    print sys.exc_info()

#            self.ui.pricesTA.resizeColumnToContents(3)
#            self.ui.pricesTA.resizeColumnToContents(5)
			# self.ui.pricesTA.horizontalHeader().setResizeMode(5, QtGui.QHeaderView.Stretch)


		## Acepciones
		aceptions = product.pop('aceptions')

		local = [aceptions.pop(index) for index, aception in enumerate(aceptions) if aception['rol_id'] == self.cnt.app.holder['id']][0]

		self.ui.edCodigo.setText("%s" % local['code'], initialToo=True)

		self.ui.edNombre.setText(local['name'], initialToo=True)

		# self.ui.supplierDataFR.initialCount = len(aceptions)

		for index, aception in enumerate(aceptions):

			self.ui.aceptionsFR.add(**aception)

		self.state_reset()

		self.updateStatus()

		# print("""\nproducts.view.Capture.setData() - END""")


	def state_get(self):
		return self._state[-1]
	def state_set(self, value):
		self._state.append(value)
	state = property(state_get, state_set)
	def state_reset(self):
		self._state.pop()


	def taxes_load(self):
		default = [x for x in self.cnt.taxes() if 'default' in x['reference']][0]
		taxes = [ [ "{} {}".format(x['name'], x['value']), x['code'] ] for x in self.cnt.taxes()]
		self.ui.taxesCH.list_set(taxes)
		self.ui.taxesCH.defaultData = default['code']


	def tipoSeleccionado(self, index):
		self.updateStatus()


	def toggleComentarios(self):
		if self.ui.boComentarios.status==u'on':
			self.ui.comentarios.hide()
			self.ui.boComentarios.status=u'off'
			# self.ui.boComentarios.setText(u'Mostrar información')
		else:
			self.ui.comentarios.show()
			self.ui.boComentarios.status=u'on'
			# self.ui.boComentarios.setText(u'Ocultar información')


	def toggleDescuento(self, state):
		f=g
		m = "products.igu.Capture.toggleDescuento() #! empty"

		# if state==QtCore.Qt.Checked:
			# self.ui.edDescuento.setEnabled(True)
			# self.ui.chDescuento.setStyleSheet("color:#FFFFFF; background-color:#80A0FF")
		# else:
			# self.ui.edDescuento.setEnabled(False)
			# self.ui.chDescuento.setStyleSheet("color:#FFFFFF; background-color:#C0D0FF")

	"""
	def toggleImpuesto(self, state):
		# print "products.view.Capture.toggleImpuesto()"
		if state==QtCore.Qt.Checked:
			self.ui.taxED.setEnabled(True)
			# self.ui.chImpuesto.setStyleSheet("color:#FFFFFF; background-color:#80A0FF;")
		else:
			self.ui.taxED.setEnabled(False)
			# self.ui.chImpuesto.setStyleSheet("color:#FFFFFF; background-color:#C0D0FF;")
	"""

	def toggleExterno(self, state):
		if state == QtCore.Qt.Checked:
			self.ui.chHabilitar.setChecked(True)
			self.ui.frTituloExterno2.hide()
			self.ui.aceptionFR_layout.sizeOut()
			self.updateStatus()
		else:
			self.ui.chHabilitar2.setChecked(False)
			self.ui.aceptionFR_layout.sizeIn()
			self.updateStatus()


	def unitChanged(self):
		self.updateStatus()


	def useProductLine_update(self, value):
		# print("useProductLine_update()")
		#! Requires state check
		f=t

		# if self.cnt.canEditProductLine():
		if value is True:
			self.ui.laLinea.show()
			self.ui.cbLinea.show()
			# self.ui.laLinea.setStyleSheet("color:#FFFFFF; background-color:#C0D0FF")
		else:
			self.ui.laLinea.hide()
			self.ui.cbLinea.hide()
			# self.ui.laLinea.setStyleSheet("color:#FFFFFF; background-color:#80A0FF")
		self.updateStatus()

		# print("useProductLine_update() - END")

	'''
	def updateClassifications(self):
		self.ui.cbClasificacion.clear()
		for classification in self.cnt.productClassifications():
			self.ui.cbClasificacion.addItem(classification['name'], classification['id'])
		self.ui.cbClasificacion.setCurrentIndex(self.ui.cbClasificacion.findText(u''))
	'''

	def canEditCurrentStock_update(self):
		if self.cnt.canEditCurrentStock():
			self.ui.actualED.setEnabled(True)
#            self.ui.laActual.setStyleSheet("color:#FFFFFF; background-color:#80A0FF;")
			# self.ui.frCostoPromedio.setEnabled(True)
		else:
			self.ui.actualED.setEnabled(False)
#            self.ui.laActual.setStyleSheet("color:#FFFFFF; background-color:#C0D0FF;")
			# self.ui.frCostoPromedio.setEnabled(False)
		self.updateStatus()


	def mustCaptureClassification_update(self):
		# print  """products.view.Capture.mustCaptureClassification_update()"""
		self.updateStatus()


	def updateOrigins(self):
		old = self.ui.originCB.currentData()

		self.ui.originCB.clear()

		origins = self.cnt.suppliers()

		if origins:
			for origin in origins:
				self.ui.originCB.addItem("%s %s" % (origin['person']['name'], origin['person']['name2']), origin['id'])
		else:
			self.ui.originCB.addItem(u"No hay origenes registrados")

		self.ui.originCB.setCurrentData(old)


	def updateProductStatuss(self):
		# self.ui.statusSE.clear()
		# for status in self.cnt.productStatuss():
			# self.ui.statusSE.addItem(status['name'], status['code'])
		# self.ui.statusSE.setCurrentData(self.cnt.defaultProductStatus()['code'])
		statuss = self.cnt.productStatuss()
		self.ui.statusSE.setData([x['name'] for x in statuss], [x['code'] for x in statuss])
		self.ui.statusSE.setCurrentData(int(self.cnt.productStatus_default()['value']))


	def updateStatus(self, *args):
		# print("""products.view.Capture.updateStatus()""")
		# print(self.state)
		if self.state is IDLE:
			if self.isModified():
				if self.mode() == 'edit':
					if self.isValid():
						self.ui.boGuardar.setEnabled(True)
						self.ui.boGuardar.setToolTip(self.mensajes2)
						self.ui.comentarios.setText(self.mensajes2)
					else:
						self.ui.boGuardar.setEnabled(False)
						self.ui.boGuardar.setToolTip(self.mensajes)
						self.ui.comentarios.setText("%s\n\n%s" % (self.mensajes, self.mensajes2))
				elif self.mode() == 'add':
					if self.isValid():
						self.ui.boGuardar.setEnabled(True)
						self.ui.boGuardar.setToolTip(u'OK')
						self.ui.comentarios.setText(u'OK')
					else:
						self.ui.boGuardar.setEnabled(False)
						self.ui.boGuardar.setToolTip(self.mensajes)
						self.ui.comentarios.setText(self.mensajes)
			else:
				self.ui.boGuardar.setEnabled(False)
				self.ui.boGuardar.setToolTip(u"No hay cambios")
				self.ui.comentarios.setText(self.mensajes)
		else:
			pass
			# print 'skipped'
			# don't test on init


	def updateAceptionsStatus(self):
		for index in range(self.aceptionsCount):
			if self.aceptionIsValid(index):
				if index == self.aceptionsCount-1:
					self.aceptionAdd()

		self.updateStatus()


	def useAuxiliaryCode_update(self):
		if self.cnt.useAuxiliaryCode():
			self.ui.laCodigo2.show()
			self.ui.edCodigo2.show()
		else:
			self.ui.laCodigo2.hide()
			self.ui.edCodigo2.hide()


	def useOwnCode_update(self):
		# print("products.view.Capture.useOwnCode_update()")

		if self.cnt.useOwnCode:
			self.ui.laCodigo.show()
			self.ui.edCodigo.show()
		else:
			self.ui.laCodigo.hide()
			self.ui.edCodigo.hide()

		# print("products.view.Capture.useOwnCode_update() - END")


	def useUniversalCode_update(self):
		if self.cnt.useUniversalCode():
			self.ui.upcLA.show()
			self.ui.upcED.show()
		else:
			self.ui.upcLA.hide()
			self.ui.upcED.hide()


	def updateUnits(self):
		self.ui.unitCB.clear()
		for unit in self.cnt.unitKinds():
			self.ui.unitCB.addItem(unit['name'], unit['code'])


	def validarCodigo(self, text=""):
		# print "products.view.Capture.validarCodigo()"
		oldFocused = self.focusWidget()

		self.ui.edCodigo.setExternalValidation(True, u"")

		if self.mode() == 'edit':
			if self.ui.edCodigo.isModified():
				aception = self.cnt.aception(code=unicode(self.ui.edCodigo.text()), rol_id=self.cnt.app.holder['id'])
				if aception:
					self.ui.edCodigo.setExternalValidation(False, u"El código ya está en uso\n")

		elif self.mode() == 'add':
			aception = self.cnt.aception(code=unicode(self.ui.edCodigo.text()), rol_id=self.cnt.app.holder['id'])
			if aception:
				## Checar si se desea agregar una acepción a un producto existente
				self.ui.edCodigo.setExternalValidation(False, u"El código ya está en uso\n")
				# if self.ui.frLocal.isEnabled():
					# acepcion = self.cnt.app.model.acepcionI(code=unicode(self.ui.edCodigo.text()), rol_id=self.cnt.app.holder.id)
					# result = QtGui.QMessageBox.warning(self, u"Empresa Básica - Código existente", u"Este código es del producto local\n\n%s, %s\n\n¿Quieres agregarle datos a ese producto?" % (acepcion.name, acepcion.product.clasificacion.name), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
					# if result == QtGui.QMessageBox.Yes:
						# self.ui.frLocal.setEnabled(False)
						# self.ui.frLocal.setToolTip(u"Para modificar estos datos, cierre esta ventana, seleccione el producto en la lista de productos y presione Modificar")
						# data = {}
						# data['acepcion'] = acepcion
						# self.setData(data)
					# else:
						# self.ui.edCodigo.setExternalValidation(False, u"El código ya existe\n")

		if oldFocused:
			oldFocused.setFocus()


	def validarCodigo2(self, text=""):
		oldFocused = self.focusWidget()
		f=g
		acepcion = self.cnt.app.model.acepcionI(rol_id=self.cnt.app.holder['id'], referencia=unicode(self.ui.edCodigo2.text()))

		self.ui.edCodigo2.setExternalValidation(True, u"")
		if acepcion:
			if self.mode() == 'add':
				self.ui.edCodigo2.setExternalValidation(True, u"El código auxiliar ya existe\n")
		if oldFocused:
			oldFocused.setFocus()
		#~ self.updateStatus()



class Aceptions(QtGui.QFrame):

	def __init__(self, *args):

		self.mst = args[0].mst
		self.cnt = self.mst.cnt

		self.owner = args[0]

		QtGui.QFrame.__init__(self, *args)

		self.ui = aceptions_ui.Ui_Frame()
		self.ui.setupUi(self)

		self.connect(self.ui.addBU, QtCore.SIGNAL('clicked()'), self.add)


	def add(self, **aception):
		# print("\nproducts.view.Aceptions.add()")
		# print(aception)
		## Check if there are incomplete aceptions
		message = u''
		checked = []
		for aceptionIndex in range(1, self.ui.contentsFRLY.count()):

			# checked.append(self.ui.aceptionSupplierCBs[aceptionIndex].currentIndex())

			aceptionFR = self.ui.contentsFRLY.itemAt(aceptionIndex).widget()

			if not aceptionFR.isValid():

				if aceptionFR.ui.supplierCB.currentIndex() >= 0:
					messages = aceptionFR.validityMessages

					message += u'Error en acepción de %s\n' % aceptionFR.ui.supplierCB.currentText()
					messages = messages.split('\n')
					for messageT in messages:
						message += u'    %s\n'  % messageT
				else:
					message += u'Error en acepción No.%s\n' % aceptionIndex

		if message:
			self.ui.addBU.setToolTip(message)

		else:
			self.ui.addBU.setToolTip('')

			# self.ui.supplierDataLY.setRowStretch(aceptionsStartRow+self.aceptionsCount, 1)

			aceptionFR = Aception(self)
			aceptionFR.init()

			self.ui.contentsFRLY.addWidget(aceptionFR)

			if aception:
				aceptionFR.setData(**aception)

		self.updateStatus()


	def clear(self):
		for aceptionIndex in range(1, self.ui.contentsFRLY.count()):
			widget = self.ui.contentsFRLY.itemAt(1).widget()
			self.ui.contentsFRLY.removeWidget(widget)
			widget.setParent(None)
			del widget


	def data(self):
		# print "products.view.Aceptions.data()"
		aceptions = []

		for aceptionIndex in range(1, self.ui.contentsFRLY.count()):
			aceptions.append(self.ui.contentsFRLY.itemAt(aceptionIndex).widget().data())

		return aceptions


	def isModified(self):

		self.modifiedMessages = u''

		for index in range(1, self.ui.contentsFRLY.count()):

			if self.ui.contentsFRLY.itemAt(index).widget().isModified():
				self.modifiedMessages += u'{}'.format(self.ui.contentsFRLY.itemAt(index).widget().modifiedMessages)

		return not not self.modifiedMessages


	def isValid(self):
		# print "products.view.Aceptions.isValid()"
		self.validityMessages = ''
		for index in range(1, self.ui.contentsFRLY.count()):
			if not self.ui.contentsFRLY.itemAt(index).widget().isValid():
				self.validityMessages += u'{}'.format(self.ui.contentsFRLY.itemAt(index).widget().validityMessages)
		return not self.validityMessages


	def updateStatus(self):
		self.owner.updateStatus()



class Aception(QtGui.QFrame):
	""" View for capturing Product Aception data

		2015.06.17  Now accepts rols not listed as suppliers by adding it to
					the pertinent widget.
	"""

	def __init__(self, *args):

		self.mst = args[0].mst
		self.cnt = self.mst.cnt

		self.owner = args[0]

		QtGui.QFrame.__init__(self, *args)

		self.ui = aception_ui.Ui_Frame()
		self.ui.setupUi(self)

		font = QtGui.QFont()
		font.setBold(True)
		font.setPointSize(10 * self.mst.layoutZoom)

		smallFont = QtGui.QFont()
		font.setBold(True)
		font.setPointSize(9 * self.mst.layoutZoom)

		style = "background-color:qlineargradient(x1:.5, y1:0, x2:.5, y2:1, stop:0 #E0E0F0, stop:.2 #F8F8FF, stop:.8 #F4F4FC, stop:1 #D0D0E0); border-radius:0px;"

		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		# sizePolicy.setHeightForWidth(self.marginAdjust[index].sizePolicy().hasHeightForWidth())

		sizePolicy.setHeightForWidth(self.ui.supplierCB.sizePolicy().hasHeightForWidth())

		self.ui.supplierCB.setSizePolicy(sizePolicy)
		self.ui.supplierCB.setFont(font)
		self.ui.supplierCB.setStyleSheet(style)
		self.ui.supplierCB.setFrame(False)
		# self.ui.supplierCB.index = self.aceptionsCount
		self.ui.supplierCB.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
		self.ui.supplierCB.setMinimumContentsLength(15)
		self.ui.supplierCB.setMaxVisibleItems(15)

		# self.ui.codeEDs.append(cdLineEdit.CDLineEdit(self.ui.supplierDataFR))
		sizePolicy.setHeightForWidth(self.ui.codeED.sizePolicy().hasHeightForWidth())

		self.ui.codeED.setSizePolicy(sizePolicy)
		self.ui.codeED.setFont(smallFont)
		self.ui.codeED.setStyleSheet(style)
		self.ui.codeED.setEnabled(False)
		self.ui.codeED.setEmptyAllowed(False)
		# self.ui.codeED.index = self.aceptionsCount
		self.ui.codeED.setSymbols('-_/" ')

		## Nombre de Producto
		# self.ui.nameEDs.append(CDTextEdit(self.ui.supplierDataFR))
		# self.ui.nameEDs.append(cdLineEdit.CDLineEdit(self.ui.supplierDataFR))

		sizePolicy.setHeightForWidth(self.ui.nameED.sizePolicy().hasHeightForWidth())

		self.ui.nameED.setSizePolicy(sizePolicy)
		self.ui.nameED.setFont(smallFont)
		self.ui.nameED.setStyleSheet(style)
		self.ui.nameED.setEnabled(False)
		self.ui.nameED.setEmptyAllowed(False)
		self.ui.nameED.setMessagePrefix(u"El nombre ")
		# self.ui.nameED.index = self.aceptionsCount
		self.ui.nameED.setSymbols(u"""-+=_.,:#"'/*°|$%&()[] """)

		completer = QtGui.QCompleter([], self.ui.nameED)
		completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

		completer.popup().setResizeMode(QtGui.QListView.Adjust)

		completerModel = Model(completer)
		completerModel.productIdRole = 1003
		completerModel.aceptionIndex = 1004

		completer.setModel(completerModel)

		self.ui.nameED.setCompleter(completer)

		# self.ui.minimumED.append(cdNumberEdit.CDNumberEdit(self.ui.supplierDataFR))
		sizePolicy.setHeightForWidth(self.ui.minimumED.sizePolicy().hasHeightForWidth())

		self.ui.minimumED.setSizePolicy(sizePolicy)
		self.ui.minimumED.setFont(font)
		self.ui.minimumED.setStyleSheet(style)
		self.ui.minimumED.setEnabled(False)
		self.ui.minimumED.setEmptyAllowed(False)
		self.ui.minimumED.setMessagePrefix(u"Pedido mínimo")
		# self.ui.minimumED.index = self.aceptionsCount

		# self.ui.aceptionCostEDs.append(cdNumberEdit.CDNumberEdit(self.ui.supplierDataFR))
		sizePolicy.setHeightForWidth(self.ui.costED.sizePolicy().hasHeightForWidth())

		self.ui.costED.setSizePolicy(sizePolicy)
		self.ui.costED.setFont(font)
		self.ui.costED.setStyleSheet(style)
		self.ui.costED.setEnabled(False)
		# self.ui.costED.index = self.aceptionsCount
		self.ui.costED.setEmptyAllowed(False)
		self.ui.costED.setMessagePrefix(u"Costo")
		self.ui.costED.setDecimals(4)

		# self.ui.aceptionDiscountEDs.append(cdNumberEdit.CDNumberEdit(self.ui.supplierDataFR))
		sizePolicy.setHeightForWidth(self.ui.discountED.sizePolicy().hasHeightForWidth())

		self.ui.discountED.setSizePolicy(sizePolicy)
		self.ui.discountED.setFont(font)
		self.ui.discountED.setStyleSheet(style)
		self.ui.discountED.setEnabled(False)
		self.ui.discountED.setMessagePrefix(u"Descuento")
		# self.ui.discountED.index = self.aceptionsCount

		# self.ui.aceptionChargeEDs.append(cdNumberEdit.CDNumberEdit(self.ui.supplierDataFR))
		sizePolicy.setHeightForWidth(self.ui.chargeED.sizePolicy().hasHeightForWidth())

		self.ui.chargeED.setSizePolicy(sizePolicy)
		self.ui.chargeED.setFont(font)
		self.ui.chargeED.setStyleSheet(style)
		self.ui.chargeED.setEnabled(False)
		self.ui.chargeED.setMessagePrefix(u"Cargos")
		# self.ui.chargeED.index = self.aceptionsCount

		# self.ui.aceptionTaxEDs.append(cdNumberEdit.CDNumberEdit(self.ui.supplierDataFR))
		# sizePolicy.setHeightForWidth(self.ui.taxED.sizePolicy().hasHeightForWidth())

		# self.ui.taxED.setSizePolicy(sizePolicy)
		# self.ui.taxED.setFont(font)
		# self.ui.taxED.setStyleSheet(style)
		# self.ui.taxED.setEnabled(False)
		# self.ui.taxED.setMessagePrefix(u"Impuesto")
		# self.ui.taxED.index = self.aceptionsCount

		# self.ui.aceptionNetCostEDs.append(cdNumberEdit.CDNumberEdit(self.ui.supplierDataFR))
		sizePolicy.setHeightForWidth(self.ui.netCostED.sizePolicy().hasHeightForWidth())

		self.ui.netCostED.setSizePolicy(sizePolicy)
		self.ui.netCostED.setFont(font)
		self.ui.netCostED.setStyleSheet(style)
		self.ui.netCostED.setEnabled(False)
		self.ui.netCostED.setMessagePrefix(u"Costo neto")
		# self.ui.netCostED.index = self.aceptionsCount
		self.ui.netCostED.setDecimals(4)

		# self.ui.supplierDataLY.addWidget(self.ui.aceptionSupplierCBs[self.aceptionsCount], aceptionsStartRow + 0, aceptionsStartColumn + self.aceptionsCount)
		# self.ui.supplierDataLY.addWidget(self.ui.aceptionCodeEDs[self.aceptionsCount], aceptionsStartRow + 1, aceptionsStartColumn + self.aceptionsCount)
		# self.ui.supplierDataLY.addWidget(self.ui.aceptionNameEDs[self.aceptionsCount], aceptionsStartRow + 2, aceptionsStartColumn + self.aceptionsCount)
		# self.ui.supplierDataLY.addWidget(self.ui.aceptionMinimumStockEDs[self.aceptionsCount], aceptionsStartRow + 3, aceptionsStartColumn + self.aceptionsCount)
		# self.ui.supplierDataLY.addWidget(self.ui.aceptionCostEDs[self.aceptionsCount], aceptionsStartRow + 4, aceptionsStartColumn + self.aceptionsCount)
		# self.ui.supplierDataLY.addWidget(self.ui.aceptionDiscountEDs[self.aceptionsCount], aceptionsStartRow + 5, aceptionsStartColumn + self.aceptionsCount)
		# self.ui.supplierDataLY.addWidget(self.ui.aceptionChargeEDs[self.aceptionsCount], aceptionsStartRow + 6, aceptionsStartColumn + self.aceptionsCount)
		# self.ui.supplierDataLY.addWidget(self.ui.aceptionTaxEDs[self.aceptionsCount], aceptionsStartRow + 7, aceptionsStartColumn + self.aceptionsCount)
		# self.ui.supplierDataLY.addWidget(self.ui.aceptionNetCostEDs[self.aceptionsCount], aceptionsStartRow + 8, aceptionsStartColumn + self.aceptionsCount)

		self.connect(self.ui.supplierCB, QtCore.SIGNAL('currentIndexChanged(int)'), self.supplierChanged)

		self.connect(self.ui.codeED, QtCore.SIGNAL("editingFinished()"), self.codeCaptured)
		# self.connect(self.ui.codeED, QtCore.SIGNAL("editingFinished()"), self.costEdited)

		self.connect(self.ui.nameED.completer(), QtCore.SIGNAL("activated(QModelIndex)"), self.nameSelected)
		# self.connect(self.ui.nameED, QtCore.SIGNAL('returnPressed()'), self.nameCaptured)
		self.connect(self.ui.nameED, QtCore.SIGNAL('editingFinished()'), self.nameCaptured)
		self.connect(self.ui.nameED, QtCore.SIGNAL('textEdited(QString)'), self.nameEdited)
		self.connect(self.ui.nameED, QtCore.SIGNAL('nameSelected(QString)'), self.setName)
		# self.connect(self.ui.nameED, QtCore.SIGNAL("editingFinished()"), self.costEdited)

		self.connect(self.ui.minimumED, QtCore.SIGNAL("editingFinished()"), self.costEdited)
		self.connect(self.ui.costED, QtCore.SIGNAL("editingFinished()"), self.costEdited)
		self.connect(self.ui.discountED, QtCore.SIGNAL("textEdited(QString)"), self.discountEdited)
		self.connect(self.ui.chargeED, QtCore.SIGNAL("textEdited(QString)"), self.chargeEdited)
		# self.connect(self.ui.taxED, QtCore.SIGNAL("textEdited(QString)"), self.taxEdited)
		self.connect(self.ui.netCostED, QtCore.SIGNAL("textEdited(QString)"), self.netCostEdited)


	def init(self):
		self.id = None
		self.loadSuppliers()
		self.ui.supplierCB.setCurrentIndex(-1, initialToo=True)

		self.ui.codeED.setText('', initialToo=True)
		self.ui.nameED.setText('', initialToo=True)
		self.ui.minimumED.setValue(Decimal('0'), initialToo=True)
		self.ui.costED.setValue(Decimal('0'), initialToo=True)
		self.ui.discountED.setValue(Decimal('0'), initialToo=True)
		self.ui.chargeED.setValue(Decimal('0'), initialToo=True)
		# self.ui.taxED.setValue(Decimal('0'), initialToo=True)
		self.ui.netCostED.setValue(Decimal('0'), initialToo=True)


	def calculateNetCost(self):
		# print "products.view.Aception.calculateNetCost()"
		cost = self.ui.costED.value() * (Decimal('100') - self.ui.discountED.value()) / Decimal('100')
		self.ui.netCostED.setValue(cost)


	def chargeEdited(self,*args):
		self.calculateNetCost()
		self.updateStatus()


	def clear(self):
		# self.ui.supplierCB.deleteLater()
		# self.ui.codeED.deleteLater()
		# self.ui.nameED.deleteLater()
		# self.ui.minimumED.deleteLater()
		# self.ui.costEDs.deleteLater()
		# self.ui.discountED.deleteLater()
		# self.ui.chargeED.deleteLater()
		# self.ui.taxEDs.deleteLater()
		# self.ui.netCostED.deleteLater()

		self.modificationMessage = ''
		self.validationMessage = ''


	def codeCaptured(self):
		# print("""    products.view.Aception.codeCaptured()""")

		rol_rfc = unicode(self.ui.supplierCB.currentData(QtCore.Qt.UserRole+1))

		filtros = {}
		filtros['code'] = unicode(self.ui.codeED.text())
		filtros['persons.rfc'] = rol_rfc

		products = self.cnt.products(0, **filtros)

		if products:
			self.cnt.app.showMessage('warning', u"Este código ya existe para este proveedor", u"Type a different one")

		#! Should widget content be marked invalid

		self.updateStatus()

		# print("""    products.view.Aception.codeCaptured() - END""")


	def costEdited(self):
		# print "products.view.Aception.costEdited()"
		self.calculateNetCost()
		self.updateStatus()


	def data(self):
		# print "products.view.Aception.data()"
		aception = {}

		if self.ui.supplierCB.isModified():
			aception['rol_id'] = self.ui.supplierCB.currentData()
		if self.ui.codeED.isModified():
			aception['code'] = u"%s" % self.ui.codeED.text()
		if self.ui.nameED.isModified():
			aception['name'] = u"%s" % self.ui.nameED.text()
			# aception['name'] = "%s" % self.ui.aceptionNameEDs[index].toPlainText()
		if self.ui.costED.isModified():
			aception['cost'] = self.ui.costED.value()
		if  self.ui.discountED.isModified() or self.id == None:
			aception['generaldiscount'] = self.ui.discountED.value()

		if self.ui.minimumED.isModified():
			aception['quota'] = self.ui.minimumED.value()

		if aception:
			if self.id:
				aception['id'] = self.id

		return aception


	def discountEdited(self,*args):
		self.calculateNetCost()
		self.updateStatus()


	def isModified(self):
		return not not self.modifiedData()


	def isValid(self):
		# print "\nproducts.view.Aception.isValid()"

		isValid = True
		self.validityMessages = u""

		index = self.parent().layout().indexOf(self)

		if not self.ui.supplierCB.isValid():
			isValid = False
			self.validityMessages += u"Error en Proveedor en acepción %s\n" % (index)

		if not self.ui.codeED.isValid():
			isValid = False
			self.validityMessages += u"Error en Código en acepción %s\n" % (index)

		if not self.ui.nameED.isValid():
			isValid = False
			self.validityMessages += u"%s\n" % self.ui.nameED.message()

		if not self.ui.minimumED.isValid():
			isValid = False
			self.validityMessages += u"Error en Pedido mínimo en acepción %s\n" % (index)

		if not self.ui.costED.isValid():
			isValid = False
			self.validityMessages += u"Error en Costo en acepción %s\n" % (index)

		if not self.ui.discountED.isValid():
			isValid = False
			self.validityMessages += u"Error en Discount en acepción %s\n" % (index)

		if not self.ui.chargeED.isValid():
			isValid = False
			self.validityMessages += u"Error en Charge en acepción %s\n" % (index)

		# if not self.ui.taxED.isValid():
			# isValid = False
			# self.validityMessages += u"Error en Tax en acepción %s\n" % (index)

		if not self.ui.netCostED.isValid():
			isValid = False
			self.validityMessages += u"Error en Costo Total en acepción %s\n" % (index)

		self.validityMessages = self.validityMessages.rstrip(u'\n')

		# print "    ", isValid
		# print "    ", messages.encode('utf8')

		return isValid


	def loadSuppliers(self):
		self.ui.supplierCB.clear()
		self.ui.supplierCB.addItem("", None)
		for supplierIndex, supplier in enumerate(self.cnt.suppliers()):
			self.ui.supplierCB.addItem(u'{}'.format(supplier['person']['name']), supplier['id'])
			self.ui.supplierCB.setItemData(supplierIndex+1, supplier['person']['rfc'], QtCore.Qt.UserRole+1)


	def modifiedData(self):
		data = []
		self.modifiedMessages = ''

		index = self.parent().layout().indexOf(self)

		if self.ui.supplierCB.isModified():
			data = self.ui.supplierCB.currentData()
			self.modifiedMessages += u"Proveedor modificado en la acepcion %s\n" % (index)

		if self.ui.codeED.isModified():
			data = self.ui.codeED.text()
			self.modifiedMessages += u"Código modificado en la acepcion %s\n" % (index)

		if self.ui.nameED.isModified():
			data = self.ui.nameED.text()
			self.modifiedMessages += u"Nombre modificado en la acepcion %s\n" % (index)

		if self.ui.costED.isModified():
			data = self.ui.costED.value()
			self.modifiedMessages += u"Costo modificado en la acepcion %s\n" % (index)

		if self.ui.discountED.isModified():
			data = self.ui.discountED.value()
			self.modifiedMessages += u"Descuento modificado en la acepcion %s\n" % (index)

		# if self.ui.taxED.isModified():
			# data = self.ui.taxED.value()
			# self.modifiedMessages += u"Impuesto modificado en la acepcion %s\n" % (index)

		if self.ui.minimumED.isModified():
			data = self.ui.minimumED.text()
			self.modifiedMessages += u"Pedido mínimo modificado en la acepcion %s\n" % (index)

		if self.ui.netCostED.isModified():
			data = self.ui.netCostED.value()
			self.modifiedMessages += u"Costo neto modificado en la acepcion %s\n" % (index)

		self.modifiedMessages = self.modifiedMessages.rstrip(u'\n')

		# if index < self.ui.aceptionsFR.initialCount:
			# self.setAceptionModificationMessages(index, messages.rstrip("\n"))

		return data


	def minimumEdited(self):
		self.updateStatus()


	def nameSelected(self, completionModelIndex=None):
		# print "products.view.Aception.nameSelected()"

		#! Este atributo no existe hay que sacarlo del layot.indexOf del parent del widget indicado
		index = self.sender().parent().index

		xModel = self.ui.nameED.completer().model()
		cModel = self.ui.nameED.completer().completionModel()

		rol_rfc = unicode(self.ui.supplierCB.currentData(QtCore.Qt.UserRole+1))

		#product = xModel.products[cModel.data(cModel.index(completerRow, 0), xModel.aceptionIndex).toInt()[0]]

		product = xModel.products[cModel.data(completionModelIndex, xModel.aceptionIndex).toInt()[0]]

		aception = [x for x in product['aceptions'] if x['rol']['person']['rfc'] == rol_rfc][0]

		self.ui.codeED.setText(aception['code'])
		self.ui.nameED.setText(aception['name'])
		self.ui.minimumED.setText(aception['quota'])
		self.ui.costED.setText('{}'.format(aception['cost']))
		self.ui.discountED.setText('{}'.format(aception['individualdiscount']))

		self.ui.nameED.emit(QtCore.SIGNAL("nameSelected(QString)"), aception['name'])


	def nameCaptured(self):
		# print "products.view.Aception.nameCaptured()"
		pass
		# index = self.sender().index
		# self.ui.aceptionNameEDs[index].setText(aception['name'])


	def nameEdited(self, text):
		"products.view.Aception.nameEdited()"
		if len(text) < 2:
			self.ui.nameED.completer().model().clear()

		elif len(text) == 2:

			rol_rfc = unicode(self.ui.supplierCB.currentData(QtCore.Qt.UserRole+1))

			filtros = {}
			filtros['name like'] = unicode(text)
			filtros['persons.rfc'] = rol_rfc

			model = self.ui.nameED.completer().model()
			model.clear()
			model.products = self.cnt.products(0, **filtros)

			## Set Model Data
			for row, product in enumerate(model.products):
				aception = [x for x in product['aceptions'] if x['rol']['person']['rfc'] == rol_rfc][0]
				model.setData(model.createIndex(row, 0), "%s %s %s" % (aception['name'], product['lines'][0]['name'], aception['code']), role=QtCore.Qt.DisplayRole)
				model.setData(model.createIndex(row, 0), "%s" % aception['name'], role=QtCore.Qt.EditRole)
				model.setData(model.createIndex(row, 0), row, role=model.aceptionIndex)
				model.setData(model.createIndex(row, 0), product['id'], role=model.productIdRole)

			model.reset()

			self.ui.nameED.completer().popup().setMinimumWidth(self.ui.nameED.completer().popup().sizeHintForColumn(0))

			h = self.ui.nameED.mapToGlobal(self.ui.nameED.pos()).x() + self.ui.nameED.width() - self.ui.nameED.completer().popup().width()
			v = self.ui.nameED.completer().popup().pos().y()

			# self.ui.nameED.completer().popup().move(100, 100)

			self.ui.nameED.completer().popup().setGeometry(100, 100, 640, 480)

		self.updateStatus()



	def netCostEdited(self):
		pass


	def setData(self, **aception):
		# print("""    products.view.Aception.setData()""")

		# print(aception)

		if 'id' in aception.keys():
			self.id = aception['id']
			initialToo = True
		else:
			initialToo = False
		if 'rol_id' in aception:

			## Imported documents capture, created the necessity of loading
			## suppliers not registered as such
			if self.ui.supplierCB.findData(aception['rol_id']) < 0:

				entity = self.cnt.app.model.rol_full_pull(id=aception['rol_id'])

				self.ui.supplierCB.addItem("%s %s" % (entity['person']['name'], entity['person']['name2']), aception['rol_id'])
				self.ui.supplierCB.setItemData(self.ui.supplierCB.count()-1, entity['person']['rfc'], QtCore.Qt.UserRole+1)
				self.ui.supplierCB.setItemData(self.ui.supplierCB.count()-1, entity, QtCore.Qt.UserRole+2)

			self.ui.supplierCB.setCurrentData(aception['rol_id'], initialToo=initialToo)
		if 'code' in aception:
			self.ui.codeED.setText(aception['code'], initialToo=initialToo)
		if 'name' in aception:
			self.ui.nameED.setText(aception['name'], initialToo=initialToo)
		if 'quota' in aception:
			self.ui.minimumED.setValue(Decimal(aception['quota']), initialToo=initialToo)
		if 'cost' in aception:
			self.ui.costED.setValue(aception['cost'], initialToo=initialToo)
		elif 'price' in aception:
			self.ui.costED.setValue(aception['price'], initialToo=initialToo)
		if 'generaldiscount' in aception:
			self.ui.discountED.setValue(aception['generaldiscount'], initialToo=initialToo)
		# self.ui.chargeED.setValue(aception['charge'], initialToo=True)
		# self.ui.taxED.setValue(aception['tax'], initialToo=True)
		if 'cost' in aception and 'generaldiscount' in aception:
			netCost = aception['cost'] * (Decimal('100')-aception['generaldiscount']) / Decimal('100')
			self.ui.netCostED.setValue(netCost, initialToo=initialToo)

		# print("""    products.view.Aception.setData() - END""")


	def setName(self, text):
		# print "products.view.Aception.setName()", text
		self.sender().setText(text)


	def supplierChanged(self):
		# print "products.view.Aception.supplierChanged()"

		message = u''

		#! Se elimina esto porque ya se acepta más de una acepción por proveedor
		#! (Su asume que se permite sólo una acepción por proveedor)
		# for aceptionIndex in range(self.aceptionsCount):
			# if self.sender().currentIndex() == self.ui.aceptionSupplierCBs[aceptionIndex].currentIndex():
				# message += u'Ya existe acepción para este proveedor'

		if message:
			self.sender().setToolTip(message)
		else:
			self.sender().setToolTip('')


			self.ui.codeED.setEnabled(True)
			self.ui.nameED.setEnabled(True)
			self.ui.costED.setEnabled(True)
			self.ui.discountED.setEnabled(True)
			self.ui.netCostED.setEnabled(True)
			# self.ui.taxED.setEnabled(True)
			self.ui.minimumED.setEnabled(True)

		self.updateStatus()


	# def taxEdited(self):
		# self.updateStatus()


	def updateStatus(self):
		self.owner.updateStatus()



class Details(QtGui.QDockWidget):

	def __init__(self, *args, **kwds):
		# self.contenedor = args[0]

		self.mst = args[0]
		self.cnt = self.mst.cnt

		self.id = kwds.pop('id')

		# QtGui.QFrame.__init__(self, *args)
		QtGui.QDockWidget.__init__(self, *args)

		# self.ui = detalles_ui.Ui_Form()
		self.ui = details_ui.Ui_DockWidget()
		self.ui.setupUi(self)

		self.ui.spacerX = []
		self.ui.laEntidadX = []
		self.ui.laCodigoX = []
		self.ui.laNombreX = []
		self.ui.laCostoX = []
		self.ui.laDescuentoX = []

		labels = [u"Ajuste", u"Descuento", u"Margen Real", u"Precio"]
		"""
		self.ui.pricesTA.setColumnCount(len(labels))
		self.ui.pricesTA.setHorizontalHeaderLabels(labels)

		self.ui.pricesTA.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.Stretch)
		"""
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('productsChanged()'), self.update)

		self.update()


	def update(self, id=None):
		if id:
			pass

		elif self.id:
			product = self.cnt.product(id=self.id)

			# print(product)

			aceptions = product.pop('aceptions')

			local = [aceptions.pop(index) for index, aception in enumerate(aceptions) if aception['rol_id']==self.cnt.app.holder['id']][0]

			self.clear()

			self.ui.laCodigo.setText("%s" % local['code'])
			self.ui.laNombre.setText(local['name'])
			# self.ui.laTipo.setText(self.cnt.attribute(code=product['kind']['code'])['name'])

			self.ui.laTipo.setText(product['kind']['name'])
			# self.ui.laUnidad.setText(self.cnt.attribute(code=product['unit_code'])['name'])
			self.ui.laUnidad.setText(product['unit_name'])
			# self.ui.laClasificacion.setText(self.cnt.attribute(id=product['classification_id'])['name'])
			self.ui.laClasificacion.setText(product['classification_name'])

			self.ui.laLinea.setText(product['lines'][0]['name'])

			self.ui.laMinimo.setText("%s" % product['minimum'])
			self.ui.laMaximo.setText("%s" % product['maximum'])
			self.ui.laActual.setText("%s" % product['current'])

			self.ui.laCosto.setText("%.2f" % product['meancost'])
			# self.ui.laImpuesto.setText("%.2f" % product['tax'])

			# print(product['taxes'])

			general = Decimal('0.00')
			special = Decimal('0.00')

			taxes = self.cnt.taxes()

			general = [x for x in taxes if 'default' in x['reference'] and x['code'] in [y['code'] for y in product['taxes']]][0]['value']
			#! Asumes only one special tax
			special0 = [x for x in taxes if x['reference'] == 'special' and x['code'] in [y['code'] for y in product['taxes']]]
			if special0:
				special = special0[0]['value']

			# print(general, special)

			# costoNeto = self.ui.edCostoPromedio.value() / (100+special) * (100+general)

			self.ui.laCostoNeto.setText("%.2f" % (product['meancost'] / (Decimal('100')+special) * (100+general)))

			self.ui.laMargen.setText("%.2f" % product['margin'])

			## PRECIOS
			"""
			self.ui.pricesTA.setRowCount(0)

			for rowIndex, rango in enumerate ( self.cnt.activePriceRules ) :

				# if rowIndex < len(aceptionLocal['precios_valor']):

				# atributoCero = [x for x in aceptionLocal['precios'] if x[3]==rango['id']]
				# if atributoCero:

				try:

					index = aceptionsLocal['prices_atributoId'].index(rango['id'])
					# price = atributoCero[0]

					self.ui.pricesTA.insertRow(rowIndex)

					item = QtGui.QTableWidgetItem("%s" % aceptionsLocal['prices_factor1'][index])
					item.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					self.ui.pricesTA.setItem(rowIndex, 0, item)

					item = QtGui.QTableWidgetItem("%s" % aceptionsLocal['prices_factor2'][index])
					item.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					self.ui.pricesTA.setItem(rowIndex, 1, item)

					item = QtGui.QTableWidgetItem("%s" % Decimal(aceptionsLocal['prices'][index]).quantize(Decimal('0.01')))
					item.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					self.ui.pricesTA.setItem(rowIndex, 3, item)

				except:
					pass

			self.ui.pricesTA.resizeColumnToContents(0)
			self.ui.pricesTA.resizeColumnToContents(1)
			self.ui.pricesTA.resizeColumnToContents(2)
			"""

			if self.ui.spacerX:
				self.ui.spacerX.pop()

			font = QtGui.QFont()
			font.setBold(True)
			font.setPointSize(8 * self.mst.layoutZoom)

			offset = 22

			index = 0
			for aception in aceptions:

				if len(self.ui.laCodigoX) >= index:
					self.ui.spacerX.append(QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred))
					self.ui.gridLayout.addItem(self.ui.spacerX[index], offset+1+index*7, 1, 1, 1)

					self.ui.laEntidadX.append(QtGui.QLabel(self.ui.frameDetalle))
					self.ui.laEntidadX[index].setFont(font)
					self.ui.gridLayout.addWidget(self.ui.laEntidadX[index], offset+1+index*7, 0, 1, 4)

					self.ui.laCodigoX.append([QtGui.QLabel(u"Código", self.ui.frameDetalle), QtGui.QLabel(self.ui.frameDetalle)])
					self.ui.laCodigoX[index][1].setFont(font)
					self.ui.gridLayout.addWidget(self.ui.laCodigoX[index][0], offset+2+index*7, 0, 1, 1)
					self.ui.gridLayout.addWidget(self.ui.laCodigoX[index][1], offset+2+index*7, 1, 1, 1)

					self.ui.laNombreX.append([QtGui.QLabel(u"Nombre", self.ui.frameDetalle), QtGui.QLabel(self.ui.frameDetalle)])
					self.ui.laNombreX[index][1].setFont(font)
					self.ui.gridLayout.addWidget(self.ui.laNombreX[index][0], offset+3+index*7, 0, 1, 1)
					self.ui.gridLayout.addWidget(self.ui.laNombreX[index][1], offset+3+index*7, 1, 1, 3)

					self.ui.laCostoX.append([QtGui.QLabel(u"Costo", self.ui.frameDetalle), QtGui.QLabel(self.ui.frameDetalle)])
					self.ui.laCostoX[index][1].setFont(font)
					self.ui.gridLayout.addWidget(self.ui.laCostoX[index][0], offset+4+index*7, 0, 1, 1)
					self.ui.gridLayout.addWidget(self.ui.laCostoX[index][1], offset+4+index*7, 1, 1, 1)

					self.ui.laDescuentoX.append([QtGui.QLabel(u"Descuento", self.ui.frameDetalle), QtGui.QLabel(self.ui.frameDetalle)])
					self.ui.laDescuentoX[index][1].setFont(font)
					self.ui.gridLayout.addWidget(self.ui.laDescuentoX[index][0], offset+5+index*7, 0, 1, 1)
					self.ui.gridLayout.addWidget(self.ui.laDescuentoX[index][1], offset+5+index*7, 1, 1, 1)

					self.ui.gridLayout.addItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding), offset+6+index*7, 1, 1, 1)

				self.ui.laEntidadX[index].setText("%s %s" % (aception['rol']['person']['name'], aception['rol']['person']['name2']))
				self.ui.laEntidadX[index].show()
				self.ui.laCodigoX[index][1].setText("%s" % aception['code'])
				self.ui.laCodigoX[index][1].show()
				self.ui.laCodigoX[index][0].show()
				self.ui.laNombreX[index][1].setText("%s" % aception['name'])
				self.ui.laNombreX[index][1].show()
				self.ui.laNombreX[index][0].show()
				self.ui.laCostoX[index][1].setText("%s" % aception['cost'])
				self.ui.laCostoX[index][1].show()
				self.ui.laCostoX[index][0].show()
				self.ui.laDescuentoX[index][1].setText("%s" % aception['generaldiscount'])
				self.ui.laDescuentoX[index][1].show()
				self.ui.laDescuentoX[index][0].show()

				index += 1

			self.ui.spacerX.append(QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding))
			self.ui.gridLayout.addItem(self.ui.spacerX[len(aceptions)-1], offset+6+(len(aceptions)-1)*6, 1, 1, 1)
			self.setWindowTitle("%s %s" % (local['code'], local['name']))


	def clear(self):
		# print "\nproducts.view.Details.clear()"
		self.ui.laCodigo.clear()
		self.ui.laNombre.clear()
		self.ui.laClasificacion.clear()
		self.ui.laCosto.clear()
		self.ui.laImpuesto.clear()
		self.ui.laMargen.clear()
		# self.ui.laAjuste1.clear()
		# self.ui.laDescuento1.clear()
		# self.ui.laMargenF1.clear()
		# self.ui.laPrecio1.clear()
		self.ui.laMinimo.clear()
		self.ui.laMaximo.clear()
		self.ui.laActual.clear()
#        for index in priceRange(len(self.ui.laCodigoX)):
#            self.ui.laEntidadX[index].hide()
#            self.ui.laCodigoX[index][0].hide()
#            self.ui.laCodigoX[index][1].hide()
#            self.ui.laNombreX[index][0].hide()
#            self.ui.laNombreX[index][1].hide()
#            self.ui.laCostoX[index][0].hide()
#            self.ui.laCostoX[index][1].hide()
#            self.ui.laDescuentoX[index][0].hide()
#            self.ui.laDescuentoX[index][1].hide()


	def mostrar(self, id):
		f=g
		self.id = id
		self.clear()
		self.update()
		self.show()



class Splitter(QtGui.QSplitter):

	def __init__(self, *args):
		self.orientation = args[0]
		QtGui.QSplitter.__init__(self, *args)

	def createHandle(self):
		return Handle(self.orientation, self)



class Handle(QtGui.QSplitterHandle):

	def __init__(self, *args):
		QtGui.QSplitterHandle.__init__(self, *args)

	def mouseDoubleClickEvent(self, event):
		self.emit(QtCore.SIGNAL("handlePressed"))


class Modelo(QtCore.QAbstractListModel):

	def __init__(self, *args):
		QtCore.QAbstractListModel.__init__(self, *args)
		self.__data = []

	def clear(self):
		self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount())
		self.__data = []
		self.endRemoveRows()

	def data(self, index, role=QtCore.Qt.DisplayRole):
		if index.row() != -1:
			if role in [QtCore.Qt.DisplayRole]:
				return self.__data[index.row()][0]
			elif role in [QtCore.Qt.EditRole]:
				return self.__data[index.row()][1]
			elif role == QtCore.Qt.TextAlignmentRole:
				return int(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
			elif role == QtCore.Qt.UserRole:
				return self.__data[index.row()][2]
		return

	def insertRow(self, row, parent=QtCore.QModelIndex()):
		self.__data.insert(row, [u"", u"", u""])
		return True

	def rowCount(self, parent=QtCore.QModelIndex()):
		return len(self.__data)

	def reload(self):
		pass

	def setData(self, index, valor, role=QtCore.Qt.DisplayRole):
		if role == QtCore.Qt.DisplayRole:
			self.__data[index.row()][0] = valor
		elif role == QtCore.Qt.EditRole:
			self.__data[index.row()][1] = valor
		elif role == QtCore.Qt.UserRole:
			self.__data[index.row()][2] = valor
		else:
			print (12345, role)
		return True


class Kardex(QtGui.QDockWidget):

	def __init__(self, *args, **kwds):
		self.mst = args[0]
		self.cnt = self.mst.cnt

		self.oldId = kwds.pop('id', None)

		QtGui.QDockWidget.__init__(self, *args)

		self.ui = kardex_ui.Ui_DockWidget()
		self.ui.setupUi(self)

		self.aception = self.cnt.aception(product_id=self.oldId)

		labels = [u"Fecha", u"Cantidad", u"Actual", u"Pr.Neto", u"Entidad", u"Documento", u"Precio"]
		self.ui.dataTA.setColumnCount(len(labels))
		self.ui.dataTA.setHorizontalHeaderLabels(labels)

		self.ui.dataTA.horizontalHeader().setResizeMode(4, QtGui.QHeaderView.Stretch)

		self.setWindowTitle("Kardex de %s %s %s" % (self.aception['code'], self.aception['name'], self.aception['lines'][0]['name']))

		self.connect(self.mst.eventRouter, QtCore.SIGNAL('movementsChanged()'), self.updateMovimientos)

		self.updateMovimientos()

		self.ui.dataTA.resizeColumnToContents(0)
		self.ui.dataTA.resizeColumnToContents(1)
		self.ui.dataTA.resizeColumnToContents(2)
		self.ui.dataTA.resizeColumnToContents(3)
		self.ui.dataTA.resizeColumnToContents(5)
		self.ui.dataTA.resizeColumnToContents(6)


	def updateMovimientos(self):
		# print "producs.view.Kardex.updateMovimientos()"

		filters = {}
		filters['subject_id'] = self.aception['product_id']
		filters['order'] = 'date'
		filters['kind'] = {'code':[11511, 12515, 12517, 13515, 13517]}     # Remision, Factura,

		movimientos = self.cnt.documentItems(**filters)

		# print(movimientos)

		self.ui.dataTA.setRowCount(0)

		font = QtGui.QFont()
		font.setBold(True)

		current = 0

		movimientos.reverse()

		# print(movimientos)

		for movimiento in movimientos:

			# print(movimiento)

			if movimiento['document']['status'] != 'cancelled':

				self.ui.dataTA.insertRow(0)

				## Quantity
				quantity = movimiento['quantity']

				netPrice = movimiento['net_price']

				## Price / Import
				discountFactor = Decimal("1.00")
				taxFactor = Decimal("1.00")

				try:

					# if movimiento['discountf']:
						# discountFactor = discountFactor * (100-movimiento['discountf'])/100
					# if movimiento['document']['discountpercent']:
						# discountFactor = discountFactor * (100-movimiento['document']['discountpercent'])/100

					# if movimiento['document']['process']['kind'] in [u'Mercancía'] or movimiento['document']['process']['kind']['code'] in [12113]:
						# taxFactor = taxFactor * (100 + movimiento['taxf']) / 100
					# elif movimiento['document']['process']['kind'] in [u'venta'] or movimiento[ 'document']['process']['kind']['code'] in [13113]:
						# pass

					# netPrice = movimiento['price'] * discountFactor * taxFactor

					netImport = quantity * netPrice

					## Base para ajuste de stock
					sentido = 1
					if movimiento['document']['process']['kind'] in [u'venta'] or movimiento['document']['process']['kind']['code'] in [13113]:
						sentido = -1

					current += quantity * sentido

					if movimiento['stock'] != current:
						movTmp = {}
						movTmp['id'] = movimiento['id']
						movTmp['stock'] = current

						self.cnt.documentItem_set(**movTmp)

				except:

					print ( "Error en products.Kardex.updateMovimientos()" )
					print ( "    Cálculos")
					print ( "    movimiento: {}".format(movimiento) )

					raise

				try:
					## FECHA
					item = QtGui.QTableWidgetItem(movimiento['document']['date'].strftime("%d %b %Y"))
					item.setFont(font)
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					self.ui.dataTA.setItem(0, 0, item)

					## Quantity
					item = QtGui.QTableWidgetItem("%s" % quantity)
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					item.setTextAlignment(QtCore.Qt.AlignCenter)
					self.ui.dataTA.setItem(0, 1, item)

					## Current Stock
					item = QtGui.QTableWidgetItem("%.2f" % current)
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
					self.ui.dataTA.setItem(0, 2, item)

					## Net Price
					item = QtGui.QTableWidgetItem("%s" % movimiento['net_price'].quantize(Decimal('0.01')))
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
					item.setToolTip("Importe: {}".format(movimiento['net_price'] * movimiento['quantity']))
					self.ui.dataTA.setItem(0, 3, item)

					## ENTIDAD
					item = QtGui.QTableWidgetItem("%s %s" % (movimiento['document']['rol']['person']['name'], movimiento['document']['rol']['person']['name2']))
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					self.ui.dataTA.setItem(0, 4, item)

					## FOLIO
					item = QtGui.QTableWidgetItem(movimiento['document']['number'])
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					self.ui.dataTA.setItem(0, 5, item)

					## list Price
					# if movimiento['cost'] is None:
						# price = movimiento['price']
					# else:
						# price = Decimal('0.00')
					price = movimiento['price']
					item = QtGui.QTableWidgetItem("{}".format(price.quantize(Decimal('0.01'))))
					item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
					item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
					item.setToolTip("Importe: {}".format(price * movimiento['quantity']))
					self.ui.dataTA.setItem(0, 6, item)

				except:
					print ("Error en products.Kardex.updateMovimientos()" )
					print ('movimiento', movimiento)
					raise

		# self.ui.dataTA.resizeColumnToContents(0)
		# self.ui.dataTA.resizeColumnToContents(2)
		# self.ui.dataTA.resizeColumnToContents(3)
		# self.ui.dataTA.resizeColumnToContents(4)
		# self.ui.dataTA.resizeColumnToContents(5)
		# self.ui.dataTA.resizeColumnToContents(6)

		#!
		# current = self.calculateCurrent()

		# self.cnt.product_push(id=self.aception['product_id'], current=current)


	# def calculateCurrent(self):
		# current = 0
		# for rowIndex in range(self.ui.dataTA.rowCount(), 0, -1):
			# cantidad = Decimal(str(self.ui.dataTA.item(rowIndex-1, 3).text()))
			# current += cantidad
			# item = QtGui.QTableWidgetItem("%.2f" % current)
			# item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
			# item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
			# self.ui.dataTA.setItem(rowIndex-1, 6, item)
		# return current




class Model(QtCore.QAbstractListModel):

	def __init__(self, *args):
		QtCore.QAbstractListModel.__init__(self, *args)
		self.__data = []

	def clear(self):
		# self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount())
		self.__data = []
		self.reset()
		# self.endRemoveRows()

	def data(self, index, role=QtCore.Qt.EditRole):
		if role in [QtCore.Qt.DisplayRole]:
			return self.__data[index.row()][0]
		elif role == QtCore.Qt.EditRole:
			return self.__data[index.row()][1]
		elif role == QtCore.Qt.TextAlignmentRole:
			# if index.column() == self.COL_QUANTITY:
				# return int(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
			# if index.column() in [self.COL_PRICE, self.COL_AMOUNT]:
				# return int(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
			return int(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
		elif role == 1001:
			return self.__data[index.row()][2]
		elif role == 1002:
			return self.__data[index.row()][3]
		elif role == 1003:
			return self.__data[index.row()][4]
		elif role == 1004:
			return self.__data[index.row()][5]
		else:
			return


	def insertRow(self, row, parent=QtCore.QModelIndex()):
		self.__data.insert(row, [u"", u""])
		return True


	def rowCount(self, parent=QtCore.QModelIndex()):
		return len(self.__data)


	def setData(self, index, value, role=QtCore.Qt.DisplayRole):
		if index.row() >= len(self.__data):
			self.__data.append([None, None, None, None, None, None, None])

		if role in [QtCore.Qt.DisplayRole]:
			self.__data[index.row()][0] = value
		elif role ==  QtCore.Qt.EditRole:
			self.__data[index.row()][1] = value
		elif role == 1001:
			self.__data[index.row()][2] = value
		elif role == 1002:
			self.__data[index.row()][3] = value
		elif role == 1003:
			self.__data[index.row()][4] = value
		elif role == 1004:
			self.__data[index.row()][5] = value
		else:
			print ("puaj")
		return True



class OptionsFR(QtGui.QFrame):

	def __init__(self, *args, **kwds):

		self.mst = kwds.pop('mst', None)
		self.cnt = self.mst.cnt

		args = args[:1] + args[2:]

		self._state = [IDLE]

		QtGui.QFrame.__init__(self, *args, **kwds)


		layoutZoom = self.cnt.app.master.layoutZoom

		font = QtGui.QFont()
		font.setPointSize(10 * layoutZoom)
		font.setWeight(75)
		font.setBold(True)

		self.setStyleSheet("""#frVentas{
			border-style: solid;
			border-width: 1px;
			border-radius: 9px;
			border-bottom-color: #A0A0A0;
			border-right-color: #A0A0A0;
			border-left-color: #FFFFFF;
			border-top-color: #FFFFFF;
			background-color: #F0F0D0;
			}""")

		self.ui = tools_ui.Ui_frame()

		self.ui.setupUi(self)

		self.ui.chCapturaClasificacionObligatoria.setFont(font)
		self.ui.chCapturaClasificacionObligatoria.attributeName = 'mustCaptureClassification'
		self.connect(self.ui.chCapturaClasificacionObligatoria, QtCore.SIGNAL('stateChanged(int)'), self.toggle)

		self.ui.chCapturaLinea.setFont(font)
		# self.ui.chCapturaLinea.attributeName = 'canEditProductLine'
		# self.connect(self.ui.chCapturaLinea, QtCore.SIGNAL('stateChanged(int)'), self.toggle)
		self.connect(self.ui.chCapturaLinea, QtCore.SIGNAL('clicked()'), self.useLine_toggle)


		self.connect(self.ui.addUnitBU, QtCore.SIGNAL('clicked()'), self.addUnit)

		self.loadUnits()

		# self.state_reset()


	def init(self):
		self.state = BUSY

		self.ui.chCapturaClasificacionObligatoria.setChecked(self.cnt.mustCaptureClassification())
		self.ui.chCapturaLinea.setChecked(self.cnt.canEditProductLine())

		self.state_reset()


	def addUnit(self):
		name = self.ui.unitED.text()
		self.cnt.app.model.setAttribute(category='unit', name='{}'.format(name))
		self.loadUnits()


	def loadUnits(self):
		self.ui.unitsLI.clear()
		units = self.cnt.unitKinds()
		for unit in units:
			self.ui.unitsLI.addItem(unit['name'])


	def state_get(self):
		return self._state[-1]
	def state_set(self, value):
		self._state.append(value)
	state = property(state_get, state_set)
	def state_reset(self):
		self._state.pop()


	def toggle(self):
		# print("""    products.view.OptionsFR.toggle()""")
		if self.state is IDLE:
			widget = self.sender()

			exec('''self.cnt.set{}{}({})'''.format(widget.attributeName[0].capitalize(), widget.attributeName[1:], widget.isChecked()))
			exec('''self.mst.eventRouter.emit(QtCore.SIGNAL('{}Changed()'))'''.format(widget.attributeName))

			# widget = self.sender()
			# exec('''self.cnt.set{}{}({})'''.format(widget.attributeName[0].capitalize(), widget.attributeName[1:], widget.isChecked()))
			# exec('''self.mst.eventRouter.emit(QtCore.SIGNAL('{}Changed()'))'''.format(widget.attributeName))


	def useLine_toggle(self):
		# print("useLine_toggle()")

		if self.state is IDLE:
			self.cnt.useLine_set(self.sender().isChecked())
			self.mst.eventRouter.emit(QtCore.SIGNAL("useLine_changedTo(bool)"), self.sender().isChecked())

		# print("useLine_toggle() - END")




"""
  This is a GUI module
	It's only purpose is to interact with the user to show him data and
	to obtain data from him.
	To enforce this, al data obtained from the user will be containde in
	dictionaries mapped to data entering widgets.
	All data processing must be made at the manager (model) module.

  Issues
	Detalles se confundirá cuando el número de rangos de precio activos aumente, ya
	que no tendrá registro para los productos capturados anteriormente.


"""

