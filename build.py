from pybuilder.core import use_plugin, init
from pybuilder.vcs import count_travis

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "zubmit"
default_task = "publish"
version = count_travis()


@init
def set_properties(project):
    project.depends_on('pony')
    project.depends_on('jinja2')
    project.depends_on('markdown')
    project.depends_on('weasyprint')
    project.depends_on('flask')
    project.depends_on('docopt')
    project.depends_on('python-dateutil')
    project.depends_on('requests')
    project.build_depends_on('splinter')
    project.set_property('coverage_break_build', False)
    project.package_data.update({'zubmit': 'templates/*'})
