# -*- coding: utf-8 -*-

 ##############################################
 ##                                            ##
 ##                    ui2py                    ##
 ##                                             ##
 ##                                             ##
 ##              from Basiq Series              ##
 ##           by Críptidos Digitales            ##
 ##                 GPL (c)2008                 ##
  ##                                            ##
    ##############################################


import os, fnmatch, subprocess



def listFiles( root, patterns='*', recurse=0, return_folders=0 ) :

    pattern_list = patterns.split( ';' )                    # Expand patterns from semicolon-separated string to list

    class Bunch :                                           # Collect input and output arguments into one bunch
        def __init__( self, **kwds ) : self.__dict__.update( kwds )

    arg = Bunch( recurse=recurse, pattern_list=pattern_list, return_folders=return_folders, results=[ ] )

    def visit( arg, dirname, files ) :

        for name in files :                                 # Append to arg.results all relevant files (and perhaps folders)
            fullname = os.path.normpath( os.path.join( dirname, name ) )
            if arg.return_folders or os.path.isfile( fullname ) :
                for pattern in arg.pattern_list :
                    if fnmatch.fnmatch( name, pattern ) :
                        arg.results.append( fullname )
                        break
        if not arg.recurse : files[ : ] = [ ]               # Block recursion if recursion was disallowed

    os.path.walk( root, visit, arg )

    return arg.results


def filterFiles( root, patterns='*', recurse=1, return_folders=0 ) :
    archivos = listFiles( root, patterns, recurse, return_folders )

    filtered = [ ]
    estosDirectoriosNo = ( 'CVS', 'DIST', 'BUILD', 'ATICO', 'RESOURCES', '.svn', '.hg' )

    for archivo in archivos :
        encontrado = False

        for directorio in estosDirectoriosNo :
            if directorio in archivo.upper( ) :
                encontrado = True

        if not encontrado :
            filtered.append( archivo )

    return filtered






if __name__ == "__main__":
    files = filterFiles( '.', '*.ui;')

    for index, file in enumerate(files):
        print len(files)-index, file
        args = ['pyuic4', file, '-o', file.replace('.', '_')+'.py']

        os.popen("pyuic4 %s -o %s " % (file, file.replace('.', '_')+'.py'))

    print '  resources.qrc'
    os.popen('pyrcc4 {} -o {} '.format('files/resources.qrc', 'resources_rc.py'))


    print 'Done.'
