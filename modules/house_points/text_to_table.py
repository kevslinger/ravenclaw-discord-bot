from typing import Iterable


# Big thanks to Jonah Lawrence (DenverCoder1) for providing this code (slightly modified)
# https://github.com/DenverCoder1/professor-vector-discord-bot/blob/main/utils/text_to_table.py
class TextToTable:
	def __init__(
		self,
		header_row: Iterable[str],
		body: Iterable[Iterable[str]],
		footer_row: Iterable[str],
		activity_cell_width: int,
		score_cell_width: int,
	) -> None:
		self.header_row = header_row
		self.body = body
		self.footer_row = footer_row
		self.activity_cell_width = activity_cell_width
		self.score_cell_width = score_cell_width
		"""
		╔═════════════════╦═══════════════════════╗
		║   Activity      ║  G     H     R     S  ║
		╟─────────────────╫───────────────────────╢
		║  Arithmancy     ║  30    40    35    30 ║
		║  Challenge      ║  30    40    35    30 ║
		║  Dueling        ║  30    40    35    30 ║
		║  Extra Credit   ║  30    40    35    30 ║
		║  Fanworks       ║  30    40    35    30 ║
		║  Great Comment  ║  30    40    35    30 ║
		║  Homework       ║  30    40    35    30 ║
		║  House Contest  ║  30    40    35    30 ║
		║  Humor          ║  30    40    35    30 ║
		║  Quidditch      ║  30    40    35    30 ║	
		╟─────────────────╫───────────────────────╢
		║  Total          ║ 130   140   135   130 ║
		╚═════════════════╩═══════════════════════╝
		"""
		self.parts = {
			"top_left_corner": "╔",
			"top_right_corner": "╗",
			"top_edge": "═",
			"first_col_top_tee": "╦",
			"top_tee": "═",
			"left_edge": "║",
			"header_row_sep": "─",
			"footer_row_sep": "─",
			"first_col_sep": "║",
			"left_tee": "╟",
			"middle_edge": " ",
			"header_row_cross": "─",
			"footer_row_cross": "─",
			"first_col_cross": "╫",
			"right_edge": "║",
			"right_tee": "╢",
			"bottom_left_corner": "╚",
			"bottom_right_corner": "╝",
			"bottom_edge": "═",
			"first_col_bottom_tee": "╩",
			"bottom_tee": "═",
		}

	def tableize(self) -> str:
		cols = len(self.header_row)
		# create table header
		table = [
			# ╔
			self.parts["top_left_corner"]
			# ═════╦
			+ self.parts["top_edge"] * self.activity_cell_width + self.parts["first_col_top_tee"]
			#
			+ (
				(self.parts["top_edge"] * self.score_cell_width + self.parts["top_tee"])
				* (cols - 1)
			)[0:-1]
			# ╗
			+ self.parts["top_right_corner"],
			# ║
			self.parts["left_edge"]
			#  #  ║
			+ f"  {self.header_row[0].ljust(self.activity_cell_width-2)}" + self.parts["first_col_sep"]
			#    G     H     R     S
			+ self.parts["middle_edge"].join(
				" " * max(len(val) - 4, 4 - len(val)) + val + " " for val in self.header_row[1:]
			)
			# ║
			+ self.parts["right_edge"],
			# ╟
			self.parts["left_tee"]
			# ─────╫
			+ (
				(
					self.parts["header_row_sep"] * self.activity_cell_width
					+ self.parts["first_col_cross"]
				)
			)
			# ───────────────────────
			+ (
				(
					self.parts["header_row_sep"] * self.score_cell_width
					+ self.parts["header_row_cross"]
				)
				* (cols - 1)
			)[0:-1]
			# ╢
			+ self.parts["right_tee"],
		]
		# add table body
		for p in self.body:
			# add table row
			table += [
				# ║
				self.parts["left_edge"]
				+
				#  1  ║
				f"  {p[0].ljust(self.activity_cell_width-2)}"
				+ self.parts["first_col_sep"]
				#  40    40    40    40
				+ self.parts["middle_edge"].join(
					f"{p[i].rjust(self.score_cell_width - 1)} " for i in range(1, cols)
				)
				# ║
				+ self.parts["right_edge"]
			]
		# footer row
		if self.footer_row:
			table += [
				# ╟
				self.parts["left_tee"]
				# ─────╫
				+ (
					(
						self.parts["footer_row_sep"] * self.activity_cell_width
						+ self.parts["first_col_cross"]
					)
				)
				# ───────────────────────
				+ (
					(
						self.parts["footer_row_sep"] * self.score_cell_width
						+ self.parts["footer_row_cross"]
					)
					* (cols - 1)
				)[0:-1]
				# ╢
				+ self.parts["right_tee"],
				# ║
				self.parts["left_edge"]
				#  SUM ║
				+ f"  {self.footer_row[0].ljust(self.activity_cell_width-2)}" + self.parts["first_col_sep"]
				#  120 ║ 120 ║ 120 ║ 120 ║
				+ self.parts["middle_edge"].join(
					f"{self.footer_row[i].rjust(self.score_cell_width - 1)} " for i in range(1, cols)
				)
				# ║
				+ self.parts["right_edge"]
			]
		table += [
			# ╚
			self.parts["bottom_left_corner"]
			# ═════╩
			+ self.parts["bottom_edge"] * self.activity_cell_width
			+ self.parts["first_col_bottom_tee"]
			# ════════════════════════
			+ (
				(self.parts["bottom_edge"] * self.score_cell_width + self.parts["bottom_tee"])
				* (cols - 1)
			)[0:-1]
			# ╗
			+ self.parts["bottom_right_corner"],
		]
		return "\n".join(table)