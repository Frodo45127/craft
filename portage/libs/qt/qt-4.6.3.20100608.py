# -*- coding: utf-8 -*-
import base
import utils
from utils import die
import os
import info
import portage
import platform

from Package.QMakePackageBase import *

# ok we need something more here
# dbus-lib
# openssl-lib
# we can't use kde-root/include because we get conflicting includes then
# we have to make sure that the compiler picks up the correct ones!
# --> fetch the two libs above, unpack them into a separate folder

class subinfo(info.infoclass):
    def setTargets( self ):
        # the static version uses one of the stable versions
        self.svnTargets['static'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.5.2-patched|"
        # this is the upcoming 4.7 version with the KDE patches.
        self.svnTargets['master'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git"
        # this version contains the patches against the 4.5.3 release and is recommended for KDE 4.3.X
        self.svnTargets['4.5.3'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.5.3-patched|"
        # this branch contains all the patches and follows the 4.6-stable branch on qt.git - it updates daily
        self.svnTargets['4.6'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.6-stable-patched|"
        # those are the stable releases with the KDE patches applied on top
        self.svnTargets['4.6.0'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.6.0-patched|"
        self.svnTargets['4.6.1'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.6.1-patched|"
        self.svnTargets['4.6.2'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.6.2-patched|"
        self.svnTargets['4.6.3'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.6.3-patched|"
        self.svnTargets['4.7'] = "git://gitorious.org/qt/qt.git|4.7|"
        self.svnTargets['v4.7.0-beta1'] = "git://gitorious.org/qt/qt.git|4.7|v4.7.0-beta1|"
        self.targetSrcSuffix['4.7'] = "4.7"
        self.patchToApply['4.7'] = ('qt-4.7.0.patch', 1)
        self.patchToApply['v4.7.0-beta1'] = ('qt-4.7.0.patch', 1)
        
        if platform.isCrossCompilingEnabled() or ( platform.buildArchitecture() == 'x64' and COMPILER == "mingw4" ):
            if platform.isCrossCompilingEnabled():
                self.defaultTarget = 'v4.7.0-beta1'
            else:
                self.defaultTarget = '4.7'
        else:
            self.defaultTarget = '4.6.3'
        
        ## \todo this is prelimary  and may be changed 
        self.options.package.packageName = 'qt'
        self.options.package.specialMode = True

    def setDependencies( self ):
        self.hardDependencies['virtual/base'] = 'default'
        self.hardDependencies['dev-util/perl'] = 'default'
        self.hardDependencies['win32libs-bin/openssl'] = 'default'
        if COMPILER == 'msvc2008':
            self.hardDependencies['win32libs-sources/dbus-src'] = 'default'
        else:
            self.hardDependencies['win32libs-bin/dbus'] = 'default'
        if not platform.isCrossCompilingEnabled():
            self.hardDependencies['testing/mysql-pkg'] = 'default'

class Package(PackageBase,GitSource, QMakeBuildSystem, KDEWinPackager):
    def __init__( self, **args ):
        self.subinfo = subinfo()
        PackageBase.__init__(self)
        GitSource.__init__(self)
        QMakeBuildSystem.__init__(self)
        KDEWinPackager.__init__(self)
        # get instance of dbus and openssl package
        self.openssl = portage.getPackageInstance('win32libs-bin','openssl')
        if COMPILER == 'msvc2008':
            self.dbus = portage.getPackageInstance('win32libs-sources','dbus-src')
        else:
            self.dbus = portage.getPackageInstance('win32libs-bin','dbus')
        if not platform.isCrossCompilingEnabled():
            self.mysql_server = portage.getPackageInstance('testing','mysql-pkg')

    def configure( self, unused1=None, unused2=""):
        self.enterBuildDir()
        self.setPathes()

        xplatform = ""
        if self.isTargetBuild():
            if self.buildPlatform() == "WM60":
                xplatform = "wincewm60professional-%s" % self.compiler()
            elif self.buildPlatform() == "WM65":
                xplatform = "wincewm65professional-%s" % self.compiler()
            elif self.buildPlatform() == "WM50":
                xplatform = "wincewm50pocket-%s" % self.compiler()
            else:
                exit( 1 )

        os.environ[ "USERIN" ] = "y"
        userin = "y"

        incdirs = " -I \"" + os.path.join( self.dbus.installDir(), "include" ) + "\""
        libdirs = " -L \"" + os.path.join( self.dbus.installDir(), "lib" ) + "\""
        incdirs += " -I \"" + os.path.join( self.openssl.installDir(), "include" ) + "\""
        libdirs += " -L \"" + os.path.join( self.openssl.installDir(), "lib" ) + "\""
        if not platform.isCrossCompilingEnabled():
            incdirs += " -I \"" + os.path.join( self.mysql_server.installDir(), "include" ) + "\""
            libdirs += " -L \"" + os.path.join( self.mysql_server.installDir(), "lib" ) + "\""
            libdirs += " -l libmysql "
        
        configure = os.path.join( self.sourceDir(), "configure.exe" ).replace( "/", "\\" )
        
        command = r"echo %s | %s -opensource -prefix %s -platform %s " % ( userin, configure, self.installDir(), self.platform )
        if self.isTargetBuild():
            command += "-xplatform %s " % xplatform
            
        if self.isHostBuild():
            command += "-no-xmlpatterns "
        

        command += "-qt-gif -qt-libpng -qt-libjpeg -qt-libtiff -openssl-linked -webkit "
            
        if not platform.isCrossCompilingEnabled():
            # non-cc builds only
            command += "-plugin-sql-odbc "
            command += "-plugin-sql-mysql "
            command += "-qt-style-windowsxp "
            command += "-qt-style-windowsvista "
        # all builds
        command += "-no-phonon -qdbus -dbus-linked "
        command += "-fast -ltcg -no-vcproj -no-dsp "
        command += "-nomake demos -nomake examples -stl "
        command += "%s %s" % ( incdirs, libdirs )

        if self.buildType() == "Debug":
          command += " -debug "
        else:
          command += " -release "
        print "command: ", command
        utils.system( command )
        return True        
        
    def make(self, unused=''):        
        if self.isTargetBuild():
            self.setupTargetToolchain()
        
        QMakeBuildSystem.make(self)
        
        return True
      

    def install( self ):
        if self.isTargetBuild():
            # Configuring Qt for WinCE ignores the -prefix option,
            # so we have to do the job manually...
            
            # delete this because it is not working for windows
            utils.deleteFile( os.path.join( self.buildDir(), "plugin", "bearer", "qnmbearerd4.dll" ))
            utils.deleteFile( os.path.join( self.buildDir(), "plugin", "bearer", "qnmbearer4.dll" ))
            utils.copySrcDirToDestDir( os.path.join( self.buildDir(), "bin" ) , os.path.join( self.installDir(), "bin" ) )
            utils.copySrcDirToDestDir( os.path.join( self.buildDir(), "lib" ) , os.path.join( self.installDir(), "lib" ) )
            # headers need to be copied using syncqt because of the relative paths
            os.putenv( "PATH", os.path.join( self.sourceDir(), "bin" ) + ";" + os.getenv("PATH") )
            command = os.path.join(self.sourceDir(), "bin", "syncqt.bat")
            command += " -base-dir \"" + self.sourceDir() + "\""
            command += " -outdir \"" + self.installDir() + "\""
            command += " -copy"
            # 4.7 has a -quiet option, enable it when we switch
            #command += " -quiet"
            utils.system( command )
            # qconfig.h isn't copied by syncqt
            utils.copyFile( os.path.join( self.buildDir(), "src", "corelib", "global", "qconfig.h" ), os.path.join( self.installDir(), "include", "QtCore" , "qconfig.h" ) )
            utils.copySrcDirToDestDir( os.path.join( self.buildDir(), "mkspecs" ) , os.path.join( self.installDir(), "mkspecs" ) )
            utils.copySrcDirToDestDir( os.path.join( self.buildDir(), "plugins" ) , os.path.join( self.installDir(), "plugins" ) )
            # create qt.conf 
            utils.copyFile( os.path.join( self.packageDir(), "qt.conf" ), os.path.join( self.installDir(), "bin", "qt.conf" ) )
            return True

        if not QMakeBuildSystem.install(self):
            return False

        # create qt.conf 
        utils.copyFile( os.path.join( self.packageDir(), "qt.conf" ), os.path.join( self.installDir(), "bin", "qt.conf" ) )
        
        # install msvc debug files if available
        if self.buildType() == "Debug" and (self.compiler() == "msvc2005" or self.compiler() == "msvc2008"):
            srcdir = os.path.join( self.buildDir(), "lib" )
            destdir = os.path.join( self.installDir(), "lib" )

            filelist = os.listdir( srcdir )
            
            for file in filelist:
                if file.endswith( ".pdb" ):
                    utils.copyFile( os.path.join( srcdir, file ), os.path.join( destdir, file ) )
                
        return True

if __name__ == '__main__':
    Package().execute()
