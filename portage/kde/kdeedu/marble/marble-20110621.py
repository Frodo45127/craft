import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['gitHEAD'] = '[git]kde:marble|KDE/4.8|'
        for ver in ['0', '1', '2', '3', '4']:
            self.targets['4.8.' + ver] = "ftp://ftp.kde.org/pub/kde/stable/4.8." + ver + "/src/marble-4.8." + ver + ".tar.bz2"
            self.targetInstSrc['4.8.' + ver] = 'marble-4.8.' + ver
        self.patchToApply['4.8.0'] = [("marble-4.8.0-20120125.diff", 1),
                                      # TODO: not tested yet
                                      #("0001-first-version-of-flightgear-position-provider-plugin.patch_", 1),
                                      #("0002-4.8-branch-do-not-have-PluginAuthor-disabled-related.patch_", 1),
                                      #("0003-compile-fix.patch_", 1),
                                      #("0004-listen-on-any-address-to-support-mapping-over-networ.patch_", 1),
                                     ]
        self.patchToApply[ 'gitHEAD' ] = [("marble-4.8.0-20120125.diff", 1),
                                          ("0001-first-version-of-flightgear-position-provider-plugin.patch_", 1),
                                          ("0002-4.8-branch-do-not-have-PluginAuthor-disabled-related.patch_", 1),
                                          ("0003-compile-fix.patch_", 1),
                                          ("0004-listen-on-any-address-to-support-mapping-over-networ.patch_", 1),
                                         ]
        self.shortDescription = 'the desktop globe'
        self.defaultTarget = 'gitHEAD'

    def setDependencies( self ):
        self.dependencies['kde/kde-runtime'] = 'default'
        # TODO: how to limit to gitHEAD for now
        self.buildDependencies['win32libs-sources/nmealib-src'] = 'default'

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )

if __name__ == '__main__':
    Package().execute()
