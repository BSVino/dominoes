import random

random.seed()

def make_deck():
	deck = []

	for i in range(0, 10):
		for j in range(0, i+1):
			deck.append([i,j])

	return deck

def shuffle_deck(deck):
	random.shuffle(deck)
	return deck

table_left = -1
table_right = -1

table_left_player = -1
table_right_player = -1

team_13_wins = 0
team_24_wins = 0

debug_print = False

player_has = []

def show_table():
	global table_left, table_right

	if debug_print:
		print (" [%d | ...] ... [... | %d]" % (table_left, table_right))

def get_partner(player):
	if player is 0:
		return 2
	if player is 1:
		return 3
	if player is 2:
		return 0
	if player is 3:
		return 1
	Error()

def chip_playable(hand, index, left):
	global table_left, table_right, table_right_player, table_left_player

	if hand[index][0] is table_left and left:
		return True

	if hand[index][1] is table_left and left:
		return True

	if hand[index][0] is table_right and not left:
		return True

	if hand[index][1] is table_right and not left:
		return True

	return False


# Use the opening strategy of playing the highest value chip
def open_highest(hand_index):
	global deck, table_left, table_right, player_hands, table_right_player, table_left_player

	hand = player_hands[hand_index]

	highest = -1
	highest_index = -1
	for i in range(0, 10):
		if hand[i][0] + hand[i][1] > highest:
			highest = hand[i][0] + hand[i][1]
			highest_index = i

	if debug_print:
		print ("Player %d opens with [%d | %d] (strategy: highest)" % (hand_index+1, hand[highest_index][0], hand[highest_index][1]))

	table_left = hand[highest_index][0]
	table_right = hand[highest_index][1]
	table_left_player = table_right_player = hand_index
	del hand[highest_index]

def play_chip(hand, index, player):
	global table_left, table_right, table_right_player, table_left_player

	if hand[index][0] is table_left:
		table_left = hand[index][1]
		table_left_player = player
		del hand[index]
		return hand

	if hand[index][1] is table_left:
		table_left = hand[index][0]
		table_left_player = player
		del hand[index]
		return hand

	if hand[index][0] is table_right:
		table_right = hand[index][1]
		table_right_player = player
		del hand[index]
		return hand

	if hand[index][1] is table_right:
		table_right = hand[index][0]
		table_right_player = player
		del hand[index]
		return hand


# Use the strategy of playing the first chip you find in the deck
def play_first(hand_index):
	global deck, table_left, table_right, player_hands

	hand = player_hands[hand_index]

	if table_left is -1:
		open_highest(hand_index)
		return False

	for i in range(0, len(hand)):
		if hand[i][0] is table_left:
			if debug_print:
				print ("Player %d plays [%d | %d] (strategy: first)" % (hand_index+1, hand[i][0], hand[i][1]))
			hand = play_chip(hand, i, hand_index)
			return False

		if hand[i][1] is table_left:
			if debug_print:
				print ("Player %d plays [%d | %d] (strategy: first)" % (hand_index+1, hand[i][0], hand[i][1]))
			hand = play_chip(hand, i, hand_index)
			return False

		if hand[i][0] is table_right:
			if debug_print:
				print ("Player %d plays [%d | %d] (strategy: first)" % (hand_index+1, hand[i][0], hand[i][1]))
			hand = play_chip(hand, i, hand_index)
			return False

		if hand[i][1] is table_right:
			if debug_print:
				print ("Player %d plays [%d | %d] (strategy: first)" % (hand_index+1, hand[i][0], hand[i][1]))
			hand = play_chip(hand, i, hand_index)
			return False

	if debug_print:
		print ("Player %d knocks." % (hand_index+1))
	return True



# Use the strategy of playing the highest value chip that matches
def play_highest(hand_index):
	global deck, table_left, table_right, player_hands

	hand = player_hands[hand_index]

	if table_left is -1:
		open_highest(hand_index)
		return False

	highest = -1
	highest_index = -1
	for i in range(0, len(hand)):
		if hand[i][0] + hand[i][1] < highest:
			continue

		if hand[i][0] is table_left:
			highest = hand[i][0] + hand[i][1]
			highest_index = i
			continue

		if hand[i][1] is table_left:
			highest = hand[i][0] + hand[i][1]
			highest_index = i
			continue

		if hand[i][0] is table_right:
			highest = hand[i][0] + hand[i][1]
			highest_index = i
			continue

		if hand[i][1] is table_right:
			highest = hand[i][0] + hand[i][1]
			highest_index = i
			continue

	if highest_index is -1:
		if debug_print:
			print ("Player %d knocks." % (hand_index+1))
		return True

	if debug_print:
		print ("Player %d plays [%d | %d] (strategy: highest)" % (hand_index+1, hand[highest_index][0], hand[highest_index][1]))
	hand = play_chip(hand, highest_index, hand_index)

	return False



def play_better(hand_index):
	global deck, table_left, table_right, table_left_player, table_right_player, player_hands, player_has

	hand = player_hands[hand_index]

	if table_left is -1:
		open_highest(hand_index)
		return False

	my_numbers = []
	for i in range(0, 10):
		my_numbers.append(0)

	for i in range(0, len(hand)):
		my_numbers[hand[i][0]] += 1
		my_numbers[hand[i][1]] += 1

	available_chips = []  # : id -> hand[id]

	for i in range(0, len(hand)):
		if hand[i][0] is table_left:
			available_chips.append(i)
			continue

		if hand[i][1] is table_left:
			available_chips.append(i)
			continue

		if hand[i][0] is table_right:
			available_chips.append(i)
			continue

		if hand[i][1] is table_right:
			available_chips.append(i)
			continue

	if not len(available_chips):
		return True

	# Don't play on your partner's chips
	# Play chips similar to your other chips
	# Try to play chips the next person doesn't have
	# Play your higher chips first (Prefer higher numbers to higher sums)
	# Try to close numbers your partner doesn't have

	chip_scores = []
	for i in range(0, len(available_chips)):
		chip_scores.append([0, 0])

	for i in range(0, len(available_chips)):
		# If it's a double then it won't kill my partner's chips
		if hand[available_chips[i]][0] == hand[available_chips[i]][1]:
			continue

		if hand[available_chips[i]][0] == table_left and table_left_player is get_partner(hand_index):
			chip_scores[i][0] -= 5
		if hand[available_chips[i]][1] == table_left and table_left_player is get_partner(hand_index):
			chip_scores[i][1] -= 5
		if hand[available_chips[i]][0] == table_right and table_right_player is get_partner(hand_index):
			chip_scores[i][0] -= 5
		if hand[available_chips[i]][1] == table_right and table_right_player is get_partner(hand_index):
			chip_scores[i][1] -= 5

	for i in range(0, len(available_chips)):
		chip_scores[i][0] += my_numbers[i]
		chip_scores[i][1] += my_numbers[i]

	next_player = (hand_index+1)%4
	for i in range(0, len(available_chips)):
		if hand[available_chips[i]][0] == table_left and hand[available_chips[i]][1] not in player_has[next_player]:
			chip_scores[i][0] += 5
		if hand[available_chips[i]][1] == table_left and hand[available_chips[i]][1] not in player_has[next_player]:
			chip_scores[i][1] += 5
		if hand[available_chips[i]][0] == table_right and hand[available_chips[i]][1] not in player_has[next_player]:
			chip_scores[i][0] += 5
		if hand[available_chips[i]][1] == table_right and hand[available_chips[i]][1] not in player_has[next_player]:
			chip_scores[i][1] += 5

	for i in range(0, len(available_chips)):
		chip_scores[i][0] += hand[available_chips[i]][0]*hand[available_chips[i]][0]/25
		chip_scores[i][0] += hand[available_chips[i]][1]*hand[available_chips[i]][1]/25
		chip_scores[i][1] += hand[available_chips[i]][0]*hand[available_chips[i]][0]/25
		chip_scores[i][1] += hand[available_chips[i]][1]*hand[available_chips[i]][1]/25

	best_play = -1
	best_score = -99999
	for i in range(0, len(available_chips)):
		if chip_scores[i][0] > best_score and chip_playable(hand, available_chips[i], True):
			best_score = chip_scores[i][0]
			best_play = available_chips[i]
		elif chip_scores[i][1] > best_score and chip_playable(hand, available_chips[i], False):
			best_score = chip_scores[i][0]
			best_play = available_chips[i]

	if best_play < 0:
		Error()

	#print (hand)
	#print (available_chips)
	#print (chip_scores)
	#print (best_play)
	if debug_print:
		print ("Player %d plays [%d | %d] (strategy: better)" % (hand_index+1, hand[best_play][0], hand[best_play][1]))
	play_chip(hand, best_play, hand_index)

	return False


def play_game(team_13_strategy, team_24_strategy, starter):
	global deck, table_left, table_right, player_hands, team_13_wins, team_24_wins, player_has

	deck = make_deck()
	deck = shuffle_deck(deck)

	player_hands = [[], [], [], []]

	player_has = []
	player_has.append([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
	player_has.append([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
	player_has.append([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
	player_has.append([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

	for i in range(0, 10):
		player_hands[0].append(deck[-1])
		deck.pop()

		player_hands[1].append(deck[-1])
		deck.pop()

		player_hands[2].append(deck[-1])
		deck.pop()

		player_hands[3].append(deck[-1])
		deck.pop()

	if debug_print:
		print (player_hands[0])
		print (player_hands[1])
		print (player_hands[2])
		print (player_hands[3])

	knocks = 0
	turn = starter
	while True:
		player_hand = turn%4
		if turn%2 == 0:
			knock = team_13_strategy(player_hand)
			if knock:
				knocks += 1

				if table_left in player_has[player_hand]:
					player_has[player_hand].remove(table_left)
				if table_right in player_has[player_hand]:
					player_has[player_hand].remove(table_right)
		else:
			knock = team_24_strategy(player_hand)
			if knock:
				knocks += 1

				if table_left in player_has[player_hand]:
					player_has[player_hand].remove(table_left)
				if table_right in player_has[player_hand]:
					player_has[player_hand].remove(table_right)

		show_table()

		if len(player_hands[player_hand]) == 0:
			if debug_print:
				print ("Player %d out of chips. Team %d/%d wins."%(player_hand, turn%2, turn%2+1))

			if turn%2 is 0:
				team_13_wins += 1
			else:
				team_24_wins += 1
			break

		turn += 1

		if knocks is 4:
			if debug_print:
				print ("All players knock, game over.")

				print(player_hands[0])
				print(player_hands[1])
				print(player_hands[2])
				print(player_hands[3])

			team_13_score = 0

			for i in range(0, len(player_hands[0])):
				team_13_score += player_hands[0][i][0]
				team_13_score += player_hands[0][i][1]

			for i in range(0, len(player_hands[2])):
				team_13_score += player_hands[2][i][0]
				team_13_score += player_hands[2][i][1]

			team_24_score = 0

			for i in range(0, len(player_hands[1])):
				team_24_score += player_hands[1][i][0]
				team_24_score += player_hands[1][i][1]

			for i in range(0, len(player_hands[3])):
				team_24_score += player_hands[3][i][0]
				team_24_score += player_hands[3][i][1]

			if team_13_score == team_24_score:
				team_13_wins += 0.5
				team_24_wins += 0.5
				if debug_print:
					print ("Draw.")
			elif team_13_score < team_24_score:
				team_13_wins += 1
				if debug_print:
					print ("Team 1/3 wins.")
			else:
				team_24_wins += 1
				if debug_print:
					print ("Team 2/4 wins.")

			break

for i in range(0, 1000):
	play_game(play_better, play_highest, i%4)

print ("Team 1/3: %d" % (team_13_wins))
print ("Team 2/4: %d" % (team_24_wins))


