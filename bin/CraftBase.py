#
# copyright (c) 2009 Ralf Habacker <ralf.habacker@freenet.de>
#
import os
import sys
import datetime
from ctypes import *

import CraftDebug
import utils
import portage
import compiler
from CraftConfig import *
import utils


## @todo complete a release and binary merge dir below rootdir
# 1.  enable build type related otDmerge install settings
# 2a. use different install databases for debug and release
# 3. binary packages which are build type independent should be
# marked in both databases or should have a separate install database
# question: How to detect reliable this case ?




class CraftBase(object):
    """base class for craft system - holds attributes and methods required by base classes"""

    def __init__( self):
        # TODO: some __init__  of subclasses need to already have been
        # called here. That is really the wrong way round.
        object.__init__(self)
        CraftDebug.debug("CraftBase.__init__ called", 2)

        if not hasattr(self, 'subinfo'):
            self.filename, self.category, self.subpackage, self.package, mod = portage.PortageInstance._CURRENT_MODULE  # ugly workaround we need to replace the constructor
            self.subinfo = mod.subinfo(self, portage.PortageInstance.options)
            self.subinfo.__evilHack = portage.PortageInstance._CURRENT_MODULE#ugly workaround we need to replace the constructor
        else:
            self.filename, self.category, self.subpackage, self.package, mod = self.subinfo.__evilHack

        if not hasattr(self, 'buildSystemType'):
            self.buildSystemType = None

        # if implicit build time dependency is wanted, depend on internal packages
        # for this class and all of its ancestor classes
        if craftSettings.getboolean("General", "EMERGE_ENABLE_IMPLICID_BUILDTIME_DEPENDENCIES", False):
            for cls in type(self).mro():
                className = cls.__name__
                packageName = 'internal/%s' % className
                if os.path.exists(os.path.join(CraftStandardDirs.craftRoot() , 'craft', 'portage',
                        'internal', className, '%s-internal.py' % className)):
                    if self.subinfo and not packageName in self.subinfo.buildDependencies:
                        self.subinfo.buildDependencies[packageName] = 'default'

        if hasattr(self,'alreadyCalled'):
            return
        self.alreadyCalled = True

        self.versioned              = False
        self.CustomDefines       = ""
        self.createCombinedPackage  = False

        ## specifies if a build type related root directory should be used
        self.useBuildTypeRelatedMergeRoot = False
        if craftSettings.getboolean("General","EMERGE_MERGE_ROOT_WITH_BUILD_TYPE", False):
            self.useBuildTypeRelatedMergeRoot = True

        self.isoDateToday           = str( datetime.date.today() ).replace('-', '')

    def __str__(self):
        if self.subpackage:
            return "%s/%s/%s" % (self.category,self.subpackage,self.package)
        else:
            return "%s/%s" % (self.category,self.package)

    @property
    def noFetch(self):
        return craftSettings.getboolean("General", "WorkOffline", False)

    @property
    def noFast(self):
        return craftSettings.getboolean("General", "EMERGE_NOFAST", True )

    @property
    def noClean(self):
        return craftSettings.getboolean("General", "EMERGE_NOCLEAN", False )

    @property
    def forced(self):
        return craftSettings.getboolean("General", "EMERGE_FORCED", False )

    @property
    def buildTests(self):
        return craftSettings.getboolean("Compile", "BuildTests")


    def __adjustPath(self, directory):
        """return adjusted path"""
        if not self.subinfo.options.useShortPathes:
            return directory
        path = c_char_p(directory)
        length = windll.kernel32.GetShortPathNameA(path, 0, 0)
        if length == 0:
            return directory
        buf = create_string_buffer('\000' * (length + 1))
        windll.kernel32.GetShortPathNameA(path, byref(buf), length+1) # ignore function result...
        CraftDebug.debug("converting " + directory + " to " + buf.value)
        return buf.value

    def buildType(self):
        """return currently selected build type"""
        return craftSettings.get("Compile","BuildType")

    def compiler(self):
        """deprecated"""
        """return currently selected compiler"""
        return compiler.getCompilerName()

    def buildArchitecture(self):
        """return the target CPU architecture"""
        compiler.architecture()

    def workDirPattern(self):
        """return base directory name for package related work directory"""
        directory = ""
        if self.subinfo.options.useCompilerType == True:
            directory += "%s-" % compiler.getCompilerName()
        if self.subinfo.options.cmake.useIDE or self.subinfo.options.cmake.openIDE:
            directory += "ide-"
        if self.subinfo.options.useBuildType == False:
            directory += "%s" % (self.buildTarget)
        elif( self.buildType() == None ):
            directory += "%s-%s" % ("default", self.buildTarget)
        else:
            directory += "%s-%s" % (self.buildType(), self.buildTarget)
        return directory

    def imageDirPattern(self):
        """return base directory name for package related image directory"""
        directory = "image"

        if self.subinfo.options.useCompilerType == True:
            directory += '-' + compiler.getCompilerName()
        if self.subinfo.options.useBuildType == True:
            directory += '-' + self.buildType()
        directory += '-' + self.buildTarget
        return directory

    def sourceDir(self, dummyIndex=0):
        utils.abstract()

    def packageDir(self):
        """ add documentation """
        return self.__adjustPath( portage.getDirname( self.category, self.package ) )

    def buildRoot(self):
        """return absolute path to the root directory of the currently active package"""
        buildroot    = os.path.join( CraftStandardDirs.craftRoot(), "build", self.category, self.package )
        return self.__adjustPath(buildroot)

    def workDir(self):
        """return absolute path to the 'work' subdirectory of the currently active package"""
        _workDir = os.path.join( self.buildRoot(), "work" )
        return self.__adjustPath(_workDir)

    def buildDir(self):
        CraftDebug.debug("CraftBase.buildDir() called", 2)
        builddir = os.path.join(self.workDir(), self.workDirPattern())
        if self.subinfo.options.unpack.unpackIntoBuildDir and self.subinfo.hasTargetSourcePath():
            builddir = os.path.join(builddir, self.subinfo.targetSourcePath())
        CraftDebug.debug("package builddir is: %s" % builddir, 2)
        return self.__adjustPath(builddir)

    def imageDir(self):
        """return absolute path to the install root directory of the currently active package
        """
        imageDir =  os.path.join( self.buildRoot(), self.imageDirPattern() )
        return self.__adjustPath(imageDir)

    def installDir(self):
        """return absolute path to the install directory of the currently active package.
        This path may point to a subdir of imageDir() in case @ref info.targetInstallPath is used
        """
        if self.subinfo.hasInstallPath():
            installDir = os.path.join( self.imageDir(), self.subinfo.installPath())
        elif self.subinfo.options.install.installPath:
            installDir = os.path.join(self.imageDir(), self.subinfo.options.install.installPath)
        else:
            installDir = self.imageDir()
        return self.__adjustPath(installDir)

    def mergeSourceDir(self):
        """return absolute path to the merge source directory of the currently active package.
        This path may point to a subdir of imageDir() in case @ref info.targetInstallPath for a
        specific target or @ref self.subinfo.options.merge.sourcePath is used
        """
        if self.subinfo.hasMergeSourcePath():
            directory = os.path.join( self.imageDir(), self.subinfo.mergeSourcePath() )
        elif not self.subinfo.options.merge.sourcePath == None:
            directory = os.path.join( self.imageDir(), self.subinfo.options.merge.sourcePath )
        else:
            directory = self.imageDir()
        return self.__adjustPath(directory)

    def mergeDestinationDir(self):
        """return absolute path to the merge destination directory of the currently active package.
        This path may point to a subdir of rootdir in case @ref info.targetMergePath for a specific
        build target or @ref self.subinfo.options.merge.destinationPath is used
        """

        if self.subinfo.hasMergePath():
            directory = os.path.join( CraftStandardDirs.craftRoot(), self.subinfo.mergePath() )
        elif not self.subinfo.options.merge.destinationPath == None:
            directory = os.path.join( CraftStandardDirs.craftRoot(), self.subinfo.options.merge.destinationPath )
        elif not self.useBuildTypeRelatedMergeRoot or self.subinfo.options.merge.ignoreBuildType:
            directory = CraftStandardDirs.craftRoot()
        elif self.buildType() == 'Debug':
            directory = os.path.join(CraftStandardDirs.craftRoot(),'debug')
        elif self.buildType() == 'Release':
            directory = os.path.join(CraftStandardDirs.craftRoot(),'release')
        elif self.buildType() == 'RelWithDebInfo':
            directory = os.path.join(CraftStandardDirs.craftRoot(),'relwithdebinfo')
        else:
            directory = CraftStandardDirs.craftRoot()
        return self.__adjustPath(directory)

    def packageDestinationDir( self, withBuildType=True ):
        """return absolute path to the directory where binary packages are placed into.
        Default is to optionally append build type subdirectory"""

        CraftDebug.debug("CraftBase.packageDestinationDir called", 2)
        dstpath = craftSettings.get("General","EMERGE_PKGDSTDIR", os.path.join( CraftStandardDirs.craftRoot(), "tmp" ) )

        if withBuildType:
            if craftSettings.getboolean("General", "EMERGE_MERGE_ROOT_WITH_BUILD_TYPE", False ):
                dstpath = os.path.join( dstpath, self.buildType())

        if not os.path.exists(dstpath):
            utils.createDir(dstpath)
        return dstpath

    @property
    def buildTarget(self):
        return self.subinfo.buildTarget

    @property
    def version(self):
        return self.subinfo.defaultTarget

    @property
    def rootdir(self):
        return CraftStandardDirs.craftRoot()

    def enterBuildDir(self):
        CraftDebug.trace("CraftBase.enterBuildDir called")

        if ( not os.path.exists( self.buildDir() ) ):
            os.makedirs( self.buildDir() )
            CraftDebug.debug("creating: %s" % self.buildDir())

        os.chdir( self.buildDir() )
        CraftDebug.debug("entering: %s" % self.buildDir())

    def enterSourceDir(self):
        if ( not os.path.exists( self.sourceDir() ) ):
            return False
        CraftDebug.warning("entering the source directory!")
        os.chdir( self.sourceDir() )
        CraftDebug.debug("entering: %s" % self.sourceDir())

    def system( self, command, errorMessage="", debuglevel=1, **kw):
        """convencience function for running system commands.
        This method prints a debug message and then runs a system command.
        If the system command returns with errors the method prints an error
        message and exits if @ref self.subinfo.options.exitOnErrors  is true"""

        if utils.system( command, **kw):
            return True
        if self.subinfo.options.exitOnErrors:
            CraftDebug.warning("while running %s cmd: %s" % (errorMessage, str(command)))
        else:
            CraftDebug.warning("while running %s cmd: %s" % (errorMessage, str(command)))
        return False

    def proxySettings(self):
        host = craftSettings.get("General", 'EMERGE_PROXY_HOST', "")
        port = craftSettings.get("General", 'EMERGE_PROXY_PORT', "")
        username = craftSettings.get("General", 'EMERGE_PROXY_USERNAME', "")
        password = craftSettings.get("General", 'EMERGE_PROXY_PASSWORD', "")
        return [host, port, username, password]


    def binaryArchiveName(self, pkgSuffix=None, fileType=craftSettings.get("Packager", "7ZipArchiveType", "7z")):
        if not pkgSuffix:
            pkgSuffix = ''
            if hasattr(self.subinfo.options.package, 'packageSuffix') and self.subinfo.options.package.packageSuffix:
                pkgSuffix = self.subinfo.options.package.packageSuffix

        if self.subinfo.hasSvnTarget():
            version = "latest"
        else:
            version = self.getPackageVersion()[0]
        return "%s-%s-%s-%s%s.%s" % (
            self.package, compiler.architecture(), version, compiler.getShortName(), pkgSuffix, fileType)

    def cacheLocation(self):
        if craftSettings.getboolean("QtSDK", "Enabled", "False"):
            version = "QtSDK_%s" % craftSettings.get("QtSDK", "Version")
        else:
            version = craftSettings.get("PortageVersions", "Qt5")
            if not version:
                CraftDebug.die("Please set a value for\n"
                                "[PortageVersions]\n"
                                "Qt5")
            version = "Qt_%s" % version
        cacheDir = craftSettings.get("ContinuousIntegration", "CacheDir", os.path.join(CraftStandardDirs.downloadDir(), "binary"))
        return os.path.join(cacheDir, sys.platform, version,
                               compiler.getCompilerName(), self.buildType())

    def cacheRepositoryUrl(self):
        if craftSettings.getboolean("QtSDK", "Enabled", "False"):
            version = "QtSDK_%s" % craftSettings.get("QtSDK", "Version")
        else:
            version = craftSettings.get("PortageVersions", "Qt5")
            if not version:
                CraftDebug.die("Please set a value for\n"
                                "[PortageVersions]\n"
                                "Qt5")
            version = "Qt_%s" % version
        return "/".join([craftSettings.get("ContinuousIntegration", "RepositoryUrl"), sys.platform, version,
                            compiler.getCompilerName(), self.buildType()])
