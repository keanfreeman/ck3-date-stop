#!/usr/bin/env python3
"""Generates the Date Stop (CK3) mod files into ../mod. Run after editing."""
import os

N = 6  # alarm slots
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mod")
SG = "GuiScope.SetRoot( GetPlayer.MakeScope ).End"
slots = range(1, N + 1)

# (key, English text). Stored as flags (flag:<key>) on the character; text is DSC_REASON_<key>.
REASONS = [
    # Characters and family
    ("pregnancy", "Pregnancy due"), ("adulthood", "Child comes of age"), ("education", "Education ends"),
    ("marriage", "Marriage or wedding"), ("birthday", "Birthday"), ("succession", "Succession"),
    # Schemes, hooks, prisoners, factions
    ("scheme", "Scheme ready"), ("hook", "Hook expires"), ("prison", "Prison or ransom"),
    ("faction", "Faction threshold"), ("stress", "Stress or health"), ("inspiration", "Inspiration"),
    # War and movement
    ("truce", "Truce ends"), ("war", "War check"), ("siege", "Siege"), ("army", "Army or levies"),
    ("travel", "Travel arrives"), ("raid", "Raid"),
    # Activities
    ("feast", "Feast or festival"), ("tournament", "Tournament"), ("hunt", "Hunt"),
    ("pilgrimage", "Pilgrimage"), ("trip", "Tour or trip"), ("activity", "Activity ends"),
    # Realm management
    ("council", "Council task"), ("decision", "Decision ready"), ("building", "Construction"),
    ("project", "Great project"), ("tax", "Taxes or tribute"), ("gold", "Save up gold"),
    ("epidemic", "Epidemic"), ("struggle", "Struggle phase"),
    # Reminders
    ("inspect", "Check realm"), ("save", "Save the game"), ("rest", "Take a break"), ("other", "Other"),
]


def write(rel, text, bom=True):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8-sig" if bom else "utf-8") as f:
        f.write(text)


def any_slot(indent, fmt="has_variable = dsc_a{i}"):
    return "".join(f"{indent}{fmt.format(i=i)}\n" for i in slots)


# ---------------------------------------------------------------- effects
eff = """# Date Stop (CK3) - scripted effects. Root scope is the player character.
# State lives in character variables (the GUI can only read those):
#   dsc_py/pm/pd         date picker
#   dsc_aN, dsc_aN_y/m/d alarm slot N (key = year*10000 + month*100 + day)
#   dsc_ticking          the daily check event is scheduled
#   dsc_pause_pending    an alarm fired; the GUI pauses the game and clears it

dsc_today = {
	set_variable = { name = dsc_ty value = current_year }
	set_variable = { name = dsc_tm value = current_month }
	set_variable = { name = dsc_td value = current_day }
	set_variable = {
		name = dsc_tkey
		value = {
			value = current_year
			multiply = 10000
			add = { value = current_month multiply = 100 }
			add = current_day
		}
	}
}

dsc_dim = {
	set_variable = { name = dsc_dim value = 31 }
	if = {
		limit = { OR = { var:dsc_pm = 4 var:dsc_pm = 6 var:dsc_pm = 9 var:dsc_pm = 11 } }
		set_variable = { name = dsc_dim value = 30 }
	}
	if = {
		limit = { var:dsc_pm = 2 }
		set_variable = { name = dsc_dim value = 28 }
	}
}

# Carries month/day over and under their limits (CK3 has no leap days).
dsc_normalize = {
	while = {
		limit = { var:dsc_pm > 12 }
		change_variable = { name = dsc_pm subtract = 12 }
		change_variable = { name = dsc_py add = 1 }
	}
	while = {
		limit = { var:dsc_pm < 1 }
		change_variable = { name = dsc_pm add = 12 }
		change_variable = { name = dsc_py subtract = 1 }
	}
	dsc_dim = yes
	while = {
		limit = { var:dsc_pd > var:dsc_dim }
		change_variable = { name = dsc_pd subtract = var:dsc_dim }
		change_variable = { name = dsc_pm add = 1 }
		if = {
			limit = { var:dsc_pm > 12 }
			set_variable = { name = dsc_pm value = 1 }
			change_variable = { name = dsc_py add = 1 }
		}
		dsc_dim = yes
	}
	while = {
		limit = { var:dsc_pd < 1 }
		change_variable = { name = dsc_pm subtract = 1 }
		if = {
			limit = { var:dsc_pm < 1 }
			set_variable = { name = dsc_pm value = 12 }
			change_variable = { name = dsc_py subtract = 1 }
		}
		dsc_dim = yes
		change_variable = { name = dsc_pd add = var:dsc_dim }
	}
	if = {
		limit = { var:dsc_py < 1 }
		set_variable = { name = dsc_py value = 1 }
	}
}

dsc_pick_today = {
	dsc_today = yes
	set_variable = { name = dsc_py value = var:dsc_ty }
	set_variable = { name = dsc_pm value = var:dsc_tm }
	set_variable = { name = dsc_pd value = var:dsc_td }
}

# Panel opened: start the picker at today unless it was used already.
dsc_open = {
	if = {
		limit = { NOT = { has_variable = dsc_py } }
		dsc_pick_today = yes
	}
}

dsc_pick_add = {
	change_variable = { name = dsc_py add = $Y$ }
	change_variable = { name = dsc_pm add = $M$ }
	change_variable = { name = dsc_pd add = $D$ }
	dsc_normalize = yes
}

dsc_try_slot = {
	if = {
		limit = {
			NOT = { has_variable = dsc_added }
			NOT = { has_variable = dsc_a$N$ }
		}
		set_variable = { name = dsc_a$N$ value = var:dsc_key }
		set_variable = { name = dsc_a$N$_y value = var:dsc_py }
		set_variable = { name = dsc_a$N$_m value = var:dsc_pm }
		set_variable = { name = dsc_a$N$_d value = var:dsc_pd }
		if = {
			limit = { has_variable = dsc_pr }
			set_variable = { name = dsc_a$N$_r value = var:dsc_pr }
		}
		set_variable = dsc_added
	}
}

dsc_ensure_ticking = {
	if = {
		limit = { NOT = { has_variable = dsc_ticking } }
		set_variable = dsc_ticking
		trigger_event = { id = date_stop.1 days = 1 }
	}
}

dsc_add = {
	set_variable = {
		name = dsc_key
		value = {
			value = var:dsc_py
			multiply = 10000
			add = { value = var:dsc_pm multiply = 100 }
			add = var:dsc_pd
		}
	}
	remove_variable = dsc_added
"""
for i in slots:
    eff += f"\tdsc_try_slot = {{ N = {i} }}\n"
eff += """	remove_variable = dsc_added
	dsc_ensure_ticking = yes
}

dsc_remove_slot = {
	remove_variable = dsc_a$N$
	remove_variable = dsc_a$N$_y
	remove_variable = dsc_a$N$_m
	remove_variable = dsc_a$N$_d
	remove_variable = dsc_a$N$_r
}

dsc_clear_all = {
"""
for i in slots:
    eff += f"\tdsc_remove_slot = {{ N = {i} }}\n"
eff += """	remove_variable = dsc_pr
}

# Remembers the reason of a firing slot as dsc_fr_<key> so the popup can list it.
dsc_note_reason = {
"""
for k, _ in REASONS:
    eff += f"\tif = {{ limit = {{ var:dsc_a$N$_r ?= flag:{k} }} set_variable = dsc_fr_{k} }}\n"
eff += """}

# Fires every alarm that is due (key <= today's key).
dsc_fire_slot = {
	if = {
		limit = {
			has_variable = dsc_a$N$
			var:dsc_a$N$ <= var:dsc_tkey
		}
		dsc_note_reason = { N = $N$ }
		dsc_remove_slot = { N = $N$ }
		set_variable = dsc_fired
	}
}

dsc_fire_due = {
	remove_variable = dsc_fired
"""
for k, _ in REASONS:
    eff += f"\tremove_variable = dsc_fr_{k}\n"
for i in slots:
    eff += f"\tdsc_fire_slot = {{ N = {i} }}\n"
eff += """}

# Hands the alarms (and the daily check) from scope:dsc_from to this character.
dsc_copy_slot = {
	if = {
		limit = { scope:dsc_from = { has_variable = dsc_a$N$ } }
		set_variable = { name = dsc_a$N$ value = scope:dsc_from.var:dsc_a$N$ }
		set_variable = { name = dsc_a$N$_y value = scope:dsc_from.var:dsc_a$N$_y }
		set_variable = { name = dsc_a$N$_m value = scope:dsc_from.var:dsc_a$N$_m }
		set_variable = { name = dsc_a$N$_d value = scope:dsc_from.var:dsc_a$N$_d }
		if = {
			limit = { scope:dsc_from = { has_variable = dsc_a$N$_r } }
			set_variable = { name = dsc_a$N$_r value = scope:dsc_from.var:dsc_a$N$_r }
		}
	}
}

dsc_inherit_alarms = {
	if = {
		limit = { scope:dsc_from ?= { has_variable = dsc_ticking } }
"""
for i in slots:
    eff += f"\t\tdsc_copy_slot = {{ N = {i} }}\n"
eff += """		remove_variable = dsc_ticking
		dsc_ensure_ticking = yes
	}
}
"""
write("common/scripted_effects/dsc_effects.txt", eff)

# -------------------------------------------------------------- scripted guis
sg = """# Date Stop (CK3) - scripted GUIs. Called from gui/dsc_widget.gui with the player character as root.

dsc_open_sgui = {
	scope = character
	effect = { dsc_open = yes }
}

dsc_today_sgui = {
	scope = character
	effect = { dsc_pick_today = yes }
}

# "The picked date is in the future, an alarm slot is free and it isn't a duplicate."
dsc_add_sgui = {
	scope = character
	is_valid = {
		OR = {
			var:dsc_py > current_year
			AND = {
				var:dsc_py = current_year
				OR = {
					var:dsc_pm > current_month
					AND = { var:dsc_pm = current_month var:dsc_pd > current_day }
				}
			}
		}
		OR = {
""" + any_slot("\t\t\t", "NOT = {{ has_variable = dsc_a{i} }}") + "\t\t}\n"
for i in slots:
    sg += (
        f"\t\tNOT = {{ AND = {{ has_variable = dsc_a{i} var:dsc_a{i}_y = var:dsc_py "
        f"var:dsc_a{i}_m = var:dsc_pm var:dsc_a{i}_d = var:dsc_pd }} }}\n"
    )
sg += """	}
	effect = { dsc_add = yes }
}

dsc_clear_sgui = {
	scope = character
	is_shown = {
		OR = {
""" + any_slot("\t\t\t") + "\t\t\thas_variable = dsc_pr\n" + """		}
	}
	effect = { dsc_clear_all = yes }
}

dsc_has_any_sgui = {
	scope = character
	is_shown = {
		OR = {
""" + any_slot("\t\t\t") + """		}
	}
}

# is_shown = "an alarm fired and the GUI hasn't paused yet". The effect clears it.
dsc_pause_sgui = {
	scope = character
	is_shown = { has_variable = dsc_pause_pending }
	effect = { remove_variable = dsc_pause_pending }
}

"""
for i in slots:
    sg += f"""dsc_slot{i}_sgui = {{
	scope = character
	is_shown = {{ has_variable = dsc_a{i} }}
	effect = {{ dsc_remove_slot = {{ N = {i} }} }}
}}

"""
# stepper / quick-add buttons: id -> (Y, M, D)
steps = {
    "y_up1": (1, 0, 0), "y_dn1": (-1, 0, 0), "y_up10": (10, 0, 0), "y_dn10": (-10, 0, 0),
    "m_up1": (0, 1, 0), "m_dn1": (0, -1, 0),
    "d_up1": (0, 0, 1), "d_dn1": (0, 0, -1), "d_up5": (0, 0, 5), "d_dn5": (0, 0, -5),
    "add_1w": (0, 0, 7), "add_1m": (0, 1, 0), "add_3m": (0, 3, 0), "add_6m": (0, 6, 0),
    "add_1y": (1, 0, 0), "add_5y": (5, 0, 0), "add_10y": (10, 0, 0),
}
for k, (y, m, d) in steps.items():
    sg += f"""dsc_{k}_sgui = {{
	scope = character
	effect = {{ dsc_pick_add = {{ Y = {y} M = {m} D = {d} }} }}
}}

"""
sg += """dsc_reason_none_sgui = {
	scope = character
	effect = { remove_variable = dsc_pr }
}

dsc_has_reason_sgui = {
	scope = character
	is_shown = { has_variable = dsc_pr }
}

"""
for k, _ in REASONS:
    sg += f"""dsc_reason_{k}_sgui = {{
	scope = character
	effect = {{ set_variable = {{ name = dsc_pr value = flag:{k} }} }}
}}

"""
for i in slots:
    sg += f"""dsc_slot{i}_has_reason_sgui = {{
	scope = character
	is_shown = {{ has_variable = dsc_a{i}_r }}
}}

"""
write("common/scripted_guis/dsc_scripted_guis.txt", sg)


# ------------------------------------------------------------------- gui
def sbtn(name, text, tip=None, w=None):
    size = f" size = {{ {w} 24 }}" if w else ""
    t = f' tooltip = "{tip}"' if tip else ""
    return (
        f'button_standard = {{{size} text = "{text}"{t} '
        f"onclick = \"[GetScriptedGui('dsc_{name}_sgui').Execute( {SG} )]\" }}"
    )


def stepper(label, var, dn_big, dn, up, up_big):
    row = "\t\t\t\thbox = {\n\t\t\t\t\tspacing = 4\n"
    row += f'\t\t\t\t\ttext_single = {{ text = "{label}" min_width = 60 align = nobaseline }}\n'
    for n, t, w in ((dn_big, "DSC_DN_BIG", 36), (dn, "DSC_DN", 30)):
        if n:
            row += "\t\t\t\t\t" + sbtn(n, t, w=w) + "\n"
    row += (
        f"\t\t\t\t\ttext_single = {{ min_width = 56 align = center "
        f"text = \"[GetPlayer.MakeScope.Var('{var}').GetValue|0]\" }}\n"
    )
    for n, t, w in ((up, "DSC_UP", 30), (up_big, "DSC_UP_BIG", 36)):
        if n:
            row += "\t\t\t\t\t" + sbtn(n, t, w=w) + "\n"
    row += "\t\t\t\t}\n"
    return row


rows = ""
for i in slots:
    rows += f"""				hbox = {{
					visible = "[GetScriptedGui('dsc_slot{i}_sgui').IsShown( {SG} )]"
					spacing = 6
					text_single = {{
						min_width = 90
						text = "[GetPlayer.MakeScope.Var('dsc_a{i}_y').GetValue|0].[GetPlayer.MakeScope.Var('dsc_a{i}_m').GetValue|0].[GetPlayer.MakeScope.Var('dsc_a{i}_d').GetValue|0]"
					}}
					text_single = {{
						min_width = 190
						visible = "[GetScriptedGui('dsc_slot{i}_has_reason_sgui').IsShown( {SG} )]"
						text = "[Localize( Concatenate( 'DSC_REASON_', GetPlayer.MakeScope.Var('dsc_a{i}_r').GetFlagName ) )]"
					}}
					button_cancel_small = {{
						size = {{ 24 24 }}
						tooltip = "DSC_DELETE_TT"
						onclick = "[GetScriptedGui('dsc_slot{i}_sgui').Execute( {SG} )]"
					}}
				}}
"""

# Reason picker: 3 columns of buttons, left of the main panel.
cols = ""
per = (len(REASONS) + 2) // 3
for c in range(3):
    cols += "\t\t\t\tflowcontainer = {\n\t\t\t\t\tdirection = vertical\n\t\t\t\t\tspacing = 3\n"
    for k, _ in REASONS[c * per:(c + 1) * per]:
        cols += (
            f'\t\t\t\t\tbutton_standard = {{ size = {{ 124 24 }} text = "DSC_REASON_{k}" '
            f"onclick = \"[GetScriptedGui('dsc_reason_{k}_sgui').Execute( {SG} )]\" "
            f"onclick = \"[GetVariableSystem.Clear('dsc_reason_open')]\" }}\n"
        )
    cols += "\t\t\t\t}\n"
reason_panel = f"""
	### Reason picker, left of the main panel
	widget = {{
		name = "dsc_reason_panel"
		visible = "[And( GetVariableSystem.Exists('dsc_panel_open'), GetVariableSystem.Exists('dsc_reason_open') )]"
		parentanchor = bottom|right
		widgetanchor = bottom|right
		position = {{ -440 -70 }}
		size = {{ 400 100 }}
		filter_mouse = all
		alwaystransparent = no

		background = {{
			using = Background_Area_Border_Solid
			margin = {{ -10 -10 }}
		}}

		flowcontainer = {{
			direction = vertical
			resizeparent = yes
			margin = {{ 12 8 }}
			spacing = 6
			text_single = {{ text = "DSC_REASON_PICK" }}
			flowcontainer = {{
				direction = horizontal
				spacing = 4
{cols}			}}
		}}
	}}
"""

gui = f"""# Date Stop (CK3): a button at the bottom right opens a panel to set dates the game pauses on.
# Created at game start by gui/scripted_widgets/dsc_widgets.txt, so no vanilla file is replaced.

widget = {{
	name = "dsc_root"
	size = {{ 100% 100% }}
	layer = top
	alwaystransparent = yes
	visible = "[And( GetPlayer.IsValid, Not( IsPauseMenuShown ) )]"

	### Auto-pause. The daily event sets dsc_pause_pending when an alarm fires.
	widget = {{
		name = "dsc_autopause"
		size = {{ 1 1 }}
		alwaystransparent = yes

		state = {{
			name = dsc_do_pause
			trigger_when = "[And( And( GetScriptedGui('dsc_pause_sgui').IsShown( {SG} ), Not( IsGamePaused ) ), Not( GetVariableSystem.Exists('dsc_pausing') ) )]"
			duration = 0.01
			on_start = "[GetVariableSystem.Set('dsc_pausing', 'true')]"
			on_start = "[OnPause]"
			on_start = "[GetScriptedGui('dsc_pause_sgui').Execute( {SG} )]"
		}}
		state = {{
			name = dsc_clear_if_already_paused
			trigger_when = "[And( GetScriptedGui('dsc_pause_sgui').IsShown( {SG} ), IsGamePaused )]"
			duration = 0.01
			on_start = "[GetScriptedGui('dsc_pause_sgui').Execute( {SG} )]"
		}}
		state = {{
			name = dsc_reset_guard
			trigger_when = "[Not( GetScriptedGui('dsc_pause_sgui').IsShown( {SG} ) )]"
			duration = 0.01
			on_start = "[GetVariableSystem.Clear('dsc_pausing')]"
		}}
	}}

	### Icon in the time bar, left of the date. Adjust position x to move it.
	button_icon = {{
		name = "dsc_button"
		parentanchor = bottom|right
		position = {{ -420 1 }}
		size = {{ 32 32 }}
		texture = "gfx/interface/icons/flat_icons/time.dds"
		tooltip = "DSC_BUTTON_TT"
		using = tooltip_ne
		onclick = "[GetVariableSystem.Toggle('dsc_panel_open')]"
	}}

	### Panel
	widget = {{
		name = "dsc_panel"
		visible = "[GetVariableSystem.Exists('dsc_panel_open')]"
		parentanchor = bottom|right
		widgetanchor = bottom|right
		position = {{ -20 -70 }}
		size = {{ 400 100 }}
		filter_mouse = all
		alwaystransparent = no

		background = {{
			using = Background_Area_Border_Solid
			margin = {{ -10 -10 }}
		}}

		state = {{
			name = _show
			on_start = "[GetScriptedGui('dsc_open_sgui').Execute( {SG} )]"
		}}

		flowcontainer = {{
			direction = vertical
			resizeparent = yes
			ignoreinvisible = yes
			margin = {{ 15 0 }}
			margin_top = 10
			margin_bottom = 12
			minimumsize = {{ 370 -1 }}
			spacing = 6

			text_single = {{ text = "DSC_TITLE" }}
			text_single = {{ text = "DSC_TODAY" }}

			### Date picker
			vbox = {{
				spacing = 4
{stepper("DSC_YEAR", "dsc_py", "y_dn10", "y_dn1", "y_up1", "y_up10")}{stepper("DSC_MONTH", "dsc_pm", None, "m_dn1", "m_up1", None)}{stepper("DSC_DAY", "dsc_pd", "d_dn5", "d_dn1", "d_up1", "d_up5")}			}}

			text_single = {{ text = "DSC_QUICK" }}
			hbox = {{
				spacing = 4
				{sbtn("today", "DSC_TODAY_BTN", "DSC_TODAY_BTN_TT", 60)}
				{sbtn("add_1w", "DSC_1W", "DSC_ADD_TT", 44)}
				{sbtn("add_1m", "DSC_1M", "DSC_ADD_TT", 44)}
				{sbtn("add_3m", "DSC_3M", "DSC_ADD_TT", 44)}
				{sbtn("add_6m", "DSC_6M", "DSC_ADD_TT", 44)}
			}}
			hbox = {{
				spacing = 4
				{sbtn("add_1y", "DSC_1Y", "DSC_ADD_TT", 44)}
				{sbtn("add_5y", "DSC_5Y", "DSC_ADD_TT", 44)}
				{sbtn("add_10y", "DSC_10Y", "DSC_ADD_TT", 44)}
			}}

			### Reason
			hbox = {{
				spacing = 6
				text_single = {{ text = "DSC_REASON_LABEL" min_width = 60 align = nobaseline }}
				button_standard = {{
					size = {{ 230 24 }}
					tooltip = "DSC_REASON_TT"
					onclick = "[GetVariableSystem.Toggle('dsc_reason_open')]"
					text = "[SelectLocalization( GetScriptedGui('dsc_has_reason_sgui').IsShown( {SG} ), 'DSC_REASON_SHOWN', 'DSC_REASON_NONE' )]"
				}}
				button_cancel_small = {{
					size = {{ 24 24 }}
					tooltip = "DSC_REASON_CLEAR_TT"
					enabled = "[GetScriptedGui('dsc_has_reason_sgui').IsShown( {SG} )]"
					onclick = "[GetScriptedGui('dsc_reason_none_sgui').Execute( {SG} )]"
				}}
			}}

			### Actions
			hbox = {{
				spacing = 6
				button_standard = {{
					size = {{ 110 26 }}
					text = "DSC_SET"
					tooltip = "DSC_SET_TT"
					enabled = "[GetScriptedGui('dsc_add_sgui').IsValid( {SG} )]"
					onclick = "[GetScriptedGui('dsc_add_sgui').Execute( {SG} )]"
				}}
				button_standard = {{
					size = {{ 110 26 }}
					text = "DSC_CLEAR"
					tooltip = "DSC_CLEAR_TT"
					enabled = "[GetScriptedGui('dsc_clear_sgui').IsShown( {SG} )]"
					onclick = "[GetScriptedGui('dsc_clear_sgui').Execute( {SG} )]"
				}}
				button_standard = {{
					size = {{ 90 26 }}
					text = "DSC_CLOSE"
					onclick = "[GetVariableSystem.Clear('dsc_panel_open')]"
				}}
			}}

			### Alarm list
			text_single = {{
				visible = "[GetScriptedGui('dsc_has_any_sgui').IsShown( {SG} )]"
				text = "DSC_LIST_HEADER"
			}}
			text_single = {{
				visible = "[Not( GetScriptedGui('dsc_has_any_sgui').IsShown( {SG} ) )]"
				text = "DSC_LIST_EMPTY"
			}}
			vbox = {{
				spacing = 2
				ignoreinvisible = yes
{rows}			}}
		}}
	}}
{reason_panel}}}
"""
import re
# CK3 forbids hbox/vbox directly inside a flowcontainer, so use flowcontainers throughout.
gui = re.sub(r"(\t*)hbox = \{\n", lambda m: f"{m.group(1)}flowcontainer = {{\n{m.group(1)}\tdirection = horizontal\n", gui)
gui = re.sub(r"(\t*)vbox = \{\n", lambda m: f"{m.group(1)}flowcontainer = {{\n{m.group(1)}\tdirection = vertical\n", gui)
write("gui/dsc_widget.gui", gui)
write("gui/scripted_widgets/dsc_widgets.txt", "gui/dsc_widget.gui = dsc_root\n")

# ------------------------------------------------------------ events / hooks
ev = """namespace = date_stop

# Daily check on the player character. Reschedules itself every day while any alarm is queued.
# Duplicate chains (e.g. after a player change) merge: a second run on the same day stops.
date_stop.1 = {
	type = character_event
	hidden = yes

	immediate = {
		dsc_today = yes
		if = {
			limit = {
				OR = {
					NOT = { has_variable = dsc_last_tick }
					NOT = { var:dsc_last_tick = var:dsc_tkey }
				}
			}
			set_variable = { name = dsc_last_tick value = var:dsc_tkey }
			dsc_fire_due = yes
			if = {
				limit = { has_variable = dsc_fired }
				set_variable = dsc_pause_pending
				trigger_event = { id = date_stop.2 }
			}
			if = {
				limit = {
					OR = {
""" + any_slot("\t\t\t\t\t\t") + """					}
				}
				trigger_event = { id = date_stop.1 days = 1 }
			}
			else = {
				remove_variable = dsc_ticking
			}
		}
	}
}

# Popup: tells you the date arrived. The GUI widget does the pausing.
date_stop.2 = {
	type = character_event
	title = date_stop.2.t
	desc = {
		desc = date_stop.2.d
"""
for k, _ in REASONS:
    ev += f"\t\ttriggered_desc = {{ trigger = {{ has_variable = dsc_fr_{k} }} desc = DSC_REASON_LINE_{k} }}\n"
ev += """	}
	theme = default

	option = {
		name = date_stop.2.a
	}
}
"""
write("events/dsc_events.txt", ev)

write(
    "common/on_action/dsc_on_actions.txt",
    """# Alarms and the daily check follow the player to a new character (heir, character switch).
on_player_character_change = {
	effect = {
		scope:previous_player_character ?= { save_scope_as = dsc_from }
		dsc_inherit_alarms = yes
	}
}
""",
)

# ------------------------------------------------------------ localization
loc = """l_english:
 DSC_BUTTON:0 "Stop at date"
 DSC_BUTTON_TT:0 "Date Stop: choose dates for the game to pause on."
 DSC_TITLE:0 "#bold Date Stop#!"
 DSC_TODAY:0 "Today: [GetCurrentDate.GetString]"
 DSC_YEAR:0 "Year"
 DSC_MONTH:0 "Month"
 DSC_DAY:0 "Day"
 DSC_DN_BIG:0 "-"
 DSC_DN:0 "-"
 DSC_UP:0 "+"
 DSC_UP_BIG:0 "+"
 DSC_QUICK:0 "Add to the chosen date:"
 DSC_TODAY_BTN:0 "Today"
 DSC_TODAY_BTN_TT:0 "Reset the chosen date to today."
 DSC_ADD_TT:0 "Moves the chosen date forward. Click more than once to add up."
 DSC_1W:0 "+1w"
 DSC_1M:0 "+1m"
 DSC_3M:0 "+3m"
 DSC_6M:0 "+6m"
 DSC_1Y:0 "+1y"
 DSC_5Y:0 "+5y"
 DSC_10Y:0 "+10y"
 DSC_SET:0 "Set stop"
 DSC_SET_TT:0 "The game pauses when the chosen date arrives. It must be in the future and not already set. There can be 6 stops at most."
 DSC_CLEAR:0 "Clear all"
 DSC_CLEAR_TT:0 "Remove every stop."
 DSC_CLOSE:0 "Close"
 DSC_LIST_HEADER:0 "Stops (year.month.day):"
 DSC_LIST_EMPTY:0 "No stops set."
 DSC_REASON_LABEL:0 "Reason"
 DSC_REASON_NONE:0 "No reason (click to choose)"
 DSC_REASON_SHOWN:0 "[Localize( Concatenate( 'DSC_REASON_', GetPlayer.MakeScope.Var('dsc_pr').GetFlagName ) )]"
 DSC_REASON_TT:0 "Choose a reason to remind you why you set this stop."
 DSC_REASON_CLEAR_TT:0 "Clear the reason."
 DSC_REASON_PICK:0 "Choose a reason"
 DSC_DELETE_TT:0 "Remove this stop."
 date_stop.2.t:0 "Date Stop"
 date_stop.2.d:0 "The date you chose has arrived: [GetCurrentDate.GetString]."
 date_stop.2.a:0 "Continue"
"""
for k, t in REASONS:
    loc += f' DSC_REASON_{k}:0 "{t}"\n DSC_REASON_LINE_{k}:0 "\\n- {t}"\n'
write("localization/english/dsc_l_english.yml", loc)

write(
    ".metadata/metadata.json",
    """{
  "name": "Date Stop",
  "id": "date_stop_ck3",
  "version": "1.0.0",
  "supported_game_version": "1.20.*",
  "short_description": "A button at the bottom right: pick dates and the game pauses when each one arrives.",
  "tags": ["Utilities", "Interface"],
  "relationships": [],
  "game_custom_data": { "multiplayer_synchronized": true }
}
""",
    bom=False,
)
print("generated into", os.path.normpath(ROOT))
