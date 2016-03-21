from django.test import TestCase, override_settings
import kibali.models


REPO_DIR = 'test_repos'

@override_settings(KIBALI_REPO_BASE=REPO_DIR)
class PackageTests (TestCase):
    def setUp(self):
        from shutil import rmtree
        from os import makedirs
        rmtree(REPO_DIR, ignore_errors=True)
        makedirs(REPO_DIR)

    def test_package_init(self):
        package = kibali.models.Package.objects.create()
        package.init(data='{"hello":"world"}')

        from os.path import exists
        self.assertTrue(exists(package.repo))
