#
# copyright (c) 2009 Ralf Habacker <ralf.habacker@freenet.de>
#

""" \package BuildSystemBase"""
from CraftDebug import craftDebug
from CraftBase import *
import compiler

from CraftOS.osutils import OsUtils


class BuildSystemBase(CraftBase):
    """provides a generic interface for build systems and implements all stuff for all build systems"""
    debug = True

    def __init__(self, typeName=""):
        """constructor"""
        CraftBase.__init__(self)
        self.supportsNinja = False
        self.supportsCCACHE = craftSettings.getboolean("Compile","UseCCache", False ) and compiler.isMinGW()
        self.supportsClang = craftSettings.getboolean("Compile","UseClang", False )
        self.buildSystemType = typeName


    def _getmakeProgram(self):
        makeProgram = craftSettings.get("Compile", "MakeProgram", "" )
        if self.subinfo.options.make.supportsMultijob:
            if self.supportsNinja and craftSettings.getboolean("Compile", "UseNinja", False):
                return "ninja"
            if makeProgram != "":
                craftDebug.log.debug("set custom make program: %s" % makeProgram)
            return makeProgram
        elif not self.subinfo.options.make.supportsMultijob:
            if "MAKE" in os.environ:
                del os.environ["MAKE"]

        if OsUtils.isWin():
            if compiler.isMSVC() or compiler.isIntel() :
                return "nmake /NOLOGO"
            elif compiler.isMinGW():
                return "mingw32-make"
            else:
                craftDebug.log.critical("unknown %s compiler" % self.compiler())
        elif OsUtils.isUnix():
            return "make"
    makeProgramm = property(_getmakeProgram)

    def compile(self):
        """convencience method - runs configure() and make()"""
        configure = getattr(self, 'configure')
        make = getattr(self, 'make')
        return configure() and make()

    def configureSourceDir(self):
        """returns source dir used for configure step"""
        # pylint: disable=E1101
        # this class never defines self.source, that happens only
        # in MultiSource.
        if hasattr(self,'source'):
            sourcedir = self.source.sourceDir()
        else:
            sourcedir = self.sourceDir()

        if self.subinfo.hasConfigurePath():
            sourcedir = os.path.join(sourcedir, self.subinfo.configurePath())
        return sourcedir

    def configureOptions(self, defines=""):
        """return options for configure command line"""
        if self.subinfo.options.configure.defines != None:
            defines += " %s" % self.subinfo.options.configure.defines
        
        if self.supportsCCACHE:
            defines += " %s" % self.ccacheOptions()
        if self.supportsClang:
            defines += " %s" % self.clangOptions()
        return defines

    def makeOptions(self, defines="", maybeVerbose=True):
        """return options for make command line"""
        if self.subinfo.options.make.ignoreErrors:
            defines += " -i"
        if self.subinfo.options.make.makeOptions:
            defines += " %s" % self.subinfo.options.make.makeOptions
        if maybeVerbose and craftDebug.verbose() > 1:
            if self.supportsNinja and craftSettings.getboolean("Compile","UseNinja", False ):
                defines += " -v "
            else:
                defines += " VERBOSE=1 V=1"
        return defines

    def dumpCraftDependencies( self ):
        """dump craft package dependencies"""
        output = dependencies.dumpDependencies( self.package )
        outDir = self.buildDir()
        outFile = os.path.join( outDir, self.package + '-craft.dot' )
        if not os.path.exists( os.path.dirname( outFile ) ):
            os.makedirs( os.path.dirname( outFile ) )
        with open( outFile, "w" ) as f:
            f.write( output )

        graphviz = GraphViz( self )

        if not graphviz.runDot( outFile, outFile + '.pdf', 'pdf' ):
            return False

        return graphviz.openOutput()

    def dumpDependencies(self):
        """dump package dependencies """
        return self.dumpCraftDependencies()

    def configure(self):
        return True
        
    def make(self):
        return True
        
    def install(self):

        # create post (un)install scripts
        if OsUtils.isWin():
            scriptExt = ".cmd"
        elif OsUtils.isUnix():
            scriptExt = ".sh"
        for pkgtype in ['bin', 'lib', 'doc', 'src', 'dbg']:
            script = os.path.join( self.packageDir(), "post-install-%s.%s" ) % (pkgtype, scriptExt)
            scriptName = "post-install-%s-%s.%s" % ( self.package, pkgtype, scriptExt )
            # are there any cases there installDir should be honored ?
            destscript = os.path.join( self.imageDir(), "manifest", scriptName )
            if not os.path.exists( os.path.join( self.imageDir(), "manifest" ) ):
                utils.createDir( os.path.join( self.imageDir(), "manifest" ) )
            if os.path.exists( script ):
                utils.copyFile( script, destscript )
            script = os.path.join( self.packageDir(), "post-uninstall-%s.%s" ) % (pkgtype, scriptExt)
            scriptName = "post-uninstall-%s-%s.%s" % ( self.package, pkgtype, scriptExt )
            # are there any cases there installDir should be honored ?
            destscript = os.path.join( self.imageDir(), "manifest", scriptName )
            if not os.path.exists( os.path.join( self.imageDir(), "manifest" ) ):
                utils.createDir( os.path.join( self.imageDir(), "manifest" ) )
            if os.path.exists( script ):
                utils.copyFile( script, destscript )
        return True

    def unittest( self ):
        """running unittests"""
        return True

    def ccacheOptions(self):
        return ""

    def clangOptions(self):
        return ""
