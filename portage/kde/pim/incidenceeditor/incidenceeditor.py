import info


class subinfo(info.infoclass):
    def setTargets(self):
        self.versionInfo.setDefaultValues()

        self.shortDescription = "IncidenceEditor library"

    def setDependencies(self):
        self.runtimeDependencies["virtual/base"] = "default"
        self.buildDependencies["frameworks/extra-cmake-modules"] = "master"
        self.runtimeDependencies["libs/qtbase"] = "default"
        self.runtimeDependencies["frameworks/ki18n"] = "default"
        self.runtimeDependencies["frameworks/kcodecs"] = "default"
        self.runtimeDependencies["kde/kmime"] = "default"
        self.runtimeDependencies["kde/akonadi"] = "default"
        self.runtimeDependencies["kde/akonadi-mime"] = "default"
        self.runtimeDependencies["kde/kldap"] = "default"
        self.runtimeDependencies["kde/calendarsupport"] = "default"
        self.runtimeDependencies["kde/eventviews"] = "default"
        self.runtimeDependencies["kde/kcalutils"] = "default"
        self.runtimeDependencies["kde/kcalcore"] = "default"
        self.runtimeDependencies["kde/kmailtransport"] = "default"


from Package.CMakePackageBase import *


class Package(CMakePackageBase):
    def __init__(self):
        CMakePackageBase.__init__(self)
