import unittest

from sapiopylib.rest.SesssionManagerService import SessionManager
from sapiopylib.rest.User import SapioUser

from sapiopylib.rest.DataMgmtService import DataMgmtServer

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="ae4e92e1-34c6-4336-8d80-7f6804d3e51c",
                 username="yqiao_api", password="Password1!")


class FR52531Test(unittest.TestCase):

    def test_session_kill(self):
        session_man: SessionManager = DataMgmtServer.get_session_manager(user)
        session_info_list = session_man.get_session_info_list()
        for session_info in session_info_list:
            if session_info.username != user.username:
                print("Killing session: " + str(session_info))
                session_man.kill_session(session_info.session_id)
