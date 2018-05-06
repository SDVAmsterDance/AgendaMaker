from ftplib import FTP_TLS, error_perm
import exports.website.js_code_templates as templates




class Website(object):
    def __init__(self, server, port, path, user):
        # path = "/domains/sdvamsterdance.nl/public_html/wp-content/plugins/agendamaker/agenda/"
        # server = "ftp.sdvamsterdance.nl"
        # port = 21
        # user = "sandeue20"
        self.server = server
        self.port = int(port)
        self.dir = path
        self.user = user
        self.ftp = FTP_TLS(self.server)

    def _get_js_file(self, ftp_pass=""):
        filename = "main2.js"
        try:
            self.ftp.login(user=self.user, passwd=ftp_pass)
            self.ftp.cwd(dir)
            self.ftp.retrbinary("RETR " + filename, open(filename, 'wb').write)
        except error_perm as e:
            return str(e)

    def _upload_js_file(self, ftp_pass=""):
        filename = "main3.js"
        try:
            self.ftp.login(user=self.user, passwd=ftp_pass)
            self.ftp.cwd(dir)
            self.ftp.storbinary('STOR ' + filename, open(filename, 'rb'))
        except error_perm as e:
            return str(e)

    @staticmethod
    def _remove_cur_month(month_var, fname):
        new_file = ""
        with open(fname, 'r', encoding="utf8") as f:
            in_cur_month = False
            for line in f.readlines():
                if line.startswith("var {}".format(month_var)):
                    print(line)
                    in_cur_month = True
                    continue
                if line.startswith("var"):
                    in_cur_month = False
                if not in_cur_month:
                    new_file += line

        with open("main2.js", 'w') as f:
            f.write(new_file)

    def add_activities(self, month, year, activities, fname="main2.js", ftp_pass="", upload=False):
        nl_activities = activities['nl']
        en_activities = activities['en']
        complete_code = ""
        month_var, partial_code = templates.activity(month=month, year=year, activities=nl_activities)
        complete_code += partial_code + "\n"
        _, partial_code = templates.activity_home(month=month, year=year, activities=nl_activities)
        complete_code += partial_code + "\n"
        _, partial_code = templates.activity(month=month, year=year, activities=en_activities, lang="EN")
        complete_code += partial_code + "\n"
        _, partial_code = templates.activity_home(month=month, year=year, activities=en_activities, lang="EN")
        complete_code += partial_code

        resp = self._get_js_file(ftp_pass=ftp_pass)
        if resp:
            del ftp_pass
            return resp

        self._remove_cur_month(month_var, fname)

        with open(fname, "a") as f:
            f.write(complete_code)

        if upload:
            resp = self._upload_js_file(ftp_pass=ftp_pass)
            if resp:
                del ftp_pass
                return resp
        del ftp_pass
