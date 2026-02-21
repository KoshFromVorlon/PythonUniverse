#!/usr/bin/python

from monde import *
from a_star import *

class Connection (object):
	
	def __init__ (self, f, x, y):
		
		self.frequency = f
		self.delay = 0
		self.x = x
		self.y = y

	def set_delay(self, d):
		
		self.delay = d

	def add_to_position(self, x, y):

		self.x = self.x + x
		self.y = self.y + y

def create_from_map(la_map):

   # ne recree pas les connections a
   # partir de rien : elles sont bel
   # et bien perdues.
   # J'aurais prefere la creer dans Map, mais Component a besoin de Map : Map ne doit pas avoir besoin de Component. On n'est pas en C...
   component = Component(la_map.x, la_map.y)

   for i in range(la_map.x):

         for j in range(la_map.y):
   
               component.map[i][j] = la_map.get_state(i, j)

   component.pos = Point(la_map.pos.x, la_map.pos.y)

   return component

class Component (object):
	
	def __init__ (self, x, y):

		self.pos = Point(0, 0)
		# ajoutes pour des raisons de compatibilite avec le
		# code de francois.

		self.x = x
		self.y = y

		self.map = []
		self.connections = []
		
		for i in range(x):
			
			self.map.append([])
			
			for j in range(y):
				
				self.map[i].append(Etat.EMPTY)

	def set_wire (self, x, y):
		
		self.map[x][y] = Etat.WIRE
	
	def set_empty (self, x, y):
		
		self.map[x][y] = Etat.EMPTY
	
	def set_state (self, x, y, state):
		
		self.map[x][y] = state
	
	def add_connection (self, c):
		
		self.connections.append(c)
	
	def get_state(self, x, y):
		
		return self.map[x][y]
	
	def turn_to_map (self):
		
		map = Map(self.x, self.y)
		
		for x in range(self.x):
			
			for y in range(self.y):
				
				if self.map[x][y] != Etat.EMPTY:
					map.set_wire(x, y)

		# Les electrons doivent etres ajoutes a la fin !

		for x in range(self.x):

			for y in range(self.y):

				if self.map[x][y] == Etat.HEAD:
					map.set_elec(x, y)
				elif self.map[x][y] == Etat.TAIL:
					map.set_tail(x, y)

		map.pos = Point(self.pos.x, self.pos.y)

		return map

	def get_size(self):

		return (self.x, self.y)

	def set_orig(self, x, y):

		self.pos.x = x
		self.pos.y = y

	def get_orig(self):

		return (self.pos.x, self.pos.y)

	def random(self):

		for x in range(self.x):

			for y in range(self.y):

				self.set_state(i, j, random.choice(range(4)))

	def resize(self, left, top, right, bottom):
		# agrandie la carte de left vers la gauche, right vers la droite, etc.
		
		if self.x + left + right < 0 or self.y + top + bottom < 0:
			raise Exception("cannot resize the Component to a negative size.")

		if self.x + left + right == 0 or self.y + top + bottom == 0:
			# La carte devient vide.
			self.x = 0
			self.y = 0
			self.map = [[]]
		else:
			# Les cas ou il se passe quelque chose.
			# On agrandi d'abord, on enleve ensuite.
			if right > 0:
				
				for x in range(right):

					self.map.append([])
					for y in range(self.y):

						self.map[self.x + x].append(Etat.EMPTY)
				self.x = self.x + right

			if left > 0:
				
				for x in range(left):

					self.map.insert(0, [])
					for y in range(self.y):

						self.map[0].append(Etat.EMPTY)
				self.x = self.x + left
				self.pos.x = self.pos.x - left
				
			if bottom > 0:
				
				for x in range(self.x):

					for y in range(bottom):

						self.map[x].append(Etat.EMPTY)
				self.y = self.y + bottom

			if top > 0:
				
				for x in range(self.x):

					for y in range(top):

						self.map[x].insert(0, Etat.EMPTY)
				self.y = self.y + top
				self.pos.y = self.pos.y - top

			if right < 0:

				self.map = self.map[:(self.x + right)]
				self.x = self.x + right

			if left < 0:

				self.map = self.map[(-left):]
				self.x = self.x + left
				self.pos.x = self.pos.x - left

			if bottom < 0:

				for x in range(self.x):

					self.map[x] = self.map[x][:(self.y + bottom)]
				self.y = self.y + bottom

			if top < 0:

				for x in range(self.x):

					self.map[x] = self.map[x][(-top):]
				self.y = self.y + top
				self.pos.y = self.pos.y - top

		# Ne garder des connexions que celles qui restent dans
		# la carte, et actualiser leurs coordonnees.

		new_con = []

		for c in self.connections:

			c.add_to_position(left, top)

			if is_in(c.x, c.y, self.x, self.y):
				
				new_con.append(c)

		self.connections = new_con
	

	def copy_component(self, p1, p2): # pour l'interface : c'est un copier.

		if p1.x > p2.x:

			tmp = p2.x
			p2.x = p1.x
			p1.x = tmp

		if p1.y > p2.y:

			tmp = p2.y
			p2.y = p1.y
			p1.y = tmp


		c = Component(p2.x - p1.x, p2.y - p1.y)

		for x in range(p2.x - p1.x):

			for y in range(p2.y - p1.y):

				c.set_state(x, y, self.map[p1.x + x][p1.y + y])
		
		for con in self.connections:

			if is_in(con.x - p1.x, con.y - p1.y, c.x, c.y):

				new_con = Connection(con.frequency, con.x - p1.x, con.y - p1.y)
				new_con.set_delay(con.delay)
				c.add_connections(new_con)

		return c

	def put_component (self, x, y, c): # pour l'interface : c'est un coller.
		
		for cx in range(c.x):
			
			for cy in range(c.y):
				
				self.set_state(x + cx, y + cy, c.map[cx][cy])

		for con in c.connections:
			
			new_con = Connection(con.frequency, con.x + x, con.y + y)
			new_con.set_delay(con.delay)
			self.connections.append(new_con)
	
	def link_connections_a_star (self, i, j, search_remplace):
		# La fonction ou tout se passe. i et j sont les
		# indices des connections a connecter.

		start = self.connections[i]
		end = self.connections[j]
		
		#self.map[start.x][start.y] = Etat.HEAD #FIXME
		#self.map[end.x][end.y] = Etat.HEAD
		#self.turn_to_map().print_world() # pour voir ou on en est. # FIXME : temporaire.
		
		self.map[start.x][start.y] = Etat.EMPTY # On va le remplir ensuite,
		self.map[end.x][end.y] = Etat.EMPTY     # mais c'est plus simple pour l'algorithme.

		if start.frequency == end.frequency and i != j:

			indicei = i
			indicej = j

			# L'algorithme se rapproche du A*, mais chaque case a
			# un certains nombre d occurrences. (une pour chaque
			# retard possible modulo la frequence.
			
			a_star_list = []
			already_seen = [A_star_pathfinder_item(0, start.x, start.y, 0, start.delay)]
			for x in [-1, 0 , 1]:
				for y in [-1, 0, 1]:
					if is_in(start.x + x, start.y + y, self.x, self.y):
						if nb_neighbours_a_star(start.x + x, start.y + y, 0, already_seen, self.map, start.frequency, self.x, self.y) == 0 and (x != 0 or y != 0):
							search_remplace(a_star_list, start.x + x, start.y + y, (start.delay + 1) % start.frequency, 1, 0)

			i = chosing_next_a_star(a_star_list, end)

			indice = 0

			while a_star_list[i].get_bird_distance(end) >= 1:
				
				indice = search_remplace(already_seen, a_star_list[i].x, a_star_list[i].y, a_star_list[i].delay, a_star_list[i].amove, a_star_list[i].father)

				for dx in [-1, 0, 1]:
					
					for dy in [-1, 0, 1]:
					
						if dx != 0 or dy != 0:

							if is_in(a_star_list[i].x + dx, a_star_list[i].y + dy, self.x, self.y):

								if nb_neighbours_a_star(a_star_list[i].x + dx, a_star_list[i].y + dy, indice, already_seen, self.map, start.frequency, self.x, self.y) == 0:
									
									if not_in_list_a_star(already_seen, a_star_list[i].x + dx, a_star_list[i].y + dy, (a_star_list[i].delay + 1) % start.frequency):
										
										search_remplace(a_star_list, a_star_list[i].x + dx, a_star_list[i].y + dy, (a_star_list[i].delay + 1) % start.frequency, already_seen[indice].amove + 1, indice)
										#a_star_list.append(A_star_pathfinder_item(ind, a_star_list[i].x + dx, a_star_list[i].y + dy, already_seen[ind].amove + 1, (a_star_list[i].delay + 1) % start.frequency))
								                # en effet, la distance dans wireworld en diagonale et celle en ligne droite est la meme : on n'augmente la distance parcourue que de 1.
									else:
										
										search_remplace(already_seen, a_star_list[i].x + dx, a_star_list[i].y + dy, (a_star_list[i].delay + 1) % start.frequency, already_seen[indice].amove + 1, indice)
										#already_seen.append(A_star_pathfinder_item(ind, a_star_list[i].x + dx, a_star_list[i].y + dy, already_seen[ind].amove + 1, (a_star_list[i].delay + 1) % start.frequency))
										# si jamais on a deja trouve un chemin, mais qui est moins bon, on choisit le nouveau.
										# On remarque que cela pourra changer l'accessibilite d'une case : il est possible que l'algorithme ne trouve pas de chemin, alors qu'il en existe.
										# Mais si je ne fait pas ca, le temps de calcul augmente en fleche.
				del a_star_list[i]

				i = chosing_next_a_star(a_star_list, end)
			
			if indicei > indicej:
				del self.connections[indicei]
				del self.connections[indicej]
			else:
				del self.connections[indicej]
				del self.connections[indicei]

			#dessin du cable.

			self.map[start.x][start.y] = Etat.WIRE
			self.map[end.x][end.y] = Etat.WIRE

			current = indice # la derniere case visitee
			previous = current

			while already_seen[current].father != current: # tant que l'on n'est pas retourne au debut...

				self.map[already_seen[current].x][already_seen[current].y] = Etat.WIRE

				previous = current
				current = already_seen[current].father

			return already_seen[previous] # On retourne la premiere case a parcourir pour aller vers la case de fin.

		else:

			raise Exception("Unacceptable wire.")


	def link_connections_fonction(self, i, j, search_remplace): # search_remplace est une fonction : celle utilisee par l'algorithme.

		# Il va falloir ruser : la fonction precedente est
		# beaucoup trop lente si on lui demande de gerer les
		# frequences.  Le cas ou la frequence est de 2 marche
		# plus ou moins s'il y a de la place (beaucoup de
		# place) et que les points a relier sont proches, on
		# va l'utiliser.

		start = self.connections[i]
		end = self.connections[j]

		if start.frequency != end.frequency:

			return

		ind = len(self.connections)

		c1 = Connection(1, start.x, start.y)
		c1.set_delay(start.delay)
		self.add_connection(c1)
		c2 = Connection(1, end.x, end.y)
		c2.set_delay(start.delay)
		self.add_connection(c2)

		first_movement = self.link_connections_a_star(ind, ind + 1, search_remplace)

		previous, point, d = get_middle_wire(start, first_movement, end, self)

		while (d + start.delay) % start.frequency != end.delay:

			b = False # b vaut True si la connection a reussi.

			while not b:

				ind = len(self.connections)

				next = next_point(point, previous, self)
				next2 = next_point(next, point, self)
				next3 = next_point(next2, next, self) # on remarque que si le cable est trop court, cette fonction renvoit directement une erreur : ce n'est pas la peine de bricoler plus si l'on a pas de marge d'actions...

				self.map[point.x][point.y] = Etat.EMPTY
				self.map[next.x][next.y] = Etat.EMPTY
				self.map[next2.x][next2.y] = Etat.EMPTY

				con = Connection(2, previous.x, previous.y)
				con.set_delay(0)
				self.add_connection(con)

				con = Connection(2, next3.x, next3.y)
				con.set_delay(1) # ainsi, la fonction link_connection_a_star va ajouter (au moins) un de retard.
				self.add_connection(con)

				try:
					self.link_connections_a_star(ind, ind + 1)
					b = True
				except:
					self.map[point.x][point.y] = Etat.WIRE
					self.map[next.x][next.y] = Etat.WIRE
					self.map[next2.x][next2.y] = Etat.WIRE
					self.map[next3.x][next3.y] = Etat.WIRE
					self.map[previous.x][previous.y] = Etat.WIRE
					# ces cables sont en effet
					# enleves par la fonction
					# link_connection_a_star
					del self.connections[ind + 1]
					del self.connections[ind]
					tmp = Point(point.x, point.y)
					point = next_point(point, previous, self)
					previous = tmp
					if next3.x == end.x and next3.y == end.y:
						# On parcourt dans l'autre sens
						point, previous, d = get_middle_wire(start, first_movement, end, self)
					if next3.x == start.x and next3.y == start.y:
						# La, on a tente de bricoler comme on pouvait partout, mais on a rien trouve.
						raise Exception("No ways found between those two points.")

			# attention, pour pouvoir executer la ligne
			# suivante, il faut que le cable ait ete
			# reconstruit localement.
			previous, point, d = get_middle_wire(start, first_movement, end, self)

			print (d + start.delay) % start.frequency


		if i > j:
			del self.connections[i]
			del self.connections[j]
		else:
			del self.connections[j]
			del self.connections[i]

	def link_connections_quick(self, i, j):

		self.link_connections_fonction(i, j, search_remplace_a_star)

	def link_connections_low(self, i, j):

		self.link_connections_fonction(i, j, add_a_star)

