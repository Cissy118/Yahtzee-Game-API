"""play.py - File for collecting functions for play the game."""
import random
# Category constants
ONES = 0
TWOS = 1
THREES = 2
FOURS = 3
FIVES = 4
SIXES = 5
UPPER_SCORE = 6
UPPER_BONUS = 7
THREE_OF_A_KIND = 8
FOUR_OF_A_KIND = 9
FULL_HOUSE = 10
SMALL_STRAIGHT = 11
LARGE_STRAIGHT = 12
YAHTZEE = 13
CHANCE = 14
LOWER_SCORE = 15
TOTAL = 16
TOTAL_DICE = 5

# ==============
# Find the score for each dice rolled
def find_score(dice, category):
	faces = [1, 2, 3, 4, 5, 6]
	# helper function
	def get_count(face):
		return dice.count(face)
	counts = map(get_count, faces)
	# Upper section
	if category in [ONES, TWOS, THREES, FOURS, FIVES, SIXES]:
		# The counted face value = category + 1 
		# Socre = count * face value
		return get_count(category + 1) * (category + 1)
	# Lower section
	# Three of a kind, Four of a kind, Yahtzee
	elif category in [THREE_OF_A_KIND, FOUR_OF_A_KIND, YAHTZEE]:
		if category is YAHTZEE:
			maxCounts = category - 8
			for face in faces:
				if get_count(face) >= maxCounts:
					return 50
		elif category is THREE_OF_A_KIND or category is FOUR_OF_A_KIND:
			maxCounts = category - 5
			for face in faces:
				if get_count(face) >= maxCounts :
					return sum(dice)
	# Full house
	elif category is FULL_HOUSE:
		# sort counts, check if it meets the full house pattern
		counts.sort()
		if counts == [0, 0, 0, 0, 2, 3]:  # validation
			return 25
	# Large straight
	elif category is LARGE_STRAIGHT:
		if counts == [0, 1, 1, 1, 1, 1] or counts == [1, 1, 1, 1, 1, 0]:
			return 40
	# Small straight
	elif category is SMALL_STRAIGHT:
		# convert counts to string, use substring to match the pattern
		countsStr = "".join(map(str, counts))
		if ("1111" in countsStr or "2111" in countsStr or 
			"1211" in countsStr or "1121" in countsStr or
			"1112" in countsStr):
			return 30
	# Chance
	elif category is CHANCE:
		return sum(dice)
	# Any pattern doesn't meet category
	return 0

# ==============
# Dice
def roll_dice(num):
	dice = []
	for i in range(num):
		dice.append(random.randint(1,6))
	return dice

def choose_dice(dice, index_choosed):
	dice_kept = []
	if not dice:
		return dice_kept
	# if any dice was choosed
	if index_choosed and len(index_choosed) is not TOTAL_DICE:
		for i in index_choosed:
			dice_kept.append(dice[i])
	return dice_kept

def roll(dice_kept):
	if not dice_kept:
		dice = roll_dice(TOTAL_DICE)
	else:
		num_dice = TOTAL_DICE - len(dice_kept)
		dice = dice_kept + roll_dice(num_dice)
	return dice









