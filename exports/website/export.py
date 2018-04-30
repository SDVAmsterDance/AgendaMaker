from ftplib import FTP_TLS
import exports.website.js_code_templates as templates

dir = "/domains/sdvamsterdance.nl/public_html/wp-content/plugins/agendamaker/agenda/"
server = "ftp.sdvamsterdance.nl"
port = 21
user = "sandeue20"


def _get_js_file(ftp_pass=""):
    filename = "main2.js"
    ftp = FTP_TLS(server)
    ftp.login(user=user, passwd=ftp_pass)
    ftp.cwd(dir)
    ftp.retrbinary("RETR " + filename, open(filename, 'wb').write)


def _upload_js_file(ftp_pass=""):
    filename = "main3.js"
    ftp = FTP_TLS(server)
    ftp.login(user=user, passwd=ftp_pass)
    ftp.cwd(dir)
    ftp.storbinary('STOR ' + filename, open(filename, 'rb'))


def add_activities(month, year, activities, fname="main2.js", ftp_pass=""):
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

    _get_js_file(ftp_pass=ftp_pass)
    _remove_cur_month(month_var, fname)

    with open(fname, "a") as f:
        f.write(complete_code)

    _upload_js_file(ftp_pass=ftp_pass)
    del ftp_pass


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
