from .podhub_info import PodHubInfo
from ...database.base import Database
from .app_package import AppPackage
from .app_package_changes import AppPackageChanges


class PodHubApplication:
    DB_CONNECTION:Database = None
    """Callback function for providing context manager with db_connection"""

    def __init__(self, **kwargs):
        self.application = kwargs.get('application')
        self.pip = PodHubInfo()
        self.current_pkgs = None
        self.last_changes = None
        self.codepoints = PodHubInfo(exp_req=50,exp_sec=50)
        self.db_connection = None

    def check_current_pkgs(self, latest:dict):
        if self.current_pkgs is None and PodHubApplication.DB_CONNECTION is not None:
            db = PodHubApplication.DB_CONNECTION
            self.current_pkgs = {}
            pkgs = AppPackage.find_all(db, application_name=self.application)
            if len(pkgs) == 0:
                for pkg_name, pkg_ver in latest.items():
                    package = AppPackage(application_name=self.application, pkg_name=pkg_name, version=pkg_ver)
                    package.insert(db)
                    self.current_pkgs[pkg_name] = [pkg_ver, package.id]
            else:
                for id, pkg_name, version in pkgs:
                    self.current_pkgs[pkg_name] = [version, id]

    def get_pkgs_differences(self, latest:dict):
        changes = []
        for oname, odata in  self.current_pkgs.items():
            over = odata[0]
            oid = odata[1]
            if oname in latest:
                if over != latest[oname]:
                    changes.append([oname, latest[oname], over, oid])
            else:
                changes.append([oname, None, over, oid])
        for nname, nver in latest.items():
            if nname not in self.current_pkgs:
                changes.append([nname, nver, None, None])
        return changes

    def save_pkg_differences(self, changes):
        db = PodHubApplication.DB_CONNECTION
        if db is None:
            return
        for pkg_name, new_ver, old_ver, old_id in changes:
            if new_ver is None:
                AppPackage.delete(db, id=old_id)
                del self.current_pkgs[pkg_name]
            elif old_ver is None:
                np = AppPackage(application_name=self.application, pkg_name=pkg_name, version=new_ver)
                np.insert(db)
                self.current_pkgs[pkg_name] = [new_ver, np.id]
            else:
                AppPackage.find_one(db, id=old_id).update(db, version=new_ver)
                prev = self.current_pkgs[pkg_name]
                self.current_pkgs[pkg_name] = [new_ver, prev[1]]

            AppPackageChanges(application_name=self.application, pkg_name=pkg_name,
                              new_version=new_ver, old_version=old_ver).insert(db)

    def get_changes(self):
        data = []
        db = PodHubApplication.DB_CONNECTION
        if db is None:
            return data
        last_dt = None
        for pkgc in AppPackageChanges.find(db, application_name=self.application, __order='created desc', __limit=200):
            pkgcc: AppPackageChanges = pkgc
            cd = pkgcc.created
            pkg_name = pkgcc.pkg_name
            over = pkgcc.old_version
            nver = pkgcc.new_version
            nldt = cd.strftime('%Y-%m-%d')
            if nldt == last_dt:
                nldt = ''
            else:
                last_dt = nldt
            if over is None:
                odt = f'NEW ({nver})'
            elif nver is None:
                odt = f'DELETED ({over})'
            else:
                odt = f'{over} {chr(8594)} {nver}'
            data.append({
                'date': nldt,
                'package': pkg_name,
                'change': odt
            })
        return data

