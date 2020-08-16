# -*- coding: utf-8 -*-

 ##############################################
 ##                                            ##
 ##              Products package               ##
 ##                  selector                   ##
 ##                                             ##
 ##              from Basiq Series              ##
 ##           by Críptidos Digitales            ##
 ##                 GPL (c)2008                 ##
  ##                                            ##
	##############################################

"""
"""

from __future__ import print_function

__version__ = "0.1.1"

debuging = False
prefix = "        products.selector."

import sys
from decimal import Decimal
import datetime
import colorsys
from PyQt4 import QtCore, QtGui

from products import selector_ui


class Controller(QtCore.QObject):

	def __init__(self, *args, **kwds):
		self.view = args[0]
		self.app = self.view.cnt.app

		QtCore.QObject.__init__(*args, **kwds)

	@property
	def auxiliaryCode_isVisible(self):
		# print("""        products.selector.Controller.auxiliaryCode_isVisible""")
		return not not int(self.app.model.attribute_get(name='useAuxiliaryCode', cast_='sale')['value'])

	@property
	def line_isVisible(self):
		# print("""        products.selector.Controller.line_isVisible""")
		return not not int(self.app.model.attribute_get(name='useLine', cast_='sale')['value'])

	def lines(self):
		return self.app.model.getProductLines()

	@property
	def ownCode_isVisible(self):
		# print("""        products.selector.Controller.ownCode_isVisible""")
		return not not int(self.app.model.attribute_get(name='useOwnCode', cast_='sale')['value'])

	@property
	def universalCode_isVisible(self):
		# print("""        products.selector.Controller.universalCode_isVisible""")
		return not not int(self.app.model.attribute_get(name='useUniversalCode', cast_='sale')['value'])




class Form(QtGui.QFrame):

	# def origin(self, index=0):
		# return self._origin_data[index]

	def setStyleColor(self, color):

		def transform(color):
			hsv = colorsys.rgb_to_hsv(int(color[1:3], 16)/255.0, int(color[3:5], 16)/255.0, int(color[5:7], 16)/255.0)
			tmp = [hex(int(x*255)) for x in colorsys.hsv_to_rgb(hsv[0], hsv[1]*1.45, hsv[2]*0.95)]
			return "#{}{}{}".format(*[x[x.index('x')+1:].zfill(2) for x in tmp])

		self.setStyleSheet("background-color:#FFF8D0;")

		self.ui.originFR.setStyleSheet("background-color:qradialgradient(cx:.5, cy:.5, radius:1,fx:.5, fy:.25, stop: 0 {}, stop:1 {}); border:1 outset {}; border-radius:6;".format(color, transform(color), color))

		self.ui.upcFR.setStyleSheet("background-color:qradialgradient(cx:.5, cy:.5, radius:1,fx:.5, fy:.25, stop: 0 {}, stop:1 {}); border:1 outset {}; border-radius:6;".format(color, transform(color), color))

		self.ui.codeFR.setStyleSheet("background-color:qradialgradient(cx:.5, cy:.5, radius:1,fx:.5, fy:.25, stop: 0 {}, stop:1 {}); border:1 outset {}; border-radius:6;".format(color, transform(color), color))

		self.ui.code2FR.setStyleSheet("background-color:qradialgradient(cx:.5, cy:.5, radius:1,fx:.5, fy:.25, stop: 0 {}, stop:1 {}); border:1 outset {}; border-radius:6;".format(color, transform(color), color))

		self.ui.nameFR.setStyleSheet("background-color:qradialgradient(cx:.5, cy:.5, radius:1,fx:.5, fy:.25, stop: 0 {}, stop:1 {}); border:1 outset {}; border-radius:6;".format(color, transform(color), color))

		self.ui.lineFR.setStyleSheet("background-color:qradialgradient(cx:.5, cy:.5, radius:1,fx:.5, fy:.25, stop: 0 {}, stop:1 {}); border:1 outset {}; border-radius:6;".format(color, transform(color), color))


	def __init__(self, *args, **kwds):
		self.owner = args[0]

		if 'mst' in kwds:
			self.mst = kwds['mst']
		else:
			self.mst = args[0].mst

		if 'cnt' in kwds:
			self.cnt = kwds['cnt']
		else:
			self.cnt = self.mst.cnt

		self.app = self.cnt.app

		self.lcnt = Controller(self)

		QtGui.QFrame.__init__(self, *args)

		# Colocadas aquí para ver si se soluciona el uso de la misma instancia de ellas entre diferentes instancias del Selector.
		self._origin_data = []
		self._origin_currentIndex = 0
		self._origin_maxIndex = 1

		# self.ui = selector_ui.Ui_selectorFR()
		self.ui = selector_ui.Ui_Frame()
		self.ui.setupUi(self)

		frameFont = QtGui.QFont()
		frameFont.setBold(True)
		frameFont.setPointSize(11 * self.mst.layoutZoom)

		labelFont = QtGui.QFont()
		labelFont.setPointSize(10 * self.mst.layoutZoom)
		labelFont.setBold(True)


		## Código de producto
		self.ui.codeLA.setFont(labelFont)
		self.ui.codeED.setFont(frameFont)
		completer = QtGui.QCompleter([], self.ui.codeED)
		completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		modelx = Model(completer)
		completer.setModel(modelx)
		self.ui.codeED.setCompleter(completer)
		self.ui.codeED.setSymbols(u'-_/" ')
		self.connect(completer, QtCore.SIGNAL("activated(QModelIndex)"), self.codeSelected)
		self.connect(self.ui.codeED, QtCore.SIGNAL('returnPressed()'), self.codeCaptured)
		self.connect(self.ui.codeED, QtCore.SIGNAL('textEdited(QString)'), self.codeEdited)

		# self.updateOwnCodeUsage()

		## Universal Product Code
		self.ui.UPCLA.setFont(labelFont)
		self.ui.UPCED.setFont(frameFont)
		completer = QtGui.QCompleter([], self.ui.UPCED)
		completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		modelx = Model(completer)
		completer.setModel(modelx)
		self.ui.UPCED.setCompleter(completer)
		self.connect(completer, QtCore.SIGNAL("activated(QModelIndex)"), self.UPCSelected)
		self.connect(self.ui.UPCED, QtCore.SIGNAL('returnPressed()'), self.UPCCaptured)
		self.connect(self.ui.UPCED, QtCore.SIGNAL('textEdited(QString)'), self.UPCEdited)

		# self.UPC_usageUpdate()


		## Auxiliary Code
		self.ui.code2LA.setFont(labelFont)
		self.ui.code2ED.setFont(frameFont)
		completer = QtGui.QCompleter([], self.ui.code2ED)
		completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.ui.code2ED.setCompleter(completer)
		self.connect(self.ui.code2ED, QtCore.SIGNAL('textEdited(QString)'), self.code2Edited)

		# self.updateAuxiliaryCodeUsage()


		## Product name
		self._nameLabelText = [u" &Nombre de artículo"]

		self.ui.nameLA.setFont(labelFont)
		self.ui.nameED.setFont(frameFont)

		completer = QtGui.QCompleter([], self.ui.nameED)
		completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		completer.setWrapAround(False)
		completer.popup().setFont(labelFont)

		modelx = Model(completer)
		modelx.productIdRole = 1003
		modelx.aceptionIndex = 1004

		completer.setModel(modelx)

		self.ui.nameED.setCompleter(completer)
		self.ui.nameED.setSymbols(u"""-_.,#"'/*°|$%&()[] """)

		self.connect(completer, QtCore.SIGNAL("activated(QModelIndex)"), self.nameSelected)
		self.connect(self.ui.nameED, QtCore.SIGNAL('returnPressed()'), self.nameCaptured)
		self.connect(self.ui.nameED, QtCore.SIGNAL("textEdited(QString)"), self.nameEdited)


		## Line
		# self.ui.cbLinea.lineEdit().setFont(frameFont)
		self.ui.lineLA.setFont(labelFont)
		self.ui.lineCB.setFont(frameFont)
		#~ self.connect(self.ui.frLinea, QtCore.SIGNAL(), self.lineChanged)

		# self.updateUseLine()


		## Add Product button
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/Plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.ui.newProductBU.setIcon(icon)
		self.connect(self.ui.newProductBU, QtCore.SIGNAL('clicked()'), self.product_add)


		self.connect(self.mst.eventRouter, QtCore.SIGNAL('lineasChanged()'), self.lines_load)
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('saleAuxiliaryCodeUsageChanged()'), self.auxiliaryCodeVisibility_update)
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('saleUniversalCodeUsageChanged()'), self.UPCVisibility_update)
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('saleOwnCodeUsageChanged()'), self.ownCodeVisibility_update)
		self.connect(self.mst.eventRouter, QtCore.SIGNAL('useLineChanged()'), self.lineVisibility_update)


		self.connect(self.ui.originLA, QtCore.SIGNAL('clicked()'), self.origin_toggle)

		self.ui.codeED.setText('', initialToo=True)
		self.ui.code2ED.setText('', initialToo=True)
		self.ui.nameED.setText('', initialToo=True)


	def init(self):
		if debuging: print("\n{}Form.init()".format(prefix))
		try:
			self.ownCodeVisibility_update()
			self.UPCVisibility_update()
			self.auxiliaryCodeVisibility_update()
			self.lineVisibility_update()
			# self.lines_load()

			# self.origin_set(self.cnt.app.holder, 0)
			# self.origin_set(None, 0)

			# self._nameLabelText = [u" &Nombre LOCAL de artículo", u" &Nombre de artículo de {} {} ...".format(self.origin()['person']['name'], self.origin()['person']['name2'])[:10]]
			self._nameLabelText = [u" &Nombre LOCAL de artículo"]

			self.ui.newProductBU.setToolTip(u'Presiona para capturar un producto nuevo')

			self.ui.loadAllBU.setToolTip(u'Presiona para cargar todos los productos del proveedor seleccionado')

		except:
			print ("\nERROR @ {}Form.init()\n            {}\n".format(prefix, sys.exc_info()))
			raise

		if debuging: print("{}Form.init() - END\n".format(prefix))


	def setEnabled(self, value):
		QtGui.QFrame.setEnabled(self, value)
		self.ui.codeED.setEnabled(value)
		self.ui.code2ED.setEnabled(value)
		self.ui.nameED.setEnabled(value)
		self.ui.lineCB.setEnabled(value)


	def clear(self):
		self.ui.codeED.clear()
		self.ui.code2ED.clear()
		self.ui.nameED.clear()
		self.ui.lineCB.clear()


	def codeCaptured(self):
		if self.ui.codeED.completer().completionCount() == 1:
			if self.ui.codeED.completer().popup().currentIndex().row() == -1:
				modelx = self.ui.codeED.completer().completionModel()
				index = modelx.index(0, 0)
				self.codeSelected(index)


	def codeSelected(self, completerModelIndex):
		# print("products.selector.Form.codeSelected()")
		completerRow = completerModelIndex.row()

		modelx = self.ui.codeED.completer().completionModel()

		# acepcion = self.cnt.aception(id=modelx.data(modelx.index(completerRow, 0), 1001).toInt()[0])

		# ! checar el costo

		## Broadcast

		self._data = modelx.data(modelx.index(completerRow,0), self.ui.codeED.completer().model().DATAROLE_PRODUCT).toString()

		# print self._data

		self.emit(QtCore.SIGNAL('productSelected()'))

		self.ui.codeED.setText("")
		self.ui.nameED.setText("")
		self.ui.lineCB.setCurrentIndex(-1)

		self.ui.nameFR.setEnabled(True)
		self.ui.nameFR.setToolTip("")
		self.ui.lineFR.setEnabled(True)

		# self.ui.tablaPartidas.setCurrentCell(self.ui.tablaPartidas.rowCount()-1, self.COL_QUANTITY)
		# self.ui.tablaPartidas.cellWidget(self.ui.tablaPartidas.rowCount()-1, self.COL_QUANTITY).selectAll()
		#~ self.ui.tablaPartidas.editItem(self.ui.tablaPartidas.item(self.ui.tablaPartidas.rowCount()-1, self.COL_QUANTITY))

		# self.status_update()


	def codeEdited(self, texto):
		# print "products.selector.Form.codeEdited()"

		self._data = None

		if len(texto) < 2:
			self.ui.codeED.completer().model().clear()

		elif len(texto) == 2:
			filtros = {}
			filtros['code LIKE'] = u"{}".format(texto.toUpper())
			filtros['rol_id'] = self.origin()['id']

			# acepciones = manejador.dameAcepciones(**filtros)
			products = self.cnt.products(**filtros)

			model = self.ui.codeED.completer().model()
			model.clear()

			if not products:
				self.ui.codeFR.setToolTip(u"El proveedor no tiene productos que lleven estas iniciales en el código")
			else:
				self.ui.codeFR.setToolTip(u"")
				## Set Model Data
				for row, product in enumerate(products):
					aceptionForOrigin = [x for x in product['aceptions'] if x['rol_id'] == self.origin()['id']][0]
					model.setData(row, "%s %s" % (aceptionForOrigin['code'], aceptionForOrigin['name']))
					if product['current'] is None:
						product['current'] = Decimal('0')
					model.setData(row, repr(product), model.DATAROLE_PRODUCT)

				model.reset()

		if self.ui.codeED.text():
			self.ui.nameFR.setEnabled(False)
			self.ui.nameFR.setToolTip(u"Desactivado si se busca por codigo")
			self.ui.lineFR.setEnabled(False)
			self.ui.lineFR.setToolTip(u"Desactivado si se busca por codigo")
		else:
			self.ui.nameFR.setEnabled(True)
			self.ui.nameFR.setToolTip("")
			self.ui.lineFR.setEnabled(True)
			self.ui.lineFR.setToolTip(u"")


	def code2Edited(self, texto):

		self._data = None

		self.sender().setText(self.sender().text().toUpper())
		filtros = {}
		filtros['code'] = u"{}".format(texto.toUpper())
		# 2015.01.18 filtros['rol_id'] = self.cnt.app.holder['id']
		filtros['rol_id'] = -1
		if self.ui.edClasificacion.text():
			filtros['clasificacion'] = u"{}".format(self.ui.edClasificacion.text())

		acepciones = self.cnt.aceptions(**filtros)

		ids = [x.id for x in acepciones]
		codigos = ["%s" % x.code for x in acepciones]

		self.sender().completer().data = ids
		self.sender().completer().model().setStringList(codigos)


	_data = None
	@property
	def data(self):
		# print("    products selector   Form.data()")
		data = eval("{}".format(self._data))
		# print("    products selector   Form.data() - END")
		return data
		# product = eval("{}".format(product))

	_dealer = None      # Object
	def dealer(self):
		return self._dealer

	def dealer_set(self, value):
		self._dealer = value
		# if self._origin_currentIndex:
		self.origin_set(value)
		# self.origin_setCurrent(value['id'])



	def lineVisibility_update(self):
		if self.lcnt.line_isVisible:
			self.lines_load()
			self.ui.lineFR.show()
		else:
			self.ui.lineFR.hide()


	def lines_load(self):

			self.ui.lineCB.clear()

			lines = self.lcnt.lines()

			lines = self.cnt.productLines()

			for line in lines:

				self.ui.lineCB.addItem(line['name'], line['id'])


	def nameLabelText_get(self):
		return self.ui.nameLA.text()
	def nameLabelText_set(self, value, index=None):
		if index is None:
			if type(value) is list:
				self._nameLabelText = value
			else:
				self._nameLabelText[self._origin_currentIndex] = value
		elif index < len(self.ui._nameLabelText):
			self._nameLabelText[index] = value
		elif index == len(self.ui._nameLabelText):
			self._nameLabelText.append(value)
		else:
			print ('puaaaaaj nameLabelText_set()', index, value)
		#! Should consider origin's len
	nameLabelText = property(nameLabelText_get, nameLabelText_set)


	def nameLabelText_update(self):
		text = self.nameLabelText[self._origin_currentIndex]
		if '{' in text:
			data = text[text.find('{')+1:text.rfind('}')]
			text = text.replace(data, '')
			text = eval("""text.format({})""".format(data))
		self.ui.nameLA.setText(text)


	def nameCaptured(self):
		if self.ui.nameED.completer().completionCount() == 1:
			if self.ui.nameED.completer().popup().currentIndex().row() == -1:
				modelx = self.ui.nameED.completer().completionModel()
				index = modelx.index(0, 0)
				self.nameSelected(index)


	def nameEdited(self, texto):
		# print "products.selector.Form.nameEdited()"

		self._data = None

		if len(texto) < 2:
			self.ui.nameED.completer().model().clear()

		elif len(texto) == 2:
			filtros = {}
			filtros['name like'] = u"{}".format(texto)
			filtros['rol_id'] = self.origin()['id']
			filtros['status'] = [40161, 40163]
			# if self.ui.edClasificacion.text():
				# filtros['linea'] = unicode(self.ui.edClasificacion.currentText())
			filtros['order'] = "name"
			# f=g
			products = self.cnt.products(**filtros)

			model = self.ui.nameED.completer().model()
			model.clear()

			## Set Model Data
			row = 0
			for index, product in enumerate(products):

				if [x for x in product['aceptions'] if x['rol_id'] == self.origin()['id']]:

					aceptionForOrigin = [x for x in product['aceptions'] if x['rol_id'] == self.origin()['id']][0]

					name = aceptionForOrigin['name'].replace(u'á','a').replace(u'é','e').replace(u'í','i').replace(u'ó','o').replace(u'ú','u')

					model.setData(row, u"{} ' {} ' {}".format(name, product['lines'][0]['name'], aceptionForOrigin['code']))

					model.setData(row, repr(product), model.DATAROLE_PRODUCT)
					row += 1

			model.reset()


	def nameSelected(self, completerModelIndex=None):
		# print "products.selector.Form.nameSelected()"
		completerRow = completerModelIndex.row()

		model = self.ui.nameED.completer().completionModel()

		# ! checar el costo

		# print( 101, "{}".format(model.data(model.index(completerRow, 0), self.ui.nameED.completer().model().DATAROLE_PRODUCT).toString()) )
		# print( 102, type(eval("{}".format(model.data(model.index(completerRow, 0), self.ui.nameED.completer().model().DATAROLE_PRODUCT).toString()))))

		try:
			self._data = model.data(model.index(completerRow, 0), self.ui.nameED.completer().model().DATAROLE_PRODUCT).toString()
		except:
			self._data = model.data(model.index(completerRow, 0), self.ui.nameED.completer().model().DATAROLE_PRODUCT)

		self.emit(QtCore.SIGNAL('productSelected()'))

		self.ui.codeED.setText("")
		self.ui.nameED.setText("")
		self.ui.lineCB.setCurrentIndex(-1)

		self.ui.nameFR.setEnabled(True)
		self.ui.nameFR.setToolTip("")
		self.ui.lineFR.setEnabled(True)



	def origin(self, index=None):
		if index is None:
			return self._origin_data[self._origin_currentIndex]

			## Currently active requested
			# if self._origin_currentIndex == 0:
				## Give local
				# return self._origin_data[0]
			# else:
				## Make dealer current and give
				# index = [x[0] for x in enumerate(self._origin_data) if x[1]['id'] == self.dealer()['id']][0]
				# self._origin_currentIndex = index
				# return self._origin_data[self._origin_currentIndex]

		else:
			return self._origin_data[index]

	# def origin_current(self):
		# return self._origin_data[self._origin_currentIndex]

	def origin_set(self, origin, index=None):
		self.app.log2sys ( 'info', "			Form.origin_set()							@ products.selector" )

		## Ensure got object for origin
		if type(origin) == int:
			origin = self.cnt.origin(id=origin)

		if index:
			self._origin_data[index] == origin
		else:
			try:
				index0 = [x[0] for x in enumerate(self._origin_data) if x[1]['id'] == origin['id']]
				if not index0:
					self._origin_data.append(origin)
					self._nameLabelText.append(u" &Nombre de artículo de {}".format(u"{} {} ...".format(origin['person']['name'], origin['person']['name2'])[:10]))
				else:
					self._origin_data[index0[0]] = origin
					self._nameLabelText[index0[0]] = u" &Nombre de artículo de {}".format(u"{} {} ...".format(origin['person']['name'], origin['person']['name2'])[:10])
			except:
				print ("    ==== ERROR @ products selector Form.origin_set()")
				print (sys.exc_info())
				print (index0)
				print (origin)
				print (self._origin_data)


		index = [x[0] for x in enumerate(self._origin_data) if x[1]['id'] == origin['id']][0]

		self._origin_currentIndex = index
		self.origin_update()

		self.app.log2sys ( 'info', "			Form.origin_set() - end						@ products.selector" )


	def origin_setCurrent(self, id):
		f=k
		# print "products.selector.Form.origin_setCurrent()", id
		foundOrigin =  [x[0] for x in enumerate(self._origin_data) if x[1]['id'] == id]

		if not foundOrigin:
			self.origin_set(id)
			foundOrigin =  [x[0] for x in enumerate(self._origin_data) if x[1]['id'] == id]

		self._origin_currentIndex = foundOrigin[0]
		self.origin_update()

	def origin_toggle(self):
		# print 'products.selector.Form.origin_togle()'

		if self._origin_currentIndex == self._origin_maxIndex:
			self._origin_currentIndex = 0
		else:
			self._origin_currentIndex += 1

		self.origin_update()

	def origin_update(self, index=None):
		# print("""products.selector.Form.origin_update()""")

		if index is not None:
			self._origin_currentIndex = index

		if self._origin_currentIndex == 0:
			self.ui.originLA.setText('Datos locales')
			self.ui.codeLA.setText(u" &Código LOCAL")
			# self.ui.nameLA.setText(u" &Nombre LOCAL de artículo")
			# self.ui.nameLA.setText(self._nameLabelText[self._origin_currentIndex])
		else:
			self.ui.originLA.setText(u'Datos de\n {}'.format(u'{} {} ...'.format(self.origin()['person']['name'], self.origin()['person']['name2'])[:20]))
			self.ui.codeLA.setText(u" Có&digo")
			# self.ui.nameLA.setText(u" &Nombre de artículo de {}".format(u"{} {} ...".format(self.origin()['person']['name'], self.origin()['person']['name2'])[:10]))
			# self.ui.nameLA.setText(self._nameLabelText[self._origin_currentIndex])

		try:
			self.ui.nameLA.setText(self._nameLabelText[self._origin_currentIndex])
		except:
			print ("""Error @ products.selector.Form.origin_update()""")
			print (self._origin_currentIndex)
			print (self._nameLabelText)

			f=g

		if len(self.ui.nameED.text()) < 2:
			self.ui.nameED.completer().model().clear()
		else:
			self.nameEdited(self.ui.nameED.text()[:2])

		self.emit(QtCore.SIGNAL('originChanged()'))


	def ownCodeVisibility_update(self):
		# print("        products.selector.Form.ownCodeVisibility_update()")
		if self.lcnt.ownCode_isVisible:
			self.ui.codeFR.show()
		else:
			self.ui.codeFR.hide()
		# print("        products.selector.Form.ownCodeVisibility_update() - END")


	@property
	def priceRule_current(self):
		## Index
		return self.__currentPriceRule


	def priceRulesChanged(self):
		pass
		#! Do whatever needs to be done


	def product_add(self):
		#!Not implemented
		data = "'rol_id':{}".format(self.origin()['id'])
		if self.ui.codeED.text():
			data += ", 'code':'{}'".format(self.ui.codeED.text())
		if self.ui.nameED.text():
			data += u", 'name':'{}'".format(self.ui.nameED.text())
		self.mst.eventRouter.emit(QtCore.SIGNAL("addProduct(QString)"), "{{{}}}".format(data))


	def UPCCaptured(self):
		if self.ui.UPCED.completer().completionCount() == 1:
			if self.ui.UPCED.completer().popup().currentIndex().row() == -1:
				modelx = self.ui.UPCED.completer().completionModel()
				index = modelx.index(0, 0)
				self.UPCSelected(index)


	def UPCEdited(self, text):
		self._data = None

		if len(text) < 2:
			self.ui.UPCED.completer().model().clear()

		elif len(text) == 2:
			filtros = {}
			filtros['code LIKE'] = "{}".format(text.toUpper())
			# filtros['rol_id'] = self.cnt.app.holder['id']
			filtros['rol_id'] = -1

			products = self.cnt.products(**filtros)

			self.ui.UPCED.completer().model().clear()

			if not products:
				self.ui.upcFR.setToolTip(u"El proveedor no tiene productos que lleven estas iniciales en el código de barras")
			else:
				self.ui.upcFR.setToolTip(u"")

				## Set Model Data
				for row, product in enumerate(products):
					aceptionForOrigin = [x for x in product['aceptions'] if x['rol_id'] == self.origin()['id']][0]
					self.ui.UPCED.completer().model().setData(row, "%s %s" % (aceptionForOrigin['code'], aceptionForOrigin['name']))
					self.ui.UPCED.completer().model().setData(row, aceptionForOrigin['id'], 1001)

				self.ui.UPCED.completer().model().reset()

		if self.ui.UPCED.text():
			self.ui.nameFR.setEnabled(False)
			self.ui.nameFR.setToolTip(u"Desactivado si se busca por codigo")
			self.ui.lineFR.setEnabled(False)
			self.ui.lineFR.setToolTip(u"Desactivado si se busca por codigo")
		else:
			self.ui.nameFR.setEnabled(True)
			self.ui.nameFR.setToolTip("")
			self.ui.lineFR.setEnabled(True)
			self.ui.lineFR.setToolTip(u"")


	def UPCSelected(self, completerModelIndex):
		# print("products.selector.Form.codeSelected()")

		completerRow = completerModelIndex.row()

		modelx = self.ui.UPCED.completer().completionModel()

		# acepcion = self.cnt.aception(id=modelx.data(modelx.index(completerRow, 0), 1001).toInt()[0])

		# ! checar el costo

		## Broadcast
		self._data = modelx.data(modelx.index(completerRow,0), self.ui.codeED.completer().model().DATAROLE_PRODUCT).toString()

		self.emit(QtCore.SIGNAL('productSelected()'))

		# self.ui.tablaPartidas.setDatosRenglon(rowIndex=-1, acepcion=acepcion, cantidad=Decimal('0.00'), precio=acepcion['costo'])

		self.ui.UPCED.setText("")
		self.ui.codeED.setText("")
		self.ui.nameED.setText("")
		self.ui.lineCB.setCurrentIndex(-1)

		self.ui.nameFR.setEnabled(True)
		self.ui.nameFR.setToolTip("")
		self.ui.lineFR.setEnabled(True)

		# self.ui.tablaPartidas.setCurrentCell(self.ui.tablaPartidas.rowCount()-1, self.COL_QUANTITY)
		# self.ui.tablaPartidas.cellWidget(self.ui.tablaPartidas.rowCount()-1, self.COL_QUANTITY).selectAll()

		# self.update()


	def UPCVisibility_update(self):
		# print "        products.selector.Form.UPCVisibility_update()"
		if self.lcnt.universalCode_isVisible:
			self.ui.upcFR.show()
		else:
			self.ui.upcFR.hide()


	def auxiliaryCodeVisibility_update(self):
		# print "        products.selector.Form.updateAuxiliaryCodeUsage()"
		if self.lcnt.auxiliaryCode_isVisible:
			self.ui.code2FR.show()
		else:
			self.ui.code2FR.hide()




class Model(QtCore.QAbstractListModel):

	DATAROLE_PRODUCT  = 1030

	def __init__(self, *args):
		QtCore.QAbstractListModel.__init__(self, *args)
		self.__data = []


	def clear(self):
		# self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount())
		self.__data = []
		self.reset()
		# self.endRemoveRows()


	def data(self, index, role=QtCore.Qt.DisplayRole):
		# print "products.selector.Model.data()"

		if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
			return self.__data[index.row()][0]

		elif role == QtCore.Qt.TextAlignmentRole:
			# if index.column() == self.COL_QUANTITY:
				# return int(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
			# if index.column() in [self.COL_PRICE, self.COL_AMOUNT]:
				# return int(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
			return int(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
		elif role == 1001:
			return self.__data[index.row()][1]
		elif role == 1002:
			return self.__data[index.row()][2]
		elif role == 1003:
			return self.__data[index.row()][3]
		elif role == 1004:
			return self.__data[index.row()][4]
		elif role == self.DATAROLE_PRODUCT:
			return self.__data[index.row()][5]
		else:
			return


	def insertRow(self, row, parent=QtCore.QModelIndex()):
		self.__data.insert(row, [u"", u""])
		return True


	def rowCount(self, parent=QtCore.QModelIndex()):
		return len(self.__data)


	def setData(self, row, value, role=QtCore.Qt.DisplayRole):
		""" No se usa la porquería de modelIndex """
		if row >= len(self.__data):
			self.__data.append([None, None, None, None, None, None])

		if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
			self.__data[row][0] = value

		elif role == 1001:
			self.__data[row][1] = value
		elif role == 1002:
			self.__data[row][2] = value
		elif role == 1003:
			self.__data[row][3] = value
		elif role == 1004:
			self.__data[row][4] = value
		elif role == self.DATAROLE_PRODUCT:
			self.__data[row][5] = value
		else:
			print ("puaj")
		return True



if __name__ == "__main__":
	print ("Test routine not implemented for products.selector")


"""

"""
