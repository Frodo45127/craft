import info

class subinfo(info.infoclass):
    def setDependencies( self ):
        self.buildDependencies['virtual/base'] = 'default'
        self.dependencies['libs/qt'] = 'default'

    def setTargets( self ):
        self.svnTargets['gitHEAD'] = 'git://github.com/flavio/qjson.git'
        for ver in ['0.7.1','0.8.0','0.8.1']:
            self.targets[ ver ] = "http://downloads.sourceforge.net/qjson/qjson-" + ver + ".tar.bz2"
            self.targetInstSrc[ ver ] = "qjson-%s" % ver

        self.targetInstSrc[ '0.7.1' ] = "qjson"
        self.targetDigests['0.7.1'] = '19bbef24132b238e99744bb35194c6dadece98f9'
        self.patchToApply['0.7.1'] = ("qjson-20100517.diff", 1)
        self.targetDigests['0.8.1'] = '197ccfd533f17bcf40428e68a82e6622047ed4ab'
        self.shortDescription = "a qt-based library that maps JSON data to Qt objects"
        self.defaultTarget = '0.8.1'
        self.options.configure.defines = ""

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )

        self.subinfo.options.configure.defines = ""
        qmake = os.path.join(self.mergeDestinationDir(), "bin", "qmake.exe")
        if not os.path.exists(qmake):
            utils.warning("could not find qmake in <%s>" % qmake)
        ## \todo a standardized way to check if a package is installed in the image dir would be good.
        self.subinfo.options.configure.defines += "-DQT_QMAKE_EXECUTABLE:FILEPATH=%s " \
            % qmake.replace('\\', '/')

if __name__ == '__main__':
    Package().execute()
