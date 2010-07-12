import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['svnHEAD'] = 'trunk/KDE/kdebase/runtime'
        if platform.isCrossCompilingEnabled():
            self.patchToApply['svnHEAD'] = ("kdebase-runtime-20100707.patch", 0)
        self.defaultTarget = 'svnHEAD'
    
    def setDependencies( self ):
        self.hardDependencies['kde/kdelibs'] = 'default'
        self.hardDependencies['kdesupport/oxygen-icons'] = 'default'
        if not platform.isCrossCompilingEnabled():
            self.hardDependencies['win32libs-sources/libssh-src'] = 'default'

from Package.CMakePackageBase import *
        
class Package(CMakePackageBase):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )
        self.subinfo.options.configure.defines = ""
        #FIXME: meinproc4 throughs an error, dont know really why
        if platform.isCrossCompilingEnabled():
            self.subinfo.options.configure.defines = "-DBUILD_doc=OFF "
        
        self.subinfo.options.configure.defines += "-DHOST_BINDIR=%s " \
            % os.path.join(ROOTDIR, "bin")

if __name__ == '__main__':
    Package().execute()
