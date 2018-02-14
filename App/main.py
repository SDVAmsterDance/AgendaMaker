# Add paths to Python Path
import sys

from agenda.draw.draw_agenda import DrawAgenda
from agenda.draw.draw_flyer import DrawFlyer

sys.path.append('../')

internal_activities = set([x.strip() for x in ",sfeablf370g74009oau35jte18@group.calendar.google.com,p68brdnv6bp4q8qu0g8o1gv914@group.calendar.google.com,sdv.amsterdance@gmail.com".split(",")])
external_activities = set([x.strip() for x in ",k37nshvnqob4c484497713cboc@group.calendar.google.com".split(",")])

draw = DrawFlyer(2, 2018,internal_activities ,external_activities )

draw.draw_agenda()

# draw = DrawAgenda(2, 2018,internal_activities ,external_activities )
# draw.draw_agenda()
