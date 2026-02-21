#!/bin/python

from monde import *

def square(a):

	return a * a

class A_star_pathfinder_item (object):

	def __init__ (self, father, x, y, already_moved, delay):

		self.father = father # indice du pere dans la liste already_seen.
		self.x = x
		self.y = y
		self.amove = already_moved
		self.delay = delay

	def copy(self):

		return  A_star_pathfinder_item(self.father, self.x, self.y, self.amove, self.delay)

        def get_distance (self, end):

            return self.amove + max(abs(self.x - end.x), abs(self.y - end.y))

	def get_bird_distance(self, end):

		return max(abs(self.x - end.x), abs(self.y - end.y)) + (end.delay - self.delay + end.frequency) % end.frequency

	def get_eucl_distance(self, end):

		return square(self.x - end.x) + square(self.y - end.y)

def chosing_next_a_star(list, end):

	if list == []:

		raise Exception("No ways found between those two points.")
		

	i = 0

	for it in range(len(list)):

		d1 = list[it].get_distance(end)
		d2 = list[i].get_distance(end)

		if d1 < d2: # Je n ai pas trouve plus joli...

			i = it

		if d1 == d2 and list[it].get_eucl_distance(end) < list[i].get_eucl_distance(end):

			i = it # pour des raisons esthetiques (et pour
			       # que le bricolage soit ensuite plus
			       # simple), le programme va preferer une
			       # ligne *relativement* droite.

	return i


def nb_neighbours_a_star(x, y, father, already_seen, map, frequency, maxx, maxy):

	n = 0
	
	for dx in [-1, 0, 1]:
      
		for dy in [-1, 0, 1]:
			
			if dy != 0 or dx != 0:
				
				if is_in(x + dx, y + dy, maxx, maxy):

					if map[x + dx][y + dy] != Etat.EMPTY:
						
						n = n + 1
	
	# ajouter ses parents dans son arbre de recherche, sauf son parent immediat.
	current = already_seen[father].father

	if current == father: # Un petit cas particulier pour l'origine...

		return n

	while True:

		if abs(already_seen[current].x - x) <= 1 and abs(already_seen[current].y - y) <= 1:

			n = n + 1

		if current == already_seen[current].father:

			break # Je n ai pas trouve mieux comme equivalent de la boucle do...while.

		current = already_seen[current].father

	return n # on doit pouvoir optimiser en revoyant un booleen
		 # vrai s il y a des voisins, mais je trouve ca moins
		 # beau...

def not_in_list_a_star(list, x, y, d):

	for obj in list:

		if obj.x == x and obj.y == y and obj.delay == d:

			return False
	return True

def search_remplace_a_star(list, x, y, d, amove, father): # add an object in the list, but remplace if there is an instance less efficient of it. Return the indice.

	i = 0

	for obj in list:

		if obj.x == x and obj.y == y and obj.delay == d:

			if obj.amove > amove:

				obj.amove = amove
				obj.father = father

			return i
		i = i + 1

	# sinon on l'ajoute a la fin.
	ind = len(list)
	list.append(A_star_pathfinder_item(father, x, y, amove, d))
	return ind

def add_a_star(list, x, y, d, amove, father):

	ind = len(list)
	list.append(A_star_pathfinder_item(father, x, y, amove, d))
	return ind

def get_middle_wire(start, first, end, component):

	current_point = Point(first.x, first.y)
	previous_point = Point(start.x, start.y)
	middle_point = Point(first.x, first.y)
	previous_middle_point = Point(start.x, start.y)
	d = 0

	while current_point.x != end.x or current_point.y != end.y:

		tmp = current_point
		current_point = next_point(current_point, previous_point, component)
		previous_point = tmp

		if d % 2 == 1:

			tmp = middle_point
			middle_point = next_point(middle_point, previous_middle_point, component)
			previous_middle_point = tmp

		d = d + 1

	
	return previous_middle_point, middle_point, d + 1

def next_point(current, previous, component):

	for dx in [-1, 0, 1]:

		for dy in [-1, 0, 1]:

			if is_in(current.x + dx, current.y + dy, component.x, component.y) and (dx != 0 or dy != 0):

				if component.map[current.x + dx][current.y + dy] == Etat.WIRE and (current.x + dx != previous.x or current.y + dy != previous.y):

					return Point(current.x + dx, current.y + dy)

	return Exception("No next point found.")


class Data(object):

	def __init__(self, start, component):

		self.already_seen = [A_star_pathfinder_item(0, start.x, start.y, 0, 0)]
		# En fait, on ne prendra pas en compte le retard.
		# Je n'ai juste as envie de faire une nouvelle classe juste pour ca.
		
		self.a_star_list = []
		for dx in [-1, 0, 1]:

			for dy in [-1, 0, 1]:

				if is_in(start.x + dx, start.y + dy, component.x, component.y):

					if nb_neighbours_a_star(start.x + dx, start.y + dy, 0, self.already_seen, component.map, 1, component.x, component.y) == 0 and (dx != 0 or dy != 0):

						self.a_star_list.append(A_star_pathfinder_item(0, start.x + dx, start.y + dy, 1, 0))

		self.start = start
		self.component = component

def get_list_father(already_seen, ind):

	list = [already_seen[ind]]

	i = ind

	while already_seen[i].father != i:

		i = already_seen[i].father
		list.append(already_seen[i])
	return list


def dynamic_a_star(end, datas):

	end.delay = 0 # je sais, c'est moche, mais sinon, ca ne passera pas...

	i = 0
	for obj in datas.already_seen:

		if obj.x == end.x and obj.y == end.y:
			# si l'on est deja passe par ce point.
			return (get_list_father(datas.already_seen, i), datas)
		i = i + 1

	# sinon, il va falloir calculer.
	i = chosing_next_a_star(datas.a_star_list, end)

	ind = 0

	while datas.a_star_list[i].x != end.x or datas.a_star_list[i].y != end.y:

		ind = len(datas.already_seen)
		datas.already_seen.append(datas.a_star_list[i])

		for dx in [-1, 0 , 1]:

			for dy in [-1, 0, 1]:

				if is_in(datas.a_star_list[i].x + dx, datas.a_star_list[i].y + dy, datas.component.x, datas.component.y):

					if nb_neighbours_a_star(datas.a_star_list[i].x + dx, datas.a_star_list[i].y + dy, ind, datas.already_seen, datas.component.map, 1, datas.component.x, datas.component.y) == 0 and (dx != 0 or dy != 0):

						search_remplace_a_star(datas.a_star_list, datas.a_star_list[i].x + dx, datas.a_star_list[i].y + dy, 0, datas.a_star_list[i].amove + 1, ind)

		del datas.a_star_list[i]

		i = chosing_next_a_star(datas.a_star_list, end)

	return (get_list_father(datas.already_seen, ind), datas)
