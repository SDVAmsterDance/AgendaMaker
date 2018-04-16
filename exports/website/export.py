from ftplib import FTP_TLS
import exports.website.js_code_templates as templates

dir = "/domains/sdvamsterdance.nl/public_html/wp-content/plugins/agendamaker/agenda/"
server = "ftp.sdvamsterdance.nl"
port = 21
user = "sandeue20"


def _get_js_file():
    filename = "main2.js"
    ftp = FTP_TLS(server)
    pw = "dansdetango22bier77brood"
    ftp.login(user=user, passwd=pw)
    ftp.cwd(dir)
    ftp.retrbinary("RETR " + filename, open(filename, 'wb').write)


def add_activities(month, year, activities, fname="main2.js"):
    month_var, code = templates.default(month=month, year=year, activities=activities)
    _get_js_file()
    _remove_cur_month(month_var, fname)

    with open(fname, "a") as f:
        f.write(code)


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



