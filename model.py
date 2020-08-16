# -*- coding: utf-8 -*-

 ##############################################
 ##                                            ##
 ##               Products package              ##
 ##                  Data model                 ##
 ##                                             ##
 ##              from Basiq Series              ##
 ##           by Críptidos Digitales            ##
 ##                 GPL (c)2008                 ##
  ##                                            ##
	##############################################

"""
"""

from __future__ import print_function

import logging

import sys
import traceback
import datetime
from decimal import Decimal


class Model:

	def __init__(self, *args, **kwds):

		self.app = args[0]

		self.app.log2sys ( 'debug', "				Model.__init__()							@ products.model" )

		self.model = self.app.model

		self.plug()

		self.app.log2sys ( 'debug', "				Model.__init__() - end					@ products.model" )


	def plug(self):
		"""products.model.plug()"""

		self.model.getFullAception = self.getFullAception
		self.model.getFullAceptions = self.getFullAceptions
		self.model.getAceptionsSelect = self.getAceptionsSelect
		self.model.product_full_pull = self.product_full_pull
		self.model.setProduct = self.setProduct
		self.model.products_full_pull = self.products_full_pull
		self.model.getProductAttribute = self.getProductAttribute
		self.model.getProductsCount = self.getProductsCount
		self.model.getProductLines = self.getProductLines
		self.model.getDefaultPriceRule = self.getDefaultPriceRule
		self.model.getPriceRule = self.getPriceRule
		# self.model.getDefaultProductKind = self.getDefaultProductKind

		self.model.get_activePriceRules = self.__get_activePriceRules

		# self.model.getProductStatuss = self.getProductStatuss
		self.model.transaction_apply = self.transaction_apply
		"""
		exec("Model.getAception = getAception")
		exec("Model.setAception = setAception")
		exec("Model.getAceptions = getAceptions")
		exec("Model.getClassifications = getClassifications")
		exec("Model.canEditCurrentStock = canEditCurrentStock")
		exec("Model.getProduct = getProduct")
		exec("Model.setProductAttribute = setProductAttribute")
		exec("Model.getProductKinds = getProductKinds")
		exec("Model.setLine = setLine")
		exec("Model.canEditProductLine = canEditProductLine")
		exec("Model.setPrice = setPrice")
		exec("Model.canEditTax = canEditTax")
		exec("Model.getUnits = getUnits")
		exec("Model.getDefaultUnit = getDefaultUnit")
		exec("Model.mustCaptureClassification = mustCaptureClassification")
		exec("Model.validateProduct = validateProduct")
		"""

	def getAception(self, **filters):
		aception = self.model.getOne('aceptions', **filters)
		return aception


	def getFullAception(self, **filters):
		command = u"""SELECT ac.*,
		products.id AS product_id, products.unit_code, products.classification_id, products.kind_code,
		attributes.name AS classification,
		kinds.name AS kind_name,
		prices.ids AS prices_id, prices.values AS prices_value, prices.factors1 AS prices_factor1, prices.range_ids AS prices_kindid, prices.factors2 AS prices_factor2,
		lines.names AS lines_name, lines.ids AS lines_id, lines.codes AS lines_code

		FROM aceptions AS ac
		JOIN products ON (ac.product_id=products.id)
		LEFT JOIN attributes ON (products.classification_id=attributes.id)
		JOIN attributes AS kinds ON (products.kind_code=kinds.code)

		JOIN (SELECT product_id,
		array_agg(at1.id) AS ids,
		array_agg(at1.value) AS values,
		array_agg(at1.reference::integer) AS range_ids,
		array_agg(at1.factor1) AS factors1,
		array_agg(at1.factor2) as factors2
		FROM productattributes as at1
		WHERE name='price' AND rstatus='active'
		GROUP BY product_id
		) AS prices ON (products.id=prices.product_id)

		JOIN (SELECT product_id, array_agg(attributes.id) AS ids, array_agg(attributes.name) AS names, array_agg(attributes.code) AS codes
		FROM productattributes, attributes
		WHERE productattributes.reference::integer=attributes.id AND productattributes.name='line'
		GROUP BY product_id
		) AS lines ON (products.id=lines.product_id) """

		filtersText = u""

		if 'code' in filters.keys():
			filters['ac.code'] = filters.pop('code')

		for filter in filters.keys():
			if type(filters[filter]) in (str, datetime.datetime):
				filtersText += u"%s='%s' AND " % (filter, filters[filter])
			elif type(filters[filter]) in (list,):
				temp = ("%s" % filters[filter]).replace("[", "{").replace("]","}").replace("'", '"')
				filtersText += u"%s='%s' AND " % (filter, temp)
			elif filters[filter] == None:
				filtersText += u"%s is null AND " % filter
			else:
				try:
					if type(filters[filter]) in [unicode]:
						filtersText += u"%s='%s' AND " % (filter, filters[filter])
					else:
						filtersText += u"ac.%s=%s AND " % (filter, filters[filter])
				except:
					filtersText += u"ac.%s=%s AND " % (filter, filters[filter])

		command += u"WHERE ac.rstatus='active' AND %s " % filtersText.rstrip(u"AND ")

		# print "products.model.getFullAception()\n    ", command.encode('utf8')

		cursor = self.model.execute(command, giveCursor=True)
		aception = cursor.fetchone()
		cursor.close()

		# print "--+\n", aception

		if aception:
			aception['prices'] = []
			for index, id in enumerate(aception['prices_id']):
				price = {'id':id, 'value':Decimal(aception['prices_value'][index]), 'kind_code':aception['prices_kindid'][index]}
				price['factor1'] = aception['prices_factor1'][index]
				try: price['factor1'] = Decimal(price['factor1'])
				except: pass
				price['factor2'] = aception['prices_factor2'][index]
				try: price['factor2'] = Decimal(price['factor2'])
				except: pass
				aception['prices'].append(price)
			aception.pop('prices_id')
			aception.pop('prices_value')
			aception.pop('prices_factor1')
			aception.pop('prices_factor2')
			aception.pop('prices_kindid')

			aception['lines'] = [{'id':id, 'code':aception['lines_code'][index], 'name':aception['lines_name'][index]} for index, id in enumerate(aception['lines_id'])]
			aception.pop('lines_id')
			aception.pop('lines_name')
			aception.pop('lines_code')

		return aception


	def getAceptions(self, **filters):
		aceptions = self.model.getAll('aceptions', **filters)
		return aceptions


	def getFullAceptions(self, **filters):
		#~ command ="""SELECT ac.id, ac.rol_id, ac.code, ac.name, ac.individualdiscount, ac.generaldiscount, ac.quota,
		#~ products.id AS product_id, products.kind_code, products.unit_code,
		#~ attributes.name AS classification, prices.*, y.lines, stock.*, cost.*

	#~ FROM aceptions AS ac JOIN products ON (ac.product_id=products.id), attributes,

		#~ (SELECT product_id, array_agg(at1.id) AS prices_id, array_agg(at1.value) AS prices_value, array_agg(at1.factor1) AS prices_factor1, array_agg(at1.factor2) AS prices_factor2, array_agg(at1.id) AS prices_id
		#~ FROM productattributes as at1
		#~ WHERE name='precio' AND rstatus='active'
		#~ GROUP BY product_id
		#~ ) AS prices,

		#~ (SELECT product_id, array_agg(attributes.name) AS lines
		#~ FROM productattributes, attributes
		#~ WHERE productattributes.id=attributes.id AND productattributes.name='línea'
		#~ GROUP BY product_id
		#~ ) AS y,

		#~ (SELECT product_id, productattributes.*
		#~ FROM productattributes
		#~ WHERE productattributes.name = 'stock' AND rstatus='active'
		#~ ) AS stock,

		#~ (SELECT product_id, productattributes.*
		#~ FROM productattributes
		#~ WHERE productattributes.name = 'cost' AND rstatus='active'
		#~ ) AS cost
		#~ """

		command = u"""
		SELECT
			ac.*,
			products.id AS product_id, products.kind_code, products.unit_code,
			attributes.name AS classification, prices.*, lines.*, stock.*, cost.*

		FROM
			aceptions AS ac

			JOIN products ON (ac.product_id=products.id)

			LEFT JOIN attributes ON (products.classification_id=attributes.id)

			JOIN (SELECT product_id,
			array_agg(at1.id) AS prices_id,
			array_agg(at1.value) AS prices_value,
			array_agg(at1.factor1) AS prices_factor1,
			array_agg(at1.factor2) AS prices_factor2,
			array_agg(at1.reference::integer) AS pricekind_code
			FROM productattributes as at1
			WHERE name='price' AND rstatus='active'
			GROUP BY product_id
			) AS prices ON (products.id=prices.product_id)

			JOIN (SELECT product_id,
			array_agg(attributes.id) AS lines_id,
			array_agg(attributes.name) AS lines_name
			FROM productattributes, attributes
			WHERE productattributes.reference::integer=attributes.id AND productattributes.name='line'
			GROUP BY product_id
			) AS lines ON (products.id=lines.product_id)

			JOIN (SELECT product_id,
			array_agg(at2.value) AS stock_value,
			array_agg(at2.factor1) AS stock_factor1,
			array_agg(at2.factor2) AS stock_factor2
			FROM productattributes as at2
			WHERE name = 'stock' AND rstatus='active'
			GROUP BY product_id
			) AS stock ON (products.id=stock.product_id)

			JOIN (SELECT product_id, value AS cost_value, factor1 AS cost_factor1, factor2 AS cost_factor2
			FROM productattributes
			WHERE name = 'cost' AND rstatus='active'
			) AS cost ON (products.id=cost.product_id)
		"""

		filtersText = """products.classification_id = attributes.id AND ac.product_id = prices.product_id AND ac.product_id = y.product_id AND ac.rstatus='active' AND """

		filtersText = """ac.rstatus='active' AND """

		for filter in filters.keys():
			if type(filters[filter]) in (str, datetime.datetime):
				filtersText += "%s='%s' AND " % (filter, filters[filter])
			elif type(filters[filter]) in (list,):
				temp = ("%s" % filters[filter]).replace("[", "{").replace("]","}").replace("'", '"')
				filtersText += "%s='%s' AND " % (filter, temp)
			elif filters[filter] == None:
				filtersText += "%s is null AND " % filter
			elif ' IN' in filter.upper():
				filtersText += "%s IN %s AND " % (filter.rstrip('IN'), filters[filter])
			else:
				try:
					if type(filters[filter]) in [unicode]:
						filtersText += "%s='%s' AND " % (filter, filters[filter])
					else:
						filtersText += "ac.%s=%s AND " % (filter, filters[filter])
				except:
					filtersText += "ac.%s=%s AND " % (filter, filters[filter])

		command += "WHERE %s " % filtersText.rstrip("AND ")

		# print command

		cursor = self.model.execute(command, giveCursor=True)
		aceptions = cursor.fetchall()
		cursor.close()

		for aception in aceptions:

			product = {}

			product['cost'] = aception.pop('cost_value')
			product['tax'] = aception.pop('cost_factor1')
			product['margin'] = aception.pop('cost_factor2')

			product['minimum'] = Decimal(aception.pop('stock_factor1')[0])
			product['maximum'] = Decimal(aception.pop('stock_factor2')[0])
			product['actual'] = Decimal(aception.pop('stock_value')[0])

			product['kind'] = {'code':aception.pop('kind_code')}
			product['classification'] = aception.pop('classification')
			product['unit_code'] = aception.pop('unit_code')



			product['prices'] = []
			for index, id in enumerate(aception['prices_id']):
				price = {'id':id, 'value':Decimal(aception['prices_value'][index]), 'kind_code':aception['priceKind_code'][index]}
				price['factor1'] = aception['prices_factor1'][index]
				try: Decimal(price['factor1'])
				except: pass
				price['factor2'] = aception['prices_factor2'][index]
				try: Decimal(price['factor2'])
				except: pass
				product['prices'].append(price)
			aception.pop('prices_id')
			aception.pop('prices_value')
			aception.pop('prices_factor1')
			aception.pop('prices_factor2')
			aception.pop('priceKind_code')
			# aception.pop('prices_tipoid')

			product['lines'] = [{'id':id, 'name':aception['lines_name'][index]} for index, id in enumerate(aception['lines_id'])]

			aception.pop('lines_id')
			aception.pop('lines_name')

			aception['product'] = product


		return aceptions


	def setAception(self, **data):
		# print("\n    products.model.setAception()")
		# print("    {}".format(data))

		try:
			currentDateTime = datetime.datetime.today()

			dataNew = None

			data['rstatus'] = u'active'
			data['rspanstart'] = currentDateTime

			if 'id' in data.keys():
				dataNew = data
				data = self.model.getOne('aceptions', id=data['id'])
			elif 'product_id' in data.keys() and 'rol_id' in data.keys():
				dataExistent = self.getAception(product_id=data['product_id'], rol_id=data['rol_id'], rstatus=u'active')
				if dataExistent:
					dataNew = data
					data = dataExistent

			if dataNew:
				id = data.pop('id')
				data['rstatus'] = u'obsolete'
				data['rspanend'] = currentDateTime
				dataNew['rspanstart'] = data['rspanend']

				command = """UPDATE aceptions SET """

				valuesText = ""
				for value in dataNew.keys():
					if type(dataNew[value]) in [str, datetime.datetime]:
						valuesText += "%s = '%s', " % (value, dataNew[value])
					else:
						try:
							if type(dataNew[value]) in [unicode]:
								valuesText += "%s = '%s', " % (value, dataNew[value])
							else:
								valuesText += "%s = %s, " % (value, dataNew[value])
						except:
							valuesText += "%s = %s, " % (value, dataNew[value])

				command += "%s WHERE id=%s" % (valuesText.rstrip(', '), id)

				# print "\n    products.model.setAception()\n        ", command.encode('utf8')

				self.model.execute(command)

			command = """INSERT INTO aceptions """
			fieldsText = ""
			valuesText = ""
			for key in data.keys():
				if type(data[key]) in [str, datetime.datetime]:
					fieldsText += "%s, " % key
					valuesText += "'%s', " % data[key]
				elif data[key] == None:
					fieldsText += "%s, " % key
					valuesText += "Null, "
				else:
					try:
						if type(data[key]) in [unicode]:
							fieldsText += "%s, " % key
							valuesText += "'%s', " % data[key]
						else:
							fieldsText += "%s, " % key
							valuesText += "%s, " % data[key]
					except:
						fieldsText += "%s, " % key
						valuesText += "%s, " % data[key]
			command = "%s (%s) VALUES (%s)" % (command, fieldsText.rstrip(", "), valuesText.rstrip(", "))

			# print "\n    products.model.setAception()\n        ", command.encode('utf8')

			self.model.execute(command)

		except:
			print ("\nproducts.model.setAception() - Exception\n    %s" % sys.exc_info()[1])
			print ("    %s" % command.encode('utf8'))


	def getAceptionsSelect(self, **filters):
		# print "\nproducts.model.getAceptionsSelect()"

		# try:
		if True:
			command = u"""SELECT ac.id, ac.product_id, ac.rol_id, ac.code, ac.name, ac.cost, ac.individualdiscount, ac.generaldiscount,
			stock.value AS product_current, stock.factor2 AS product_maximum, cost.value AS product_cost, products.status AS product_status,
			attributes.name AS classification_name,
			pcs.prices_id, pcs.prices_value, pcs.prices_factor1, pcs.prices_reference,
			lns.lines_name
			FROM aceptions AS ac
				JOIN products ON (products.id=ac.product_id)
				JOIN attributes ON (attributes.id=products.classification_id)
				JOIN productattributes AS stock ON (stock.product_id=ac.product_id AND stock.name='stock' AND stock.rstatus='active')
				JOIN productattributes AS cost ON (cost.product_id=ac.product_id AND cost.name='cost' AND cost.rstatus='active')
				JOIN (SELECT product_id, array_agg(attributes.name) AS lines_name
					FROM productattributes JOIN attributes ON (productattributes.reference::integer=attributes.id)
					WHERE [1] productattributes.rstatus='active' AND productattributes.name='line'
					GROUP BY product_id
				) AS lns ON (ac.product_id=lns.product_id)
				LEFT JOIN (SELECT product_id, array_agg(at1.id) AS prices_id, array_agg(at1.value) AS prices_value,
				array_agg(at1.factor1) AS prices_factor1, array_agg(at1.reference) AS prices_reference
					FROM productattributes as at1
					WHERE name='price' AND rstatus='active'
					GROUP BY product_id
				) AS pcs ON (ac.product_id=pcs.product_id)
			"""


			command_select = u"""SELECT ac.id, ac.product_id, ac.rol_id, ac.code,
			ac.name,
			ac.cost, ac.individualdiscount,
			ac.generaldiscount
			, cost.value AS product_cost, products.status AS product_status
			, attributes.name AS classification_name
			, pcs.prices_id, pcs.prices_value, pcs.prices_factor1, pcs.prices_reference
			, lns.lines_name
			"""

			command_ = u"""
			FROM aceptions AS ac
			JOIN products ON (products.id=ac.product_id)
			JOIN attributes ON (attributes.id=products.classification_id)
			JOIN productattributes AS cost ON (cost.product_id=ac.product_id AND cost.name='cost' AND cost.rstatus='active')

			LEFT JOIN (SELECT product_id, array_agg(at1.id) AS prices_id, array_agg(at1.value) AS prices_value,
			array_agg(at1.factor1) AS prices_factor1, array_agg(at1.reference) AS prices_reference
				FROM productattributes as at1
				WHERE name='price' AND rstatus='active'
				GROUP BY product_id
			) AS pcs ON (ac.product_id=pcs.product_id)

			JOIN (SELECT product_id, array_agg(attributes.name) AS lines_name
				FROM productattributes JOIN attributes ON (productattributes.reference::integer=attributes.id)
				WHERE productattributes.rstatus='active' AND productattributes.name='line'
				GROUP BY product_id
			) AS lns ON (ac.product_id=lns.product_id)

			"""

			cursor = self.model.execute("SELECT * FROM information_schema.tables WHERE table_name='{}'".format('documentitems'), giveCursor=True)

			no_stock = not cursor.fetchone()

			cursor.close()

			if not no_stock:

				command_select += """
				, stock.factor2 AS product_maximum
				, stocks.value AS product_current"""

				command_ += """
				JOIN productattributes AS stock ON (stock.product_id=ac.product_id AND stock.name='stock' AND stock.rstatus='active')

				LEFT JOIN (SELECT subject_id AS product_id, stock AS value
				FROM (SELECT subject_id, stock, quantity, documents.date, attributes.reference::integer
						, row_number() over ( partition by subject_id order by documents.date desc) AS rn
						FROM documentitems
						JOIN documents ON documents.id = documentitems.document_id
						JOIN attributes ON attributes.code = documents.kind_code
						WHERE attributes.reference in ('1', '-1')
					) AS stock
					WHERE rn=1
				) AS stocks ON ac.product_id = stocks.product_id

				"""

			command = command_select + command_

			filtersText = """ac.rstatus='active' AND """
			filtersText1 = ""

			#~ orderText = """ac.id, products.id """
			orderText = ''
			if 'order' in filters.keys():
				text = ''
				for filter in filters.pop('order').split(', '):
					text += "ac.%s, " % filter
				orderText += "ORDER BY %s" % text.rstrip(', ')

			for filter in filters.keys():
				if filter == 'line':
					filtersText1 += "attributes.id={} AND ".format(filters[filter])
				elif ' LIKE' in filter.upper():
					filtersText += "UPPER(ac.%s) LIKE '%s%%' AND " % (filter.upper().rstrip('LIKE'), filters[filter].upper())
				elif type(filters[filter]) in (str, datetime.datetime):
					filtersText += "ac.%s='%s' AND " % (filter, filters[filter])
				elif type(filters[filter]) in (list,):
					filtersText += "{} IN {} AND ".format(filter, filters[filter]).replace("[", "(").replace("]",")").replace("'", '"')
				elif filters[filter] == None:
					filtersText += "%s is null AND " % filter
				else:
					try:
						if type(fiters[filter]) in [unicode]:
							filtersText += "ac.%s='%s' AND " % (filter, filters[filter])
						else:
							filtersText += "%s=%s AND " % (filter, filters[filter])
					except:
						filtersText += "%s=%s AND " % (filter, filters[filter])

			command = command.replace("WHERE [1]", "WHERE {}".format(filtersText1))
			command += "WHERE %s " % filtersText.rstrip("AND ")
			command += "%s " % orderText

			# print("""\n    products.model.getAceptionsSelect()""")
			# print(command.encode('utf8'))

			cursor = self.model.execute(command, giveCursor=True)
			aceptions = cursor.fetchall()
			cursor.close()

			for aception in aceptions:

				#! Remove this command when product current is working ok
				if 'product_current' in aception:
					if aception['product_current'] is None:
						aception['product_current'] = '0'

				if not aception['product_cost']:
					aception['product_cost'] = u'0'

				try:

					aception['product'] = {'cost':Decimal(aception.pop('product_cost')), 'status':aception.pop('product_status')}

					if 'product_current' in aception:
						aception['current'] = Decimal(aception.pop('product_current'))
					if 'product_maximum' in aception:
						aception['maximum'] = Decimal(aception.pop('product_maximum'))

					aception['prices'] = [{'id':id, 'value':Decimal(aception['prices_value'][index]), 'factor1':aception['prices_factor1'][index], 'reference':aception['prices_reference'][index]} for index, id in enumerate(aception['prices_id'])]
					aception.pop('prices_id')
					aception.pop('prices_value')
					aception.pop('prices_factor1')
					aception.pop('prices_reference')

					if aception['lines_name']:
						aception['lines'] = [{'name':aception['lines_name'][index]} for index, name in enumerate(aception['lines_name'])]
					else:
						aception['lines'] = []
					aception.pop('lines_name')

					aception['classification'] = {'name':aception['classification_name']}
					aception.pop('classification_name')
				except:
					print ("\nException @ poducts.model.getAceptionsSelect()\n    {}".format(sys.exc_info()[1]))
					print ("    {}".format(command.encode('utf8')))
					print ("    {}".format(aception))

			return aceptions

		# except:
			# print("\nException @ poducts.model.getAceptionsSelect()\n    %s" % sys.exc_info()[1])
			# print("    %s" % command.encode('utf8'))


	def getClassifications(self):
		classifications = self.model.getAttributes(category=u'productClassification', order=u'name')
		return classifications


	def setLine(self, **data):
		# print("\n    products.model.setLine()")
		# print("    {}".format(data))

		try:
			attribute = {}

			if 'id' in data.keys():
				## Se usa una linea existente
				attribute['reference'] = data.pop('id')

			elif 'name' in data.keys():
				## Se usa una linea nueva, se crea a partir del nombre
				attribute['reference'] = self.model.setAttribute(category='productLine', name=data['name'])['id']

			if 'attributeId' in data.keys():
				## El atributo existe
				attribute['id'] = data['attributeId']
				## Se eliminan campos innecesarios por prevencion
			else:
				## El atributo es nuevo
				attribute['name'] = u'line'
				attribute['product_id'] = data['product_id']

			self.setProductAttribute(**attribute)

		except:
			print ("\nException @ products.model.setLine()\n    %s" % sys.exc_info()[1])
			print ("    %s" % command.encode('utf8'))


	# def getLines(self):
		# lines = self.model.getAttributes(category=u'productLine', order=u'name')
		# return lines


	def prices(**filters):
		command = """SELECT atributosproducto.* FROM atributosproducto JOIN atributos ON (atributosproducto.atributo_id=atributos.id) """
		filtersText = """atributosproducto.nombre='precio' AND """

		for filter in filters.keys():
			if type(filters[filter]) in [str]:
				filtersText += "%s='%s' AND " % (filter, filters[filter])
			elif type(filters[filter]) in (list,):
				temp = ("%s" % filters[filter]).replace("[", "{").replace("]","}").replace("'", '"')
				filtersText += "%s='%s' AND " % (filter, temp)
			elif filters[filter] == None:
				filtersText += "%s is null AND " % filter
			else:
				try:
					if type(filters[filter]) in [unicode]:
						filtersText += "%s='%s' AND " % (filter, filters[filter])
					else:
						filtersText += "%s=%s AND " % (filter, filters[filter])
				except:
					filtersText += "%s=%s AND " % (filter, filters[filter])

		if filtersText:
			command += "WHERE %s " % filtersText.rstrip("AND ")

		query(command)
		prices = fetchall()

		return prices


	def setPrice(self, **data):
		# print "\nproducts.model.setPrice()"

		data['name'] = u'price'

		self.setProductAttribute(**data)

		'''
		try:
			currentDateTime = datetime.datetime.today()
			data['name'] = u'price'
			data['rstatus'] = u'active'
			data['rspanstart'] = currentDateTime
			if 'id' in data.keys():
				dataNew = data
				data = self.model.getOne('productattributes', id=dataNew['id'])
				data.pop('id')
				data['rstatus'] = 'obsolete'
				data['rspanend'] = currentDateTime

				dataNew['name'] = u'price'
				dataNew['rstatus'] = u'active'
				dataNew['rspanstart'] = data['rspanend']

				command = """UPDATE productattributes SET """
				valuesText = ""
				for value in dataNew.keys():
					if type(dataNew[value]) in [str, unicode, datetime.datetime]:
						valuesText += "%s = '%s', " % (value, dataNew[value])
					else:
						valuesText += "%s = %s, " % (value, dataNew[value])
				command += "%s WHERE id=%s" % (valuesText.rstrip(', '), id)

				# print command.encode('utf8')

				self.model.execute(command)

			command = """INSERT INTO productattributes """
			fieldsText = ""
			valuesText = ""
			for key in data.keys():
				if type(data[key]) in [str, unicode, datetime.datetime]:
					fieldsText += "%s, " % key
					valuesText += "'%s', " % data[key]
				elif data[key] == None:
					fieldsText += "%s, " % key
					valuesText += "Null, "
				else:
					fieldsText += "%s, " % key
					valuesText += "%s, " % data[key]
			command = "%s (%s) VALUES (%s)" % (command, fieldsText.rstrip(", "), valuesText.rstrip(", "))

			# print command.encode('utf8')

			self.model.execute(command)

		except:
			print ("\nException @ products.model.setPrice()\n    %s" % sys.exc_info()[1])
			print ("    %s" % command.encode('utf8'))
		'''


	def __get_activePriceRules ( self ) :

		self.app.log2sys ( 'debug', "				Model.__get_activePriceRules()			@ products.model" )

		data = self.model.getAttributes ( category='priceRule', order='reference' )
		active = []
		for rule in data:
			if rule['reference'][1] == 'a':
				active.append ( rule )

		self.app.log2sys ( 'debug', "				Model.__get_activePriceRules() - end		@ products.model" )

		return active


	def getDefaultPriceRule(self):
		data = self.model.getAttribute(category='priceRule', value='default')
		return data


	def getPriceRule(self, **kwds):
		# print "products.model.Model.getPriceRule()", kwds
		kwds['category'] = 'priceRule'
		return self.model.getAttribute(**kwds)


	def getProduct(self, **filters):
		product = self.model.getOne('products', **filters)
		return product


	def product_full_cursor(self, *args, **filters):
		# print("""    products.model.product_full_cursor()""")

		# print(args)
		# print(filters)

		messages = ""

		if args:
			connIndex = args[0]     #! pop(x, default) didn't work
		else:
			connIndex = 0

		try:
			command = """
			SELECT * FROM
				(SELECT DISTINCT products.*{1}
				FROM products
				JOIN aceptions ON ( products.id = aceptions.product_id )
				{2}
			) AS products

			JOIN (SELECT
				code AS status_code,
				name AS status_name
				FROM attributes
			) AS st ON products.status=st.status_code

			JOIN (SELECT prods1.id AS id,
				array_agg(acps.id) AS acps_id,
				array_agg(acps.product_id) AS acps_product_id,
				array_agg(acps.rol_id) AS acps_rol_id,
				array_agg(acps.code) AS acps_code,
				array_agg(acps.name) AS acps_name,
				array_agg(acps.cost) AS acps_cost,
				array_agg(acps.individualdiscount) AS acps_individualdiscount,
				array_agg(acps.generaldiscount) AS acps_generaldiscount,
				array_agg(acps.quota) AS acps_quota,
				array_agg(persons.name) AS rols_person_name,
				array_agg(persons.name2) AS rols_person_name2,
				array_agg(persons.rfc) AS rols_person_rfc
				FROM products AS prods1
					JOIN aceptions AS acps ON (prods1.id=acps.product_id AND acps.rstatus='active')
					JOIN rols ON (acps.rol_id=rols.id)
					JOIN persons ON (rols.person_id=persons.id)
				{3}
				GROUP BY prods1.id
			) AS aceptions ON (products.id=aceptions.id)

			JOIN (SELECT
				code AS unit_code,
				name AS unit_name,
				reference AS unit_shortname
				FROM attributes
			) AS units ON products.unit_code=units.unit_code

			JOIN (SELECT product_id AS id,
				array_agg(productattributes.id) AS lines_id,
				array_agg(productattributes.product_id) AS lines_product_id,
				array_agg(attributes.id) AS lines_reference_id,
				array_agg(attributes.name) AS lines_name,
				array_agg(attributes.code) AS lines_code

				FROM productattributes
					JOIN attributes ON (productattributes.reference::integer=attributes.id AND productattributes.name='line' AND productattributes.rstatus='active')
					GROUP BY product_id
			) AS lines ON (products.id=lines.id)

			JOIN (SELECT prods2.id AS id,
				array_agg(atts.id) AS atts_id,
				array_agg(atts.name) AS atts_name,
				array_agg(atts.value) AS atts_value,
				array_agg(atts.factor1) AS atts_factor1,
				array_agg(atts.factor2) AS atts_factor2,
				array_agg(atts.reference) AS atts_reference

				FROM products AS prods2
					JOIN productattributes AS atts ON (prods2.id=atts.product_id AND atts.name!='line' AND atts.name!='price' AND atts.rstatus='active')
					GROUP BY prods2.id
			) AS attributes ON (products.id=attributes.id)
			"""

			cursor = self.model.execute("SELECT * FROM information_schema.tables WHERE table_name='{}'".format('documentitems'), giveCursor=True)

			no_stock = not cursor.fetchone()

			cursor.close()

			if not no_stock:

				command += """
			LEFT JOIN (SELECT subject_id AS product_id, COALESCE(stock, 0.00) AS current
				FROM (SELECT subject_id, stock, quantity, documents.date, attributes.value::integer
					, row_number() over ( partition by subject_id order by documents.date desc) AS rn
					FROM documentitems
					JOIN documents ON documents.id = documentitems.document_id
					JOIN attributes ON attributes.code = documents.kind_code
					WHERE attributes.value in ('1', '-1')
				) AS stock
				WHERE rn=1
			) AS stocks ON products.id=stocks.product_id

			JOIN (SELECT product_id AS id,
				array_agg(productattributes.id) AS prices_id,
				array_agg(productattributes.product_id) AS prices_product_id,
				array_agg(productattributes.value) AS prices_value,
				array_agg(productattributes.factor1) AS prices_factor1,
				array_agg(productattributes.factor2) AS prices_factor2,
				array_agg(attributes.id) AS prices_reference_id,
				array_agg(attributes.name) AS prices_name,
				array_agg(attributes.code) AS prices_code

				FROM productattributes
					JOIN attributes ON (productattributes.reference::integer=attributes.code AND productattributes.name='price' AND productattributes.rstatus='active')
					GROUP BY product_id
			) AS prices ON (products.id=prices.id)


			"""

			orderText = ''
			if 'order' in filters.keys():
				order = filters.pop('order')
				text = ''
				for filter in order.split(', '):
					if filter in ['name']:
						text += "{}, ".format(filter)
					else:
						text += "acps_%s, " % filter
				orderText += "%s" % text.rstrip(', ')

			text1 = ""
			filtersText_ = ""
			filtersText = ""
			for filter in filters.keys():

				# print(filter)

				if ('code' in filter and '_code' not in filter) or 'name' in filter or 'rol_id' in filter:
				# if 'name' in filter or 'rol_id' in filter:

					if ' LIKE' in filter.upper():

						unaccented = filters[filter].lower().replace(u'á','a').replace(u'é','e').replace(u'í','i').replace(u'ó','o').replace(u'ú','u')

						#text = "to_ascii(convert_to(aceptions.{}, 'latin1'), 'latin1')".format(filter.lower().rstrip('like'))
						text = "aceptions.{}".format(filter.lower().rstrip('like'))

						filtersText += "LOWER({}) LIKE '{}%%' AND ".format(text, unaccented.lower())

						if orderText:
							text1 += ', {} AS {}'.format(text, filter.lower().rstrip('like'))

					elif type(filters[filter]) in [int]:
						filtersText += "aceptions.%s=%s AND " % (filter, filters[filter])
					else:
						filtersText += "aceptions.%s='%s' AND " % (filter, filters[filter])


				elif 'persons' in filter:
					filtersText_ += "%s='%s' AND " % (filter, filters[filter])
				elif type(filters[filter]) in (str, datetime.datetime):
					filtersText += "%s='%s' AND " % (filter, filters[filter])

				elif type(filters[filter]) in (list,):
					# temp = ("%s" % filters[filter]).replace("[", "{").replace("]","}").replace("'", '"')
					filtersText += "{} IN {} AND ".format(filter, filters[filter]).replace("[", "(").replace("]",")").replace("'", '"')

					# filtersText += "%s='%s' AND " % (filter, temp)

				elif filters[filter] == None:
					filtersText += "%s is null AND " % filter

				else:
					try:
						if type(filters[filter]) in [unicode]:
							filtersText += "%s='%s' AND " % (filter, filters[filter])
						else:
							filtersText += "products.{}={} AND ".format(filter, filters[filter])
					except:
						filtersText += "products.{}={} AND ".format(filter, filters[filter])

				# print(filtersText)

		#        else:
		#            filtersText += "acps.%s=%s AND " % (filter, filters[filter])

			# print(33001, text1)
			# print(33002, filtersText)
			# print(33003, filtersText_)

			command = command.replace("{1}", text1)

			if filtersText:
				filtersText = "WHERE aceptions.rstatus='active' AND {}".format(filtersText.rstrip("AND "))
			command = command.replace("{2}", filtersText)

			if filtersText_:
				filtersText_ = "WHERE {}".format(filtersText_.rstrip("AND "))
			command = command.replace("{3}", filtersText_)

			if orderText:
				command += "ORDER BY {}".format(orderText)

		except:

			## Error in command or database access
			messages += u"Error en creación de comando"

		# print(command)

		cursor = self.model.execute(command, connIndex, giveCursor=True)

		# print("""    products.model.product_full_cursor() - END""")
		return cursor


	def product_full_pull(self, **filters):
		# print("""    products.model.product_full_pull()""")

		messages = ''

		product = None

		cursor = self.product_full_cursor(**filters)

		product = cursor.fetchone()

		# print(8800, product)

		cursor.close()

		if product:

			try:

				product['status'] = {'code':product.pop('status_code'), 'name':product.pop('status_name')}

				aceptions = [{'id':id, 'product_id':product['acps_product_id'][index], 'rol_id':product['acps_rol_id'][index], 'rol':{'id':product['acps_rol_id'][index], 'person':{'name':product['rols_person_name'][index], 'name2':product['rols_person_name2'][index], 'rfc':product['rols_person_rfc'][index]}}, 'code':product['acps_code'][index], 'name':product['acps_name'][index], 'cost':product['acps_cost'][index], 'individualdiscount':product['acps_individualdiscount'][index], 'generaldiscount':product['acps_generaldiscount'][index], 'quota':product['acps_quota'][index]} for index, id in enumerate(product['acps_id'])]
				product.pop('acps_id')
				product.pop('acps_product_id')
				product.pop('acps_rol_id')
				product.pop('acps_code')
				product.pop('acps_name')
				product.pop('acps_cost')
				product.pop('acps_individualdiscount')
				product.pop('acps_generaldiscount')
				product.pop('acps_quota')
				product.pop('rols_person_name')
				product.pop('rols_person_name2')
				product.pop('rols_person_rfc')
				product['aceptions'] = aceptions

				product['kind'] = {'code':product.pop('kind_code')}

				if product['lines_id']:
					lines = [{'id':id, 'product_id':product['lines_product_id'][index], 'reference':product['lines_reference_id'][index], 'name':product['lines_name'][index], 'code':product['lines_code'][index]} for index, id in enumerate(product['lines_id'])]
				else:
					lines = []
				product.pop('lines_id')
				product.pop('lines_product_id')
				product.pop('lines_reference_id')
				product.pop('lines_name')
				product.pop('lines_code')
				product['lines'] = lines

				if 'prices_id' in product:
					product['prices'] = [ {'id':id, 'product_id':product['prices_product_id'][index], 'value':product['prices_value'][index], 'reference':product['prices_reference_id'][index], 'name':product['prices_name'][index], 'code':product['prices_code'][index], 'factor1':product['prices_factor1'][index], 'factor2':product['prices_factor2'][index] } for index, id in enumerate(product['prices_id'])]
					product.pop('prices_id')
					product.pop('prices_product_id')
					product.pop('prices_value')
					product.pop('prices_factor1')
					product.pop('prices_factor2')
					product.pop('prices_reference_id')
					product.pop('prices_name')
					product.pop('prices_code')

				# print(8801, product)


				attributes = [{'id':id, 'name':product['atts_name'][index], 'value':product['atts_value'][index], 'factor1':product['atts_factor1'][index], 'factor2':product['atts_factor2'][index], 'reference':product['atts_reference'][index]} for index, id in enumerate(product['atts_id']) if id != None]
				product.pop('atts_id')
				product.pop('atts_name')
				product.pop('atts_value')
				product.pop('atts_factor1')
				product.pop('atts_factor2')
				product.pop('atts_reference')

				# print 1232, attributes

				# reversed = attributes[:]
				# reversed.reverse()
				# product['lines'] = [attributes.pop(len(reversed)-index-1) for index, attribute in enumerate(reversed) if attribute['name']==u'line']

				# print attributes

				'''
				reversed = attributes[:]
				reversed.reverse()
				product['prices'] = [attributes.pop(len(reversed)-index-1) for index, attribute in enumerate(reversed) if attribute['name']==u'price']
				'''

				# print(attributes)

				reversed = attributes[:]
				reversed.reverse()

				try:
					cost = [attributes.pop(len(reversed)-index-1) for index, attribute in enumerate(reversed) if attribute['name']==u'cost'][0]

					product['cost_id'] = Decimal(cost['id'])
					product['meancost'] = Decimal(cost['value'])
					product['margin'] = Decimal(cost['factor2'])
				except:
					messages += u"Error in cost attributes"

				# print(attributes)
				# print(reversed)

				reversed = attributes[:]
				reversed.reverse()
				# taxes = [attributes.pop(len(reversed)-index-1) for index, attribute in enumerate(reversed) if attribute['name']==u'tax']

				try:
					taxes = [{'code':int(attribute['reference']), 'value':Decimal(attribute['value'])} for index, attribute in enumerate(reversed) if attribute['name']==u'tax']
					# print(888, taxes)
					# print(889, cost)
					tax = {'code':51, 'factor':Decimal(cost['factor1']), 'reference':cost['reference']}
					taxes.append(tax)
					product['taxes'] = taxes
				except:
					messages += u"Error in taxes attributes\n    cost: {}\n    taxes: {}".format(cost, taxes)

				reversed = attributes[:]
				reversed.reverse()
				stock = [attributes.pop(len(reversed)-index-1) for index, attribute in enumerate(reversed) if attribute['name']==u'stock'][0]

				# print(stock)

				if stock:
					product['stock_id'] = stock['id']
					if product['current'] is None:
						product['current'] = Decimal('0')
					product['minimum'] = Decimal(stock['factor1'])
					product['maximum'] = Decimal(stock['factor2'])

				product['attributes'] = attributes

				product = dict(product)

			except:
				## Errors in product record other than cost attributes
				print ("\nException @ products.model.product_full_pull()\n    {}".format(sys.exc_info()[1]))
				messages += "{}".format(sys.exc_info()[1])
		else:
			## No product
			pass

		if messages:
			print ("Errores en products.model.product_full_pull()\n    {}".format(messages))
			print (product)

		# print("""    products.model.product_full_pull() - END""")

		return product


	def products_full_pull(self, *args, **filters):

		# print("""    products.model.products_full_pull()""")

		cursor = self.product_full_cursor(*args, **filters)

		items = cursor.fetchall()

		cursor.close()

		# print(88888, len(items))

		products = []

		taxKinds = self.model.getAttributes(category='tax')
		taxKind_general = self.model.attribute_get(**{'category':'tax', 'referenceLIKE':'general, default'})

		for index, item in enumerate(items):

			# print(5500, index, item)

			product = {}

			aceptions = [{'id':id, 'product_id':item['acps_product_id'][index], 'rol_id':item['acps_rol_id'][index], 'rol':{'id':item['acps_rol_id'][index], 'person':{'name':item['rols_person_name'][index], 'name2':item['rols_person_name2'][index], 'rfc':item['rols_person_rfc'][index]}}, 'code':item['acps_code'][index], 'name':item['acps_name'][index], 'cost':item['acps_cost'][index], 'individualdiscount':item['acps_individualdiscount'][index], 'generaldiscount':item['acps_generaldiscount'][index], 'quota':item['acps_quota'][index]} for index, id in enumerate(item['acps_id'])]
			item.pop('acps_id')
			item.pop('acps_product_id')
			item.pop('acps_rol_id')
			item.pop('acps_code')
			item.pop('acps_name')
			item.pop('acps_cost')
			item.pop('acps_individualdiscount')
			item.pop('acps_generaldiscount')
			item.pop('acps_quota')
			item.pop('rols_person_name')
			item.pop('rols_person_name2')
			item.pop('rols_person_rfc')
			product['aceptions'] = aceptions

			## 04'14 La idea es eliminar referencias específicas a atributos
			## (como la línea especificada aqui abajo) y generalizarlas.

			lines = [{'id':id, 'product_id':item['lines_product_id'][index], 'reference':item['lines_reference_id'][index], 'name':item['lines_name'][index], 'code':item['lines_code'][index]} for index, id in enumerate(item['lines_id'])]
			item.pop('lines_id')
			item.pop('lines_product_id')
			item.pop('lines_reference_id')
			item.pop('lines_name')
			item.pop('lines_code')
			product['lines'] = lines

			if 'prices_id' in item:
				product['prices'] = [ { 'id':id, 'product_id':item['prices_product_id'][index], 'value':item['prices_value'][index], 'reference':item['prices_reference_id'][index], 'name':item['prices_name'][index], 'code':item['prices_code'][index], 'factor1':item['prices_factor1'][index], 'factor2':item['prices_factor2'][index] } for index, id in enumerate(item['prices_id']) ]
				item.pop('prices_id')
				item.pop('prices_product_id')
				item.pop('prices_value')
				item.pop('prices_factor1')
				item.pop('prices_factor2')
				item.pop('prices_reference_id')
				item.pop('prices_name')
				item.pop('prices_code')

			attributes = [{'id':id, 'name':item['atts_name'][index], 'value':item['atts_value'][index], 'factor1':item['atts_factor1'][index], 'factor2':item['atts_factor2'][index], 'reference':item['atts_reference'][index]} for index, id in enumerate(item['atts_id']) if id != None]
			item.pop('atts_id')
			item.pop('atts_name')
			item.pop('atts_value')
			item.pop('atts_factor1')
			item.pop('atts_factor2')
			item.pop('atts_reference')

	#        print 1232, attributes

	#        print attributes
			reversed = attributes[:]
			reversed.reverse()

			try:
				cost = [attributes.pop(len(reversed)-index-1) for index, attribute in enumerate(reversed) if attribute['name']==u'cost'][0]
			except:
				self.model.app.log2sys ( 'error', "\n    products Model products_full_pull()" )
				self.model.app.log2sys ( 'error', "    {}".format(sys.exc_info()) )
				self.model.app.log2sys ( 'error', "    {}".format(reversed) )
				raise

			product['cost_id'] = Decimal(cost['id'])
			product['meancost'] = Decimal(cost['value'])
			# product['tax'] = Decimal(cost['factor1'])
			product['margin'] = Decimal(cost['factor2'])


			## TAXES
			"""taxes contains a list of taxes, each one can be of any of the
			tax_kinds registered in the system, for history reasons the most
			common general tax [IVA] is contained in the [cost] attribute of
			a product, this must be converted to the format used for taxes
			instances wich is code, name, percent, value, reference"""

			# print(4446, reversed)

			reversed = attributes[:]
			reversed.reverse()

			taxes = []
			# taxes = [attributes.pop(len(reversed)-index-1) for index, attribute in enumerate(reversed) if attribute['name']==u'tax']
			for tax in [x for x in reversed if x['name']=='tax']:
				taxKind = [x for x in taxKinds if x['code'] == int(tax['reference'])][0]
				taxes.append({'code':taxKind['code'], 'name':taxKind['name'], 'factor':taxKind['value'], 'value':tax['value'], 'reference':taxKind['reference'].replace(', default', '')})

			if not taxes:
				if cost['reference']:
					taxKind = [x for x in taxKinds if x['code'] == Decimal(cost['reference'])][0]
					taxes.append({'code':taxKind['code'], 'name':taxKind['name'], 'factor':taxKind['value'], 'reference':taxKind['reference'].replace(', default', '')})

			## Temporal fix
			if not taxes:
				taxKind = taxKind_general
				taxes.append({'code':taxKind['code'], 'name':taxKind['name'], 'factor':taxKind['value'], 'reference':taxKind['reference'].replace(', default', '')})

			product['taxes'] = taxes


			reversed = attributes[:]
			reversed.reverse()
			stock0 = [attributes.pop(len(reversed)-index-1) for index, attribute in enumerate(reversed) if attribute['name']==u'stock']
			if stock0:
				product['stock_id'] = stock0[0]['id']
				# product['current'] = Decimal(stock0[0]['value'])
				product['minimum'] = Decimal(stock0[0]['factor1'])
				product['maximum'] = Decimal(stock0[0]['factor2'])

			unit = {}
			unit['code'] = item.pop('unit_code')
			unit['name'] = item.pop('unit_name')
			unit['shortname'] = item.pop('unit_shortname')
			product['unit'] = unit

			product['classification_id'] = item['classification_id']
			product['origin_id'] = item['origin_id']
			product['id'] = item['id']
			product['rstatus'] = item['rstatus']
			# product['maximum'] = item['maxStock']
			# product['minimum'] = item['minStock']
			product['kind'] = {'code':item['kind_code']}
			product['upc'] = item['upc']
			product['status'] = {'code':item.pop('status_code'), 'name':item.pop('status_name')}

			# print(type(item['current']), item['current'])
			if 'current'in item:
				if item['current'] >= 0 :
					product['current'] = item['current']
				else:
					product['current'] = Decimal(0)

			# product['attributes'] = attributes

			# print product

			products.append(product)

		# print products

		# print("""products.model.products_full_pull() - END""")

		return products


	def getProductAttribute(self, **filters):
		attribute = self.model.getOne('productattributes', **filters)
		return attribute


	def setProductAttribute(self, **data):
		""" Regresa None
			Regresar el atributo actualizado requeriria un acceso extra a la base de datos.
		"""
		# print "\nproducts.model.setProductAttribute()\n    %s" % data

		try:
			currentDateTime = datetime.datetime.today()

			dataNew = None

			data['rstatus'] = u'active'
			data['rspanstart'] = currentDateTime

			if 'id' in data.keys():
				dataNew = data
				data = self.model.getOne('productattributes', id=data['id'])
			elif 'product_id' in data.keys() and 'name' in data.keys():
				dataExistent = self.model.getOne('productattributes', product_id=data['product_id'], name=data['name'], rstatus=u'active')
				if dataExistent:
					dataNew = data
					data = dataExistent

			if dataNew:
				id = data.pop('id')
				data['rstatus'] = u'obsolete'
				data['rspanend'] = currentDateTime
				dataNew['rspanstart'] = data['rspanend']

				command = """UPDATE productattributes SET """
				valuesText = ""
				for value in dataNew.keys():
					if type(dataNew[value]) in [str, datetime.datetime]:
						valuesText += "%s = '%s', " % (value, dataNew[value])
					else:
						try:
							if type(dataNew[value]) in [unicode]:
								valuesText += "%s = '%s', " % (value, dataNew[value])
							else:
								valuesText += "%s = %s, " % (value, dataNew[value])
						except:
							valuesText += "%s = %s, " % (value, dataNew[value])
				command += "%s WHERE id=%s" % (valuesText.rstrip(', '), id)

	#            print command.encode('utf8')

				self.model.execute(command)

			command = """INSERT INTO productattributes """
			fieldsText = ""
			valuesText = ""
			for key in data.keys():
				if type(data[key]) in [str, datetime.datetime]:
					fieldsText += "%s, " % key
					valuesText += "'%s', " % data[key]
				elif data[key] == None:
					fieldsText += "%s, " % key
					valuesText += "Null, "
				else:
					try:
						if type(data[key]) in [unicode]:
							fieldsText += "%s, " % key
							valuesText += "'%s', " % data[key]
						else:
							fieldsText += "%s, " % key
							valuesText += "%s, " % data[key]
					except:
						fieldsText += "%s, " % key
						valuesText += "%s, " % data[key]
			command = "%s (%s) VALUES (%s)" % (command, fieldsText.rstrip(", "), valuesText.rstrip(", "))

			# print command.encode('utf8')

			attr = self.model.execute(command)

			# print 6667, attr

		except:
			print ("\nException @ products.model.setProductAttribute()\n    %s" % sys.exc_info()[1])
			print ("    %s" % command.encode('utf8'))


	def setProduct(self, **data):
		"""
			Sets (INSERT) complete or partial (UPDATE) data of a product.

			Regresa None
			Regresar el producto actualizado requeriria un acceso extra a la base de datos.
		"""
		# print("\n    products.model.setProduct()")
		# print("    ", data)

		try:
			currentDateTime = datetime.datetime.today()

			if 'id' in data.keys():
				id = data.pop('id')
			else:
				id = None

			if 'aceptions' in data.keys():
				aceptions = data.pop('aceptions')
			else:
				aceptions = []

			aception = {}
			if 'code' in data.keys():
				aception['code'] = data.pop('code')
			if 'code2' in data.keys():
				aception['reference'] = data.pop('code2')
			if 'name' in data.keys():
				aception['name'] = data.pop('name')
			if aception:
				holder = self.model.rol_full_pull(kind=u'holder')
				aception['rol_id'] = holder['id']
				aception['rstatus'] = u'active'
				aceptions.append(aception)

			## PRICES
			if 'prices' in data.keys():
				prices = data.pop('prices')
			else:
				prices = []

			## LINES
			if 'lines' in data.keys():
				lines = data.pop('lines')
			else:
				lines = []

			## CLASIFICACIÓN
			if not 'classification_id' in data.keys():
				if 'classification' in data.keys():
					name = data.pop('classification')
					classification = self.model.getAttribute(category=u'productClassification', name=name)
					if classification is None:
						classification = self.model.setAttribute(category=u'productClassification', name=name, rstatus='active')
					data['classification_id'] = classification['id']

			## SPAN
			# if not 'rspanstart' in data.keys():
				# data['rspanstart'] = currentDateTime

			ruser = data.pop('ruser', None)
			rspanstart = data.pop('rspanstart', None)
			rspanend = data.pop('rspanend', None)

			## COST
			cost = {}
			if 'cost_id' in data.keys():
				cost['id'] = data.pop('cost_id')
			if 'meancost' in data.keys():
				cost['value'] = data.pop('meancost')

			if 'margin' in data.keys():
				cost['factor2'] = data.pop('margin')

			## TAXES
			taxes = []
			if 'taxes' in data.keys():
				taxesData = data.pop('taxes')
				special0 = [x for x in taxesData if 'special' in x['reference']]
				# print(special0)

				if special0:

					special = taxesData.pop(taxesData.index(special0[0]))

					#! Falta incluir impuestos modificados (que incluyan 'id')
					tax = {'value':special['value'], 'reference':special['code']}
					taxes.append(tax)

				if taxesData:
					default0 = [x for x in taxesData if 'default' in x['reference']]
					if default0:

						default = taxesData.pop(taxesData.index(default0[0]))
						cost['factor1'] = default['value']
						cost['reference'] = default['code']

				if taxesData:
					other = taxesData[0]

					cost['factor1'] = other['value']
					cost['reference'] = other['code']

			## STOCK
			stock = {}
			if 'stock_id' in data.keys():
				stock['id'] = data.pop('stock_id')
			if 'current' in data.keys():
				stock['value'] = data.pop('current')
			if 'minimum' in data.keys():
				stock['factor1'] = data.pop('minimum')
			if 'maximum' in data.keys():
				stock['factor2'] = data.pop('maximum')

			#! Missing current stock setting routine

			if 'kind' in data.keys():
				## kind.code is mandatory
				if 'code' not in data['kind'].keys():
					data['kind']['code'] = self.model.getAttribute(category='processKind', name=data['kind']['name'])['code']
				data['kind_code'] = data.pop('kind')['code']
			elif 'kind_code' in data.keys():
				logging.getLogger('system').error((u"documents.model.setDocument()\n    Invalid kind data\n    {}".format(data)).encode('utf8'))


			if data:

				# STATUS
				# if not 'rstatus' in data.keys():
					# data['rstatus'] = 'active'

				if id:
					command = """UPDATE products SET """
					pairsText = ""
					for key in data.keys():
						if type(data[key]) in [str, datetime.datetime, datetime.date, Decimal]:
							pairsText += "%s='%s', " % (key, data[key])
						else:
							try:
								if type(data[key]) in [unicode]:
									pairsText += "%s='%s', " % (key, data[key])
								else:
									pairsText += "%s=%s, " % (key, data[key])
							except:
								pairsText += "%s=%s, " % (key, data[key])

					command += "%s WHERE id=%s " % (pairsText.rstrip(', '), id)

					# print command.encode('utf8')

					self.model.execute( command )

				else:
					command = """INSERT INTO products """
					fieldsText = ""
					valuesText = ""
					for key in data.keys():
						if type(data[key]) in [str, datetime.datetime, datetime.date]:
							fieldsText += "%s, " % key
							valuesText += "'%s', " % data[key]
						elif data[key] == None:
							fieldsText += "%s, " % key
							valuesText += "Null, "
						else:
							try:
								if type(data[key]) in [unicode]:
									fieldsText += "%s, " % key
									valuesText += "'%s', " % data[key]
								else:
									fieldsText += "%s, " % key
									valuesText += "%s, " % data[key]
							except:
								fieldsText += "%s, " % key
								valuesText += "%s, " % data[key]

					command = "%s (%s) VALUES (%s) RETURNING id" % (command, fieldsText.rstrip(", "), valuesText.rstrip(", "))

					# print(1110121, command)

					id = self.model.execute(command)['id']

					# print(1110122, id)

					## ADD FIRST DOCUMENT ITEM FOR STOCK INITIALIZATION
					if cost:
						cost_ = cost['value']
					else:
						cost_ = Decimal('0.0000')

					if prices:
						#! registers first price available
						price_ = prices[0]['value']
					else:
						price_ = Decimal['0.0000']

					command = """INSERT INTO documentitems (document_id,
		subject_id, quantity, cost, price, discountf, taxf, net_price, stock)
		SELECT id, {}, 0.00, {}, {}, 0.00, 0.00, 0.00, 0.00
		FROM documents
			JOIN (SELECT code FROM attributes
				WHERE category='documentKind' AND name='InitialStock') AS kinds ON (kinds.code=documents.kind_code)
		WHERE number='{}'
					""".format(id, cost_, price_, datetime.datetime.today().year)

					# print(1110123, command)

					self.model.execute( command )


			if ruser:
				self.setProductAttribute(product_id=dbData['id'], name='ruser', value='{}'.format(ruser))

			if rspanstart:
				self.setProductAttribute(product_id=dbData['id'], name='rspanstart', value='{}'.format(rspanstart))

			if rspanend:
				self.setProductAttribute(product_id=dbData['id'], name='rspanend', value='{}'.format(rspanend))

			if cost:
				cost['name'] = u'cost'
				cost['product_id'] = id
				self.setProductAttribute(**cost)

			if stock:
				stock['name'] = u'stock'
				stock['product_id'] = id
				self.setProductAttribute(**stock)

			# TAXES (ONLY OF TYPE SPECIAL)
			# print(taxes)
			if taxes:
				for tax in taxes:
					tax['name'] = u'tax'
					tax['product_id'] = id
					self.setProductAttribute(**tax)

			# ACEPTIONS
			for aception in aceptions:
				if 'id' not in aception.keys():
					if 'product_id' not in aception.keys():
						aception['product_id'] = id
				self.setAception(**aception)

			# PRICES
			for price in prices:
				if 'id' not in price.keys():
					if 'product_id' not in price.keys():
						price['product_id'] = id
				self.setPrice(**price)

			# LINES

			for line in lines:
				if 'id' not in line:
					line['category'] = 'productLine'
					line = self.model.attribute_set(**line)
				line['product_id'] = id
				self.setLine(**line)

			return id

		except:
			print ("\nException @ products.model.setProduct()\n    %s" % sys.exc_info()[1])
			print (traceback.format_tb(sys.exc_info()[2]))
			print (data)
			# print "    %s" % command.encode('utf8')

		# print("\n    products.model.setProduct() - END")


	def getProductsCount(self):
		cursor = self.model.execute("""SELECT count(*) FROM products""", giveCursor=True)
		count = cursor.fetchone()['count']
		cursor.close()
		return count


	def getDefaultProductKind(self):
		productKind = self.model.getAttribute(category=u'productKind', value=u'default')
		return productKind['code']

	_lines = []
	def getProductLines(self):
		# print("        products.model.getProductLines()")
		# if self.productLinesChanged:

		# self._lines = self.model.getAttributes(category=u'productLine', order=u'name')
		lines = self.model.getAll('attributes', category=u'productLine', order='name')
		self._lines = []
		for line in lines:
			line['code'] = line['reference']
			line.pop('category')
			line.pop('reference')

			self._lines.append(line)
		self.productLinesChanged = False

		# print("        products.model.getProductLines()- END")
		return self._lines


	#~ def getLines(**filtros):
		#~ """ Filtra por referencia """
		#~ if 'referencia' in filtros.keys():
			#~ lines = getAttributes(grupo=u'líneaProducto', referencia=filtros['referencia'], order=u'nombre')
		#~ else:
			#~ lines = getAttributes(grupo=u'líneaProducto', order=u'nombre')
		#~ return lines



	def documentItems(**filters):
		f=g
		command = """SELECT partidasdocumento.*, documentos.fecha AS document_date, documentos.folio AS document_serial,
		documentos.descuentoporcentaje AS document_discountpercent,
		entidades.nombre AS rol_name, entidades.nombre2 AS rol_name2,
		operaciones.operaciones_tipo

		FROM partidasdocumento
		JOIN documentos USING (documento_id)
		JOIN roles ON (documentos.rol_id=roles.id)
		JOIN entidades ON (roles.entidad_id=entidades.id)
		JOIN operaciones_documentos USING (documento_id)
		JOIN

		(SELECT operacion_id, array_agg(ops.operacion_tipo) AS operaciones_tipo
			FROM operaciones as ops
			WHERE ops.operacion_tipo IN ('entrada', 'salida')
			GROUP BY operacion_id
			) AS operaciones

		USING (operacion_id)
		"""

		filtersText = ''
		for filter in filters.keys():
			if filter == 'tipo':
				if type(filters[filter]) == list:
					command += "JOIN atributos ON (documentos.tipo_id=atributos.id) "
					filtersText += "atributos.nombre IN %s AND " % (tuple(filters[filter]),)
			elif type(filters[filter]) in (str, datetime.datetime):
				filtersText += "%s='%s' AND " % (filter, filters[filter])
			# elif type(filters[filter]) in (list,):
				# temp = ("%s" % filters[filter]).replace("[", "{").replace("]","}").replace("'", '"')
				# filtersText += "%s='%s' AND " % (filter, temp)
			elif filters[filter] == None:
				filtersText += "%s is null AND " % filter
			else:
				try:
					if type(filters[filter]) in [unicode]:
						filtersText += "%s='%s' AND " % (filter, filters[filter])
					else:
						filtersText += "%s=%s AND " % (filter, filters[filter])
				except:
					filtersText += "%s=%s AND " % (filter, filters[filter])

		command += "WHERE %s " % filtersText.rstrip("AND ")
		command += "ORDER BY documentos.fecha DESC "

		# print command

		query(command)
		items = fetchAll()

		return items


	def elimina(**filtros):
		acepcion = man.session().query(Acepcion).filter(Acepcion.id==filtros['id']).one()

		acepciones = dameAcepciones(product_id=acepcion.product_id)

		for acepcion in acepciones:
			acepcion.fechabaja = datetime.datetime.today()
			acepcion.rstatus = u'eliminada'

		producto = acepcion.producto

		producto.fechabaja = datetime.datetime.today()
		producto.rstatus = u'eliminado'

		man.session().commit()






	def stock_get(self, subject_id):
		command = """
			SELECT documentitems.stock
			FROM documentitems
			JOIN documents ON (documents.id=documentitems.document_id)
			WHERE subject_id={}
			ORDER BY documents.date DESC LIMIT 1
		""".format(subject_id)

		stock = self.model.getOne(command)

		return stock


	def transaction_apply(self, processKind, document):
		# print("""\n    products.model.transaction_apply()""")

		try:
		# if True:
			index = None
			if processKind == u'Mercancía':

				# print(222001, document)

				try:
					document['taxes']
				except:
					print ("\nKeyError: 'taxes'\n")
					documentTaxFactor = 0
				else:
					try:
						document['taxes']['general']
					except:
						print ("\nKeyError: 'general'\n")
						documentTaxFactor = 0
					else:
						documentTaxFactor = document['taxes']['general']['factor']

				for index, item in enumerate(document['items']):

					print ('item:', item)

					product = item.pop('product')

					# print('product:', product)

					# item['subject_id'] = product['id']

					documentDiscountP = Decimal('0.00')

					if document['subtotal']:    # Now accepts zero due to cfdi requirements
						if 'discount' in document:
							documentDiscountP = document['discount'] / document['subtotal'] * 100

					newCost = item['price'] * (100-item['discountf'])/100 * (100-documentDiscountP)/100

					newCurrent = product['current'] + item['quantity']

					try:
						newMeanCost = ((product['current'] * product['meancost'] + item['quantity'] * newCost) / newCurrent).quantize(Decimal('0.0001'))
					except:
						## There was an error calculating newMeanCost
						## Probably erroneous current stock
						newMeanCost = newCost.quantize(Decimal('0.0001'))

					## Cost / Mean Cost deviation
					if newCost:     # Now accepts zero due to cfdi requirements
						costDeviationP = ( newCost - newMeanCost ) / newCost * 100
					else:
						costDeviationP = Decimal('0.00')

					## Modified product data
					modifiedProduct = {}
					# modifiedProduct['current'] = newCurrent

					# print(index, product['meancost'], newMeanCost)

					if product['meancost'] != newMeanCost:
						modifiedProduct['meancost'] = newMeanCost

					try:
						## Modified price
						if self.model.recalculatePriceOnPurchase():

							# print("    Recalculating Price ...")

							priceDeviationMarginP = Decimal(self.model.getAttribute(category=u'system', name=u'margenDeCambio', cast_='product')['value'])

							sentido = self.model.getAttribute(category=u'system', name=u'sentidoDeCambio', cast_='product')['value']

							# print(priceDeviationMarginP, sentido)

							attributes = []

							for price in product['prices']:
								# print('price:', price)

								attribute = {}

								netMargin = ((100 + product['margin']) * (100 + Decimal(price['factor1'])) / 100 * (100 - Decimal(price['factor2'])) / 100) - 100
								## Apply cost deviation
								## Act on deviation bigger than 5%, newMeanCost = newCost - 5%
								# print(netMargin)
								if costDeviationP > Decimal('5'):
									newPrice = (newCost * Decimal('0.95')) * (100 + item['taxf']) / 100 * (100 + documentTaxFactor) / 100 * (100 + netMargin) / 100
								else:
									newPrice = newMeanCost * (100 + item['taxf']) / 100 * (100 + documentTaxFactor) / 100 * (100 + netMargin) / 100

								# print(newPrice)
								if sentido == u'+/-':
									if Decimal(price['value']) * (100 + priceDeviationMarginP) / 100 < newPrice < Decimal(price['value']) * (100 - priceDeviationMarginP) / 100:
										attribute['value'] = "{}".format(newPrice)
										# self.model.setProductAttribute(id=price['id'], value="{}".format(newPrice))
								elif sentido == u'+':
									if newPrice > Decimal(price['value'])*(100 + priceDeviationMarginP) / 100:
										attribute['value'] = "{}".format(newPrice)
										# self.model.setProductAttribute(id=price['id'], value="{}".format(newPrice))

								# print(123, attribute)
								if attribute:
									# print(234, attribute)
									attribute['id'] = price['id']
									attributes.append(attribute)

							if attributes:
								# print(345, attributes)
								modifiedProduct['attributes'] = attributes

							# print(modifiedProduct)
							# print

					except:
						print ("    ==== ERROR @ products.model.transaction_apply()")
						print (sys.exc_info())
						raise

					"""
					## Stock change
					# self.model.setDocumentItem({'id':item['id'], 'stock':self.stock_get(item['subject_id']) + item['quantity']})
					"""

					# print(333001, product)
					try:
						## Aception modifications
						modifiedAception = {}
						aception = [x for x in product['aceptions'] if x['rol_id'] == document['rol_id']][0]
					except:
						print ("    products.model.transaction_apply()")
						print ("    ", aception)
						# print(996, item)

					if aception['cost'] != item['price']:
						modifiedAception['cost'] = item['price']

					if aception['individualdiscount'] != item['discountf']:
						modifiedAception['individualdiscount'] = item['discountf']

					if 'discountpercent' in document:
						if aception['generaldiscount'] != document['discountpercent']:
							modifiedAception['generaldiscount'] = document['discountpercent']

					if modifiedAception:
						modifiedAception['id'] = aception['id']
			#                self.model.setAception(**modifiedAception)
						modifiedProduct['aceptions'] = [modifiedAception]

					# item['product'] = modifiedProduct

					# print('modifiedProduct:', modifiedProduct)

					if modifiedProduct:
						modifiedProduct['id'] = product['id']

					self.model.setProduct(**modifiedProduct)

			elif processKind == u'venta':

				generalDiscount = Decimal("0.00")

				for item in items:
					# print(item)

					product = item.pop('product')

					item['subject_id'] = product['id']

					# newCost = item['price'] * (100-item['discount'])/100 * (100-generalDiscount())/100
					#newMeanCost = (product['current']*product['meancost'] + item['quantity']*newCost) / (product['current']+item['quantity'])
					newCurrent = product['current'] - item['quantity']

					## Modified product data
					modifiedProduct = {}
					modifiedProduct['current'] = newCurrent

					# if product['meancost'] != newMeanCost:
						# modifiedProduct['meancost'] = newMeanCost

					if modifiedProduct:
						modifiedProduct['id'] = product['id']

					self.model.setProduct(**modifiedProduct)

					## Stock change
					self.model.setDocumentItem({'id':item['id'], 'stock':self.stock_get(item['subject_id']) - item['quantity']})

		except:
			print ("\nException @ products.model.transaction_apply()\n    {}".format(sys.exc_info()))
			print ("index", index)
			raise

		# print("""    products.model.transaction_apply() - END""")





	def validateProduct(self, data, mode):
		"""
			Realiza la validación de lógica de negocios
				La clasificación se recibe como una cadena para uniformizar el
				proceso de validación
		"""
		valid = True
		mesagges = ""

		## La validación de código se hace en la interfase

		## Determinar si la clasificación ya existe, o es una nueva
		if 'classification' in data.keys():
			mesagges += u"La clasificación no existe, se creará\n"

		return valid, mesagges



	def createDb(self):
		# print "    productos.model.createDb()"
		try:
			print ("        CREATING TABLE products ...", end='')
			self.model.execute("""CREATE TABLE products (
				id          SERIAL PRIMARY KEY,
				upc         TEXT DEFAULT '',
				origin_id   INTEGER REFERENCES rols (id),
				kind_code   INTEGER REFERENCES attributes (code),
				classification_id    INTEGER REFERENCES attributes (id),
				unit_code   INTEGER REFERENCES attributes (code),
				status      INTEGER REFERENCES attributes (code),

				rstatus     TEXT DEFAULT 'active'
			)""")
			print ("Success")
		except:
			print ("Failed")
			print (sys.exc_info()[1])

		try:
			"""
			name   value      factor1   factor2
			cost    meancost    tax       margin
			stock   current     minimum   maximum
			"""
			print ("        CREATING TABLE productattributes ...", end='')
			self.model.execute("""CREATE TABLE productattributes (
				id            SERIAL PRIMARY KEY,
				product_id    INTEGER REFERENCES products (id),
				name          TEXT,
				value         TEXT DEFAULT '',
				factor1       TEXT DEFAULT '',
				factor2       TEXT DEFAULT '',
				reference     TEXT DEFAULT '',

				rstatus       TEXT DEFAULT 'active',
				rspanstart    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				rspanend      TIMESTAMP,
				ruser         INTEGER REFERENCES rols (id)
			)""")
			print ("Success")
		except:
			print ("Failed")
			print (sys.exc_info()[1])

		try:
			print ("        CREATING TABLE aceptions ...", end='')
			self.model.execute("""CREATE TABLE aceptions (
				id          SERIAL PRIMARY KEY,
				product_id  INTEGER REFERENCES products(id),
				rol_id      INTEGER REFERENCES rols(id),
				code        TEXT,
				name        TEXT,
				cost        DECIMAL (12,4),
				individualdiscount  DECIMAL (6,2),
				generaldiscount     DECIMAL (6,2),
				reference   TEXT DEFAULT '',
				quota       DECIMAL(6, 2),

				rstatus     TEXT DEFAULT 'active',
				rspanstart  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				rspanend    TIMESTAMP,
				ruser       INTEGER REFERENCES rols (id)
			)""")
			# UniqueConstraint('product_id', 'rol_id', 'status', 'fechaalta')
			print ("Success")
		except:
			print ("Failed")
			print (sys.exc_info())



	def initDb(self):
		# print "\n    productos.model.initDb()"
		try:
			version = int(self.model.getOne('attributes', code=40001)['value'])
		except:
			self.createDb()
			print ("        Initializing products data")
			version = 0

		if version < 1:

			# 40000-40099 Products
			# 40100-40129    productKind
			# 40130-40159    units
			# 40160-40179    productStatus
			# 40180-40399
			# 40400-40499    Prices
			# 40500-40999    Classifications
			# 41000-49999

			# 81000-81999    Brands
			# 82000-         Divisions
			# 82100-82       Lines
			# 83000-83999    Families

			registros = [
				[40001, u'system',    u'databaseVersion',   u'',        u''],

				[40005, u'system',    u'capturaActualPermitida', u'0',  u''],
				[40007, u'system',    u'capturaLineaHabilitada', u'1',  u''],
				[40009, u'system',    u'capturaClasificacionObligatoria', u'1', u''],
				[40011, u'system',    u'useOwnCode',        u'1',       u''],
				[40012, u'system',    u'useUniversalCode',  u'0',       u''],
				[40013, u'system',    u'useAuxiliaryCode',  u'0',       u''],

				[40017, u'system',    u'descuentoEnabled',  u'1',       u''],
				[40019, u'system',    u'impuestoEnabled',   u'1',       u''],

				[40031, u'system',    u'stock_enabled',     u'1',       u''],

				[40103, u'productKind', u'Artículo',        u'default', u''],
				[40105, u'productKind', u'Equipo',          u'',        u''],
				[40107, u'productKind', u'Parte',           u'',        u''],
				[40109, u'productKind', u'Ensamble',        u'',        u''],
				[40111, u'productKind', u'Servicio',        u'',        u''],
				[40113, u'productKind', u'Insumo',          u'',        u''],

				[40131, u'unit',        u'-',               u'',        u'-'],
				[40135, u'unit',        u'Pieza',           u'default', u'pza'],
				[40137, u'unit',        u'Metro',           u'',        u'mt'],
				[40139, u'unit',        u'Kilogramo',       u'',        u'kg'],
				[40145, u'unit',        u'Litro',           u'',        u'lt'],
				[40151, u'unit',        u'Servicio',        u'',        u'serv'],

				[40161, u'productStatus', u'Intacto',       u'0',       u''],
				[40163, u'productStatus', u'Activo',        u'0',       u''],
				[40165, u'productStatus', u'Latente',       u'0',       u''],
				[40167, u'productStatus', u'Obsoleto',      u'1',       u''],
				[40169, u'productStatus', u'Liquidado',     u'1',       u''],
				[40160, u'productStatus', u'default',       u'40161',   u''],

				[40205, u'system',     u'sentidoDeCambio',  u'+/-',     u''],
				[40207, u'system',     u'margenDeCambio',   u'5',       u''],

				[40221, u'priceRule',  u'General',          u'default', u'1a'],
				[40223, u'priceRule',  u'Preferente',       u'',        u'2i'],

				[40231, u'system',   u'defaultBaseMargin',  u'0',       u''],

				[40421, u'system',  u'priceMarginKind', u'finalDiscountBased', u''],

				[40500, u'productClassification', u'',      u'',        u''],

				# [80101, u'tipoEquipo', u'Sedán',        u'',    u''],
				# [80102, u'tipoEquipo', u'Familiar',     u'',    u''],
				# [80103, u'tipoEquipo', u'Monovolumen',  u'',    u''],
				# [80104, u'tipoEquipo', u'Furgoneta',    u'',    u''],
				# [80105, u'tipoEquipo', u'Utilitario',   u'',    u''],
				# [80106, u'tipoEquipo', u'Pickup',       u'',    u''],
				# [80107, u'tipoEquipo', u'Reparto',      u'',    u''],

				# [81051, u'marcaEquipo', u'Acura',      u'',    u''],
				# [81073, u'marcaEquipo', u'Audi',       u'',    u''],
				# [81095, u'marcaEquipo', u'BMW',        u'',    u''],
				# [81017, u'marcaEquipo', u'Buick',      u'',    u''],
				# [81139, u'marcaEquipo', u'Cadillac',   u'',    u''],
				# [81161, u'marcaEquipo', u'Chevrolet',  u'',    u''],
				# [81183, u'marcaEquipo', u'Chrysler',   u'',    u''],
				# [81205, u'marcaEquipo', u'Citroen',    u'',    u''],
				# [81227, u'marcaEquipo', u'Dodge',      u'',    u''],
				# [81249, u'marcaEquipo', u'FAW',        u'',    u''],
				# [81271, u'marcaEquipo', u'Fiat',       u'',    u''],
				# [81293, u'marcaEquipo', u'Ferrari',    u'',    u''],
				# [81315, u'marcaEquipo', u'Ford',       u'',    u''],
				# [81337, u'marcaEquipo', u'GMC',        u'',    u''],
				# [81359, u'marcaEquipo', u'Honda',      u'',    u''],
				# [81381, u'marcaEquipo', u'Hummer',     u'',    u''],
				# [81403, u'marcaEquipo', u'Hyundai',    u'',    u''],
				# [81425, u'marcaEquipo', u'Isuzu',      u'',    u''],
				# [81447, u'marcaEquipo', u'Jaguar',     u'',    u''],
				# [81469, u'marcaEquipo', u'Jeep',       u'',    u''],
				# [81491, u'marcaEquipo', u'Kia',        u'',    u''],
				# [81513, u'marcaEquipo', u'Land Rover', u'',    u''],
				# [81535, u'marcaEquipo', u'Lexus',      u'',    u''],
				# [81557, u'marcaEquipo', u'Lincoln',    u'',    u''],
				# [81579, u'marcaEquipo', u'Mazda',      u'',    u''],
				# [81601, u'marcaEquipo', u'Mercedes-Benz', u'', u''],
				# [81623, u'marcaEquipo', u'Mini',       u'',    u''],
				# [81645, u'marcaEquipo', u'Mitsubishi', u'',    u''],
				# [81667, u'marcaEquipo', u'Nissan',     u'',    u''],
				# [81689, u'marcaEquipo', u'Opel',       u'',    u''],
				# [81711, u'marcaEquipo', u'Peugeot',    u'',    u''],
				# [81733, u'marcaEquipo', u'Pontiac',    u'',    u''],
				# [81755, u'marcaEquipo', u'Porsche',    u'',    u''],
				# [81777, u'marcaEquipo', u'Renault',    u'',    u''],
				# [81799, u'marcaEquipo', u'Saab',       u'',    u''],
				# [81821, u'marcaEquipo', u'Seat',       u'',    u''],
				# [81843, u'marcaEquipo', u'Subaru',     u'',    u''],
				# [81865, u'marcaEquipo', u'Suzuki',     u'',    u''],
				# [81887, u'marcaEquipo', u'Toyota',     u'',    u''],
				# [81909, u'marcaEquipo', u'Volkswagen', u'',    u''],
				# [81931, u'marcaEquipo', u'Volvo',      u'',    u''],

				[81031, 'brand', 'Acros',           '', '014'],
				[81090, 'brand', 'Black & Decker',  '', '010'],
				[81235, 'brand', 'Ekco',            '', '010'],
				[81347, 'brand', 'Hamilton Beach',  '', '010'],
				[81411, 'brand', 'IEM',             '', '014'],
				[81697, 'brand', 'Oster',           '', '010'],

				[82005, 'division', 'Educación Básica', '', ''],
				[82010, 'division', 'Electrodomésticos Menores', 'default', ''],
				[82014, 'division', 'Electrodomésticos', '', '' ],
				[82030, 'division', 'Gas', '', ''],
				[82054, 'division', 'Insumos', '', '']





			]

			for registro in registros:
				data = {'code':registro[0], 'category':registro[1], 'name':registro[2], 'value':registro[3], 'reference':registro[4], 'cast_':'product'}
				self.model.set('attributes', **data)

			# marca = self.model.getOne('attributes', category=u'marcaEquipo', name=u'Ford')
			# try:
				# registros = [
					# [82101, u'lineaEquipo', u'Ikon',      u'%s' % marca['id'], u''],
					# [82105, u'lineaEquipo', u'Focus',     u'%s' % marca['id'], u''],
					# [82109, u'lineaEquipo', u'Mondeo',    u'%s' % marca['id'], u''],
					# [82113, u'lineaEquipo', u'Mustang',   u'%s' % marca['id'], u''],
					# [82117, u'lineaEquipo', u'F',         u'%s' % marca['id'], u''],
					# [82121, u'lineaEquipo', u'Navigator', u'%s' % marca['id'], u'']
					# ]
				# for registro in registros:
					# data = {'code':registro[0], 'category':registro[1], 'name':registro[2], 'value':registro[3], 'reference':registro[4]}
					# self.model.set('attributes', **data)
			# except:
				# pass

			version = 15
			self.model.set('attributes', code=40001, value=version)

			print ("            Applied version {}".format(version))


		if version > 15:
			print (u"        LA BASE DE DATOS DEL MÓDULO products ES UNA VERSION MÁS RECIENTE QUE LA REQUERIDA\nTAL VEZ EL SISTEMA NO FUNCIONE ADECUADAMENTE")

		# print "        products data initialized"


if __name__ == "__main__":
	print ("Test routine not implemented for products.model")


"""
  ~~~~  Change log  ~~~~



  test

  Un producto es una entidad única e independiente.

  Puede tener algunos atributos que varían de acuerdo a la percepción
  de otros, en este caso los proveedores y clientes. Ej código, nombre,
  clasificación, costo.

  Estos datos se registran en una tabla satelite, indicando de quien es
  la percepción. De esta manera se mantiene la integridad de los datos
  de producto.


  Determinación de códigos de productos.
	Códigos locales
	Cada vez hay más globalización en productos, lo que genera
	uniformidad de información, muchos productos tienen códigos usados
	internacionalmente, se recomienda usar estos estandares, si se
	requiere una diferenciación extra se recomienda agregar caracteres
	al estandar.
	Si no se cuenta con un código estándar, se recomienda usar el código
	del fabricante.

	Códigos externos
	Se usa el proporcionado por el proveedor. No se recomienda
	cambiarlo, porque se generarían errores en la comunicación con el
	proveedor.
	Si el proveedor cambia sus datos, EB puede registrar esos cambios
	sin problemas, sin perder información ya registrada.



  Issues

	Precio2 may lead to crash if capture hability is changed. Design
	time.

"""



