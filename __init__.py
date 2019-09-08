# -*- coding: utf-8 -*-

 ##############################################
 ##                                            ##
 ##               Products package              ##
 ##                                             ##
 ##                                             ##
 ##              from Basiq Series              ##
 ##           by Críptidos Digitales            ##
 ##                 GPL (c)2008                 ##
  ##                                            ##
    ##############################################

"""
"""

from __future__ import print_function

__version__ = "0.1"             ## Go to end for change log

from PyQt4 import QtCore

from products import view
from products import model






class Controller(QtCore.QObject):

    _capture_mode = None
    def capture_mode_get(self):
        return self._capture_mode
    def capture_mode_set(self, value):
        self._capture_mode = value
    capture_mode = property(capture_mode_get, capture_mode_set)
    
    _cast = 'products'
    @property
    def cast(self):
        return self._cast
    # def cast_is(self, value):
        # return value == _cast
    
    @property
    def title(self):
        return u"Productos"


    def __init__(self, *args, **kwds):
        # print("    products.Controller.__init__()")

        args = list(args)
        self.owner = args.pop(0)
        self.app = args.pop(0)
        args = tuple(args)

        self.modules = kwds.pop('modules', {})

        self._capture_mode = kwds.pop('capture_mode', 1)

        QtCore.QObject.__init__(self, *args, **kwds)

        self.model = model.Model(self.app.model)

        if self.capture_mode is 1:
            self.master = view.Master(self.owner.master, self.cast, cnt=self)

        self.initOrder = 4
        self.displayOrder = 1

        # self.parent().menu.button_add(self, style="background-color:QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D0F8D0, stop:1 #A0F0A0);")
        
        self.connect(self.master, QtCore.SIGNAL('productLines_changed()'), self.loadProductLines)
        

        # print("    products.Controller.__init__() - END")


    def init(self, withViews=True):
        """        products.Controller.init()"""
        
        # if self.capture_mode is 1:
            # self.master = view.Master(self.owner.master, self.cast, cnt=self)
            
        self._productLines_changed = True
        self._productLines = []


    def hideLocalAception(self):
        self.master._localAceptionIsHidden = True

    def aception(self, **kwds):
        return self.model.getFullAception(**kwds)

    def aceptionsForSelect(self, **kwds):
        if 'kind' in kwds:
            if type(kwds['kind']) == dict:
                kwds['kind_code'] = kwds.pop('kind')['code']
        if 'status' in kwds:
            if type(kwds['status']) == dict:
                kwds['status'] = kwds.pop('status')['code']
        return self.app.model.products_full_pull(**kwds)

    def activePriceRules(self):
        return self.model.getActivePriceRules()

    def attribute(self, **kwds):
        return self.app.model.getAttribute(**kwds)


    def divisions_pull(self, **kwds):
        kwds['category'] = 'division'
        divisions = self.app.model.attributes_get(**kwds)
        return divisions
        
    def brands_pull(self, **kwds):
        kwds['category'] = 'brand'
        brands = self.app.model.attributes_get(**kwds)
        return brands
        
    def lines_pull(self, **kwds):
        kwds['category'] = 'line'
        lines = self.app.model.attributes_get(**kwds)
        return lines

    def families_pull(self, **kwds):
        kwds['category'] = 'family'
        families = self.app.model.attributes_get(**kwds)
        return families
        
    def models_pull(self, **kwds):
        kwds['category'] = 'model'
        models = self.app.model.attributes_get(**kwds)
        return models
        
    def classifications_pull(self, **kwds):
        kwds['category'] = 'classification'
        classifications = self.app.model.attributes_get(**kwds)
        return classifications
        

    def canEditCurrentStock(self):
        return not not int(self.app.model.getAttribute(name=u'capturaActualPermitida', cast_=u'product')['value'])
    def setCanEditCurrentStock(self, value):
        self.app.model.setAttribute(category='system', name=u'capturaActualPermitida', cast_=u'product', value={True:1, False:0}[value])


    def canEditTax(self):
        return not not int(self.app.model.getAttribute(category='system', name=u'impuestoEnabled', cast_=u'product')['value'])
    def setCanEditTax(self, value):
        self.app.model.setAttribute(category='system', name=u'impuestoEnabled', cast_=u'product', value={True:1, False:0}[value])


    def canEditProductLine(self):
        return not not int(self.app.model.getAttribute(category='system', name=u'capturaLineaHabilitada', cast_=u'product')['value'])
    def useLine_set(self, value):
        self.app.model.attribute_set(category='system', name=u'capturaLineaHabilitada', cast_=u'product', value={True:1, False:0}[value])


    def defaultProductKind(self):
        return self.model.getDefaultProductKind()

    def defaultUnitKind(self):
        unit = self.app.model.getAttribute(category=u'unit', value=u'default')
        return unit

    def documentItem_set(self, **kwds):
        return  self.app.model.setDocumentItem(**kwds)

    def documentItems(self, **kwds):
        return self.app.model.getFullDocumentItems(**kwds)

    def information_set(self, value):
        self.app.master.info = value


    def mustCaptureClassification(self):
        return not not int(self.app.model.getAttribute(cast_=u'product', name=u'capturaClasificacionObligatoria')['value'])
    def setMustCaptureClassification(self, value):
        self.app.model.setAttribute(category='system', cast_=u'product', name=u'capturaClasificacionObligatoria', value={True:1, False:0}[value])


    def priceRanges(self, **kwds):
        return self.model.getPriceRanges(**kwds)

    def product(self, **kwds):
        return self.model.product_full_pull(**kwds)

    def products(self, *conn, **kwds):
        return self.model.products_full_pull(*conn, **kwds)

    def productsCount(self):
        return self.model.getProductsCount()

    def productClassifications(self):
        return self.model.getClassifications()

    def productKinds(self):
        return self.app.model.getAttributes(category=u'productKind', name='!= default')
    
    ####    Product Lines    ####

    @property
    def productLineChanged(self):       
        self._productLines = self.model.getProductLines()
        self.loadProductLines()

    def loadProductLines(self):
        self.master.manager.loadLines(self._productLines)
        self.master.capture.loadLines()


    def productStatuss(self):
        return self.app.model.getAttributes(category='productStatus', name='!= default')

    def productStatus_default(self):
        return self.app.model.getAttribute(category='productStatus', name='default')


    # def setProduct(self, **kwds):
        # return self.model.setProduct(**kwds)
        
    def product_push(self, **data):
        return self.model.setProduct(**data)

    def suppliers(self):
        return self.app.model.rols_full_pull(kind='supplier', order='name')

    def suppliersCount(self):
        return self.app.model.getPersonsCount(kindName='supplier')

    def taxes(self):
        taxes = self.app.model.getAttributes(category=u'tax')
        return taxes
    
    def unitKinds(self):
        units = self.app.model.getAttributes(category=u'unit')
        return units


    def useAuxiliaryCode(self):
        return not not int(self.app.model.getAttribute(name=u'useAuxiliaryCode',  cast_=u'product')['value'])
    def setUseAuxiliaryCode(self):
        self.app.model.setAttribute(category='system', name=u'useAuxiliaryCode', cast_=u'product',value={True:1, False:0}[value])


    @property
    def useOwnCode(self):
        return not not int(self.app.model.attribute_get(name=u'useOwnCode', cast_=u'product')['value'])
    def useOwnCode_set(self, value):
        self.app.model.attribute_set(category='system', name=u'useOwnCode', cast_=u'product', value={True:1, False:0}[value])


    def useUniversalCode(self):
        return not not int(self.app.model.getAttribute(name=u'useUniversalCode', cast_=u'product')['value'])
    def setUseUniversalCode(self):
        self.app.model.setAttribute(category='system', name=u'useUniversalCode', cast_=u'product', value={True:1, False:0}[value])


    def validateProduct(self, *args):
        return self.model.validateProduct(*args)


    def master_init(self):
        if self.capture_mode is 1:
            self.master.init()
        # self.parent().menu.button_add(self, style="background-color:QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D0F8D0, stop:1 #A0F0A0);")

    def model_init(self):
        """        products.Controller.model_init()"""
        # self.model = model.Model(self.app.model)

        self.model.initDb()
        # self.model.plug()



if __name__ == "__main__":
    print ("Test routine not implemented for products")


"""
  ~~~~~~  Status de producto  ~~~~~~
    Descripción implícita
    Intacto     - Pedible    - Se dió de alta pero no se ha utilizado, sus datos pueden ser mostrados o actualizados.
    Activo      - Pedible    - Funciona normalmente
    Latente     - Pedible    - Inactivo, fue activo en algun momento, posiblemente activo en el futuro próximo.
    Obsoleto    - No pedible - Activo pero se inactivará en determinadas circunstancias (ej: al terminar las existencias).
    Liquidado   - No pedible - No se muestran ni actualizan sus datos en reportes normales, no se puede modificar, sólo se podrán consultar sus datos en reportes propios de este status.

  ~~~~~~  Determinación de precios  ~~~~~~
  Para productos que no han actualizado sus precios por falta de referencias directas como compras o lista de precios, se utilizará un factor que contemple los aumentos que han sufrido los precios por proveedor, por inflación, por material, etc.
  
  Los precios de venta se calculan aplicando un factor de utilidad a una base obtenida a partir del precio de compra.
  
  
  
  Siguiendo la política de posibilidad de reproducir cualquier dato calculado en cualquier momento,
  para obtener un precio se utilizan los siguientes registros.
  
  Se registra para entradas:
        Precio de lista Bruto
        Precio de lista Neto 
        Costo Bruto
        Costo Neto
        Descuentos
        Impuestos
        Costo Promedio
        
  Para salidas:
      X  Precio Bruto de lista al público.
      /  Precio Neto de lista al público.
      /  Costo Promedio Bruto
      
      El momento de cálculo de precio de lista neto al público está afectado por el parámetro -Cálculo de Precio de venta de lista neto al público- que puede contener [manual|automatico|semiautomatico].
      En modo automático, cuando se detecte una variación dentro de los rangos predeterminados, se registra el nuevo valor. En modo semiautomatico, los cambios se realizan cuando lo solicite el usuario o cuando el sistema avise que detectó una variación dentro de los rangos determinados y al usuario autorice. En modo manual los cambios se realizan sólocualdo el usuario lo solicite.
      El sistema buscará detectar variaciones de precios de lista neto al público al momento de procesar cambios en el precio de compra de los productos, ya sea por notificaciones de proveedor o por compra de productos.
      Debido a que el cambio de precio de compra se puede dar en cualquier momento, se debe contar con un registro independiente para este dato.

  ~~~~~~  Existencia actual  ~~~~~~
  La existencia actual de un producto no es una atributo propio del mismo, es un dato derivado del manejo de inventarios, al igual que el limite de existencia minima y el limite de existencia máxima. Estos son datos de naturaleza variante por lo que se registran como tales.
  La existencia actual de un producto se ve modificada cada vez que hay algún movimiento de ese producto, una entrada o salida de almacén de una determinada cantidad del producto, cada movimiento queda registrado como un documentItem, de aqui se deduce que la existencia actual se podría guardar en el registro de documentItem y consultarse a partir de el.
  Por razones de reducción de uso espacio de almacenamiento y ciclos de computación, se elige esta opción soble la alternativa de uso de atributo de producto para guardar este dato.
  Casos especiales.
  Al realizar careo entre existencias físicas reales y existencias en el sistema, pueden darse diferencias que no se pueden corregir por falta de documentación. Para este caso existen los documentos de ajuste de existencia, que tienen sus correspondientes documentItems que contiene la cantidad de diferencia.
  Al inicio de ciclos de control, es probable que ya exista una existencia en el almacén, el movimiento en el que se registró dicha existencia sería el último del ciclo de control anterior. En este caso se crea un documento de amparo de existencia inicial en lugar de usar el último movimiento disponible de cada producto.



  ~~~~~~  Lineamientos para registros  ~~~~~~
    Se utilizan 3 tipos de registros:
        - Base, datos únicos (no requieren
            más de una instancia), datos que no cambian (tipo, unidad, etc)
            o datos que cambian rara vez (costo promedio, impuesto, etc)

        - Renta, datos que definen la rentabilidad

        - Complemento, datos que requieren mas de una instancia para
            una misma base (acepciones)
        - Variables, datos que cambian constantemente (existencia actual)
        - Atributos, datos que requieren más de una instancia (precios, ubicaciones)

    Cada dato al sufrir un cambio provoca la creación de un registro sombra
    del registro que lo contiene, el registro sombra contiene los datos como
    estaban antes del cambio, mas la fecha del cambio.

    Esto permite reproducir el estado de la base de datos en cualquier momento.
    PEj, reproducir exactamente la captura de una factura a pesar de que hayan
    cambiado los datos los productos, se puede accesar los precios que se tenian
    al momento de la captura de la factura (datos que no quedan plasmados en los
    registros de la factura).


  PRODUCTO
  id                  inmutable
  tipo_id
  unidad_id
  clasificacion_id

  margen
  impuesto
  precio

  minimo
  maximo
  actual

  fechaalta
  fechabaja
  status

  ACEPCION


  Producto            Producto2   Acepción            Atributo
  (esencia)           (renta)     control)           (control)
  id                  id          id                  id
  tipo                margen      producto_id         acepcion_id
  clasificacion_id    impuesto    rol_id              tipo            precio      linea       base
  unidad_id           costo       codigo              valor           50.00       att_id      margen=50
                                  nombre              factor1         descuento=0             impuesto
                                  costo
                                  descuento
                                  quota
                                  minimo
                                  maximo
                                  actual
  fechaalta                       fechaalta           fechaalta
  fechabaja                       fechabaja           fechabaja
  status                          status              status



  Atributo    ( Precio, Linea,

  id
  producto_id
  nombre
  valor
  factor1
  factor2
  referencia
  usuario
  status
  fechaalta
  fechabaja


  Precio      (Atributo)  - Requiere más de una instancia y varias referencias
                            (tipo, descuento, etc)
  Línea       (Atributo)  - Requiere más de una instancia

  Nombre      (Acepción)  - Requiere más de una instancia


  ~~~~~~  NOTES  ~~~~~~
  
    Use Case 1 - IEPS
    
    Para desglosar los impuestos cuando existe IEPS, se suman los
    factores de IEPS e IVA.
    
        Precio neto / ( 1.16 + 0.0322 ) = Costo bruto
    



"""