import info
import kdedefaults as kd

class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['gitHEAD'] = '[git]kde:%s|%s|' % (self.package, kd.kdebranch)
        for ver in ['0', '1', '2', '3', '4', '5']:
            self.targets[kd.kdeversion + ver] = "http://download.kde.org/stable/" + kd.kdeversion + ver + "/src/" + self.package + "-" + kd.kdeversion + ver + ".tar.xz"
            self.targetInstSrc[kd.kdeversion + ver] = self.package + '-' + kd.kdeversion + ver

        self.patchToApply[ 'gitHEAD' ] = [("0004-listen-on-any-address-to-support-mapping-over-networ.patch_", 1)]
        self.patchToApply[ '4.10.0' ] = [("marble-4.10.0-20130301.diff", 1)]
        self.patchToApply[ '4.10.1' ] = [("marble-4.10.0-20130301.diff", 1)]
        self.shortDescription = 'the desktop globe'
        self.defaultTarget = 'gitHEAD'

    def setDependencies( self ):
        self.dependencies['kde/kde-runtime'] = 'default'
        self.buildDependencies['win32libs/nmealib'] = 'default'

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )

if __name__ == '__main__':
    Package().execute()
