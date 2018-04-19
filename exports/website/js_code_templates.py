from translatables.month import Maand


def prev_month(month, year):
    if month == 1:
        year -= 1
    month -= 1
    month = (month % 12)
    if not month:
        month = 12
    return month, year


def next_month(month, year):
    if month == 12:
        year += 1
    month += 1
    month = month % 12
    if not month:
        month = 12
    return month, year


def activity(month, year, activities, lang=""):
    month_var = "{}{}{}".format(Maand(month).name, year, lang)
    p_month, p_year = prev_month(month, year)
    prev_month_var = "{}{}".format(Maand(p_month).name, p_year)
    n_month, n_year = next_month(month, year)
    next_month_var = "{}{}".format(Maand(n_month).name, n_year)
    js_code = "var {0} = '<div id=\"{0}\">' +\n"
    js_code += "'<img id=\"agendaImage\" src=\"' + agsrs + '{0}{3}.gif\" width=\"877px\" height=\"620px\" alt=\"Agenda\" usemap=\"#{0}map\">' +\n"
    js_code += "'<img id=\"agendaOverlay\" src=\"' + agsrs + 'overlay.gif\" usemap=\"#{0}map\">' +\n"
    js_code += "'<map name=\"{0}map\">' +\n"
    js_code += "'<area class=\"date\" shape=\"poly\" coords=\"0,0,80,0,80,620,0,620\" alt=\"date\" onmousemove=\"show(\\'left\\',event,\\'{1}\\')\" onmouseout=\"hide();\" onmousedown=\"myfun2(\\'{1}\\')\"/>' +\n"
    js_code += "'<area class=\"date\" shape=\"poly\" coords=\"797,0,877,0,877,620\" alt=\"date\" onmousemove=\"show(\\'right\\',event,\\'{2}\\')\" onmouseout=\"hide();\" onmousedown=\"myfun2(\\'{2}\\')\"/>' +\n"
    js_code += _activities_code(activities=activities)
    js_code += "'</map></div>';"
    js_code = js_code.format(month_var, prev_month_var, next_month_var, lang)
    return month_var, js_code


def activity_home(month, year, activities, lang=""):
    month_var = "{}{}home{}".format(Maand(month).name, year, lang)
    p_month, p_year = prev_month(month, year)
    prev_month_var = "{}{}".format(Maand(p_month).name, p_year)
    n_month, n_year = next_month(month, year)
    next_month_var = "{}{}".format(Maand(n_month).name, n_year)
    js_code = "var {0} = '<div id=\"{0}\">' +\n"
    js_code += "'<a href=\"/activiteiten#agendaImage\">'+\n"
    js_code += "'<img id=\"agendaImage\" src=\"'+agsrs+'{0}{3}.gif\"  width=\"877px\" height=\"620px\" alt=\"Agenda\" usemap=\"#{0}map\">'+\n"
    js_code += "'<img id=\"agendaOverlay\" src=\"'+agsrs+'overlay.gif\" usemap=\"#{0}map\">'+\n"
    js_code += "'<map name=\"{0}map\">'+\n"
    js_code += "'<area class=\"date\" shape=\"poly\" coords=\"0,0,80,0,80,620,0,620\" alt=\"date\" onmousemove=\"show(\\'left\\',event,\\'{1}\\')\" onmouseout=\"hide();\" onmousedown=\"myfun2(\\'{1}\\')\"/>'+\n"
    js_code += "'<area class=\"date\" shape=\"poly\" coords=\"797,0,877,0,877,620\" alt=\"date\" onmousemove=\"show(\\'right\\',event,\\'{2}\\')\" onmouseout=\"hide();\" onmousedown=\"myfun2(\\'{2}\\')\"/>'+\n"
    js_code += _activities_code_home(activities=activities)
    js_code += "'</map></a></div>';"
    js_code = js_code.format(month_var, prev_month_var, next_month_var,lang)
    return month_var, js_code


def _activities_code(activities):
    code = ""
    area = "'<area class=\"date\" shape=\"poly\" coords=\"{}\" alt=\"date\" href=\"\"" \
           "onmousemove=\"show(\\'{}\\', event,\\'{}\\');\" onmouseout=\"hide();\" >' +\n"
    for act in activities:
        code += area.format(",".join([str(c) for c in act['coords']]), act['direction'],
                            act['description'])
    return code


def _activities_code_home(activities):
    code = ""
    area = "'<area class=\"date\" shape=\"poly\" coords=\"{}\" alt=\"date\" " \
           "onmousemove=\"show(\\'{}\\', event,\\'{}\\');\" onmouseout=\"hide();\" >' +\n"
    for act in activities:
        description = "<p><b>{}: {}</b><br/><em>{}: {}<br/>{}: {}-{}<br/></em><p>{}".format(act['date'],
                                                                                            act['name'],
                                                                                            "Locatie",
                                                                                            act['location'],
                                                                                            "Tijd",
                                                                                            act['begin_time'],
                                                                                            act['end_time'],
                                                                                            act['description'])
        code += area.format(",".join([str(c) for c in act['coords']]),
                            act['direction'],
                            description)
    return code
