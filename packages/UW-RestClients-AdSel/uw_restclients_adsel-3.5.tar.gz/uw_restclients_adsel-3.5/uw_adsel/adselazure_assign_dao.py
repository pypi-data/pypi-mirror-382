"""
Contains UW AdSEL Azure Assign DAO implementations.
"""
from restclients_core.dao import DAO
from os.path import abspath, dirname
import os


class ADSEL_AZURE_ASSIGN_DAO(DAO):
    def service_name(self):
        return 'adsel_azure_assign'

    def service_mock_paths(self):
        path = [abspath(os.path.join(dirname(__file__), "resources"))]
        return path
