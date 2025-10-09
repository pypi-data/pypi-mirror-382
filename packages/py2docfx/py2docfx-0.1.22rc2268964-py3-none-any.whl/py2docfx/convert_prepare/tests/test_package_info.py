import os
import json

from py2docfx.convert_prepare.package_info import PackageInfo
from py2docfx.convert_prepare.source import Source

test_dict = dict()
param_case_dir = "convert_prepare/tests/data/params/"
full_test_file_path = os.path.join(param_case_dir, "test.json")

with open(full_test_file_path, "r", encoding="utf-8") as json_file:
    test_dict = json.load(json_file)
package_info_0 = PackageInfo.parse_from(test_dict["packages"][0], False)
package_info_0.code_location = "dummy_location"

package_info_1 = PackageInfo.parse_from(test_dict["packages"][1], False)

package_info_2 = PackageInfo.parse_from(test_dict["packages"][2], False)

package_info_3 = PackageInfo.parse_from(test_dict["packages"][3], False)

def test_parse_from():
    assert package_info_0.exclude_path == ["test*", "example*", "sample*", "doc*"]
    assert package_info_0.name == "azure-mltable-py2docfxtest"
    assert package_info_0.install_type.name == "PYPI"

def test_get_combined_name_version():
    name_version = package_info_1.get_combined_name_version()
    assert name_version == "azureml-accel-models==1.0.0"

def test_get_sphinx_extensions():
    assert package_info_3.sphinx_extensions == ["sphinx-pydantic"]
    assert package_info_3.name == "semantic-kernel"
    assert package_info_3.install_type.name == "PYPI"

def test_intall_command():
    install_command = package_info_0.get_install_command()
    assert install_command[0] == "azure-mltable-py2docfxtest"
    assert install_command[1] == ["--upgrade"]

    install_command = package_info_1.get_install_command()
    assert install_command[0] == "azureml-accel-models==1.0.0"
    assert install_command[1] == []

def test_get_exclude_command(tmp_path):
    source_folder = os.path.join(tmp_path,"source_folder")
    yaml_output_folder = os.path.join(tmp_path,"yaml_output_folder")
    package_info_0.path = Source(
        source_folder = source_folder, yaml_output_folder = yaml_output_folder, package_name = "azure-mltable-py2docfxtest"
    )
    exclude_path = package_info_0.get_exluded_command()
    expected_exclude_path = [
        "build/*",
        "setup.py",
        "test*",
        "example*",
        "sample*",
        "doc*",
        "azure/__init__.py",
        "azure/mltable/__init__.py"
    ]
    def form_exclude_path(raletive_path):
        return os.path.join(source_folder, raletive_path)
    assert exclude_path == [form_exclude_path(path) for path in expected_exclude_path]

def test_get_exclude_command_check_extra_exclude(tmp_path):
    source_folder = os.path.join(tmp_path,"source_folder")
    yaml_output_folder = os.path.join(tmp_path,"yaml_output_folder")
    package_info_2.path = Source(
        source_folder = source_folder, yaml_output_folder = yaml_output_folder, package_name = 'azure-core-tracing-opencensus'
    )
    exclude_path = package_info_2.get_exluded_command()
    expected_exclude_path = [
        "build/*",
        "setup.py",
        "azure/__init__.py",
        "azure/core/__init__.py",
        "azure/core/tracing/__init__.py",
        'azure/core/tracing/ext/__init__.py'
    ]
    def form_exclude_path(raletive_path):
        return os.path.join(source_folder, raletive_path)
    assert exclude_path == [form_exclude_path(path) for path in expected_exclude_path]


def test_get_combined_name_version_with_extras():
    """Test get_combined_name_version with extras"""
    # Test package with extras but no version
    test_data = {
        "package_info": {
            "install_type": "pypi",
            "name": "test-package",
            "extras": ["dev", "test"],
        },
    }
    pkg = PackageInfo.parse_from(test_data)
    assert pkg.get_combined_name_version() == "test-package[dev,test]"

    # Test package with extras and version
    test_data_with_version = {
        "package_info": {
            "install_type": "pypi",
            "name": "test-package",
            "version": "1.0.0",
            "extras": ["dev", "test"],
        },
    }
    pkg_with_version = PackageInfo.parse_from(test_data_with_version)
    assert (
        pkg_with_version.get_combined_name_version() == "test-package[dev,test]==1.0.0"
    )

    # Test package with extras and version operator
    test_data_with_operator = {
        "package_info": {
            "install_type": "pypi",
            "name": "test-package",
            "version": ">=1.0.0",
            "extras": ["dev"],
        },
    }
    pkg_with_operator = PackageInfo.parse_from(test_data_with_operator)
    assert pkg_with_operator.get_combined_name_version() == "test-package[dev]>=1.0.0"


def test_install_command_pypi_with_extras():
    """Test get_install_command for PYPI packages with extras"""
    # Test PYPI package with extras and version
    test_data = {
        "package_info": {
            "install_type": "pypi",
            "name": "test-package",
            "version": "1.0.0",
            "extras": ["dev", "test"],
        },
    }
    pkg = PackageInfo.parse_from(test_data)
    install_command = pkg.get_install_command()
    assert install_command[0] == "test-package[dev,test]==1.0.0"
    assert install_command[1] == []

    # Test PYPI package with extras but no version (should get --upgrade)
    test_data_no_version = {
        "package_info": {
            "install_type": "pypi",
            "name": "test-package",
            "extras": ["dev"],
        },
    }
    pkg_no_version = PackageInfo.parse_from(test_data_no_version)
    install_command = pkg_no_version.get_install_command()
    assert install_command[0] == "test-package[dev]"
    assert install_command[1] == ["--upgrade"]


def test_install_command_source_code_with_extras(tmp_path):
    """Test get_install_command for SOURCE_CODE packages with extras"""
    source_folder = os.path.join(tmp_path, "source_folder")
    yaml_output_folder = os.path.join(tmp_path, "yaml_output_folder")

    test_data = {
        "package_info": {
            "install_type": "source_code",
            "name": "test-package",
            "url": "https://github.com/test/test-package.git",
            "extras": ["dev", "test"],
        },
    }
    pkg = PackageInfo.parse_from(test_data)
    pkg.path = Source(
        source_folder=source_folder,
        yaml_output_folder=yaml_output_folder,
        package_name="test-package",
    )

    install_command = pkg.get_install_command()
    assert install_command[0] == f"{source_folder}[dev,test]"
    assert install_command[1] == []


def test_install_command_dist_file_with_extras():
    """Test get_install_command for DIST_FILE packages with extras"""
    test_data = {
        "package_info": {
            "install_type": "dist_file",
            "location": "/path/to/package.whl",
            "extras": ["dev"],
        },
    }
    pkg = PackageInfo.parse_from(test_data)
    install_command = pkg.get_install_command()
    assert install_command[0] == "/path/to/package.whl[dev]"
    assert install_command[1] == []


def test_install_command_without_extras():
    """Test that packages without extras work as before"""
    # Test PYPI package without extras
    test_data = {
        "package_info": {
            "install_type": "pypi",
            "name": "test-package",
            "version": "1.0.0",
        }
    }
    pkg = PackageInfo.parse_from(test_data)
    install_command = pkg.get_install_command()
    assert install_command[0] == "test-package==1.0.0"
    assert install_command[1] == []


def test_install_command_empty_extras():
    """Test that packages with empty extras list work correctly"""
    test_data = {
        "package_info": {
            "install_type": "pypi",
            "name": "test-package",
            "version": "1.0.0",
            "extras": [],
        },
    }
    pkg = PackageInfo.parse_from(test_data)
    install_command = pkg.get_install_command()
    assert install_command[0] == "test-package==1.0.0"
    assert install_command[1] == []


def test_install_command_single_extra():
    """Test package with single extra"""
    test_data = {
        "package_info": {
            "install_type": "pypi",
            "name": "test-package",
            "version": "1.0.0",
            "extras": ["dev"],
        },
    }
    pkg = PackageInfo.parse_from(test_data)
    install_command = pkg.get_install_command()
    assert install_command[0] == "test-package[dev]==1.0.0"
    assert install_command[1] == []
