import base
import os
import shutil
import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.targets['1.2.26'] = 'http://ovh.dl.sourceforge.net/sourceforge/libpng/libpng-1.2.26.tar.gz'
        self.targetInstSrc['1.2.26'] = 'libpng-1.2.26'
        self.defaultTarget = '1.2.26'
    
    def setDependencies( self ):
        self.hardDependencies['virtual/base'] = 'dev-util/win32libs'

class subclass(base.baseclass):
  def __init__( self, **args ):
    base.baseclass.__init__( self, args=args )
    self.createCombinedPackage = True
    self.buildType = "Release"
    self.subinfo = subinfo()
    if self.compiler <> "mingw":
      print "error: can only be build with MinGW (but in the end a mingw/msvc combined package is created"
      exit( 1 )

  def unpack( self ):
    if( not self.kdeSvnUnpack() ):
      return False
    # the cmake script is in libpng-src/scripts
    srcdir  = os.path.join( self.workdir, self.instsrcdir, "scripts", "CMakeLists.txt" )
    destdir = os.path.join( self.workdir, self.instsrcdir,            "CMakeLists.txt" )
    shutil.copy( srcdir, destdir )
    
    return True

  def compile( self ):
    self.kdeCustomDefines = "-DPNG_TESTS=OFF -DPNG_STATIC=OFF -DPNG_NO_STDIO=OFF"
    return self.kdeCompile()

  def install( self ):
    return self.kdeInstall()

  def make_package( self ):
    # auto-create both import libs with the help of pexports
    self.stripLibs( "libpng12" )

    # auto-create both import libs with the help of pexports
    self.createImportLibs( "libpng12" )

    # now do packaging with kdewin-packager
    self.doPackaging( "libpng", self.buildTarget )

    return True

if __name__ == '__main__':
    subclass().execute()
