#!/usr/bin/python

class Etat (object):

      EMPTY = 0
      WIRE = 1
      HEAD = 2
      TAIL = 3

def is_in(x, y, maxx, maxy):
      return (x >= 0 and x < maxx and y >= 0 and y < maxy)

def nb_neighbour(monde, cell, maxx, maxy):
      nb = 0
      for c in cell.neighbour:
                  
            if monde[c.x][c.y].e == Etat.HEAD:
                  nb = nb + 1
      return nb

def is_in_list(p, l):
      for a in l:
            if a.x == p.x and a.y == p.y:
                  return True
      return False

def erase_pairs(l):
      new_l = []
      for x in l:
            if not is_in_list(x, new_l):
                  new_l.append(x)
      return new_l

class Point (object):
      
      def __init__ (self, x, y):
            self.x = x
            self.y = y

class Cell (object):

      def __init__ (self, e, voisines):
            self.e = e
            self.neighbours = voisines # Les coordonees des voisines.

def get_neighbour(monde, x, y, maxx, maxy):
      neighbour = []
      if monde[x][y].e == Etat.EMPTY:
            return []

      for i in [-1, 0, 1]:

            for j in [-1, 0, 1]:
                  
                  if is_in(x + i, y + j, maxx, maxy) and not (i == 0 and j == 0):
                        if monde[x + i][y + j].e != Etat.EMPTY:
                              neighbour.append(Point(x + i, y + j))
      return neighbour

class Map (object):

      def __init__ (self, x, y):

            self.pos = Point(0, 0) # pour la compatibilite avec les modules de Francois.

            self.x = x
            self.y = y
            self.monde = [[], []] # contient deux mondes. Switch a
                                  # chaque tour. Cela permet d eviter
                                  # de perdre du temps en allocation
                                  # et recopie.
            self.current_world = 0
            self.electron = [] # tableau de coordonnees des
                               # electrons. (en fait de toutes les
                               # cases qui peuvent etre modifiee au
                               # prochain tour)
            for i in range(x):

                  self.monde[0].append([])
                  self.monde[1].append([])
                  for j in range(y):

                        self.monde[0][i].append(Cell(Etat.EMPTY, []))
                        self.monde[1][i].append(Cell(Etat.EMPTY, []))

      def iter_part(self, electron):

            new_electron = []

            for c in electron:
                  
                  e = self.monde[self.current_world][c.x][c.y].e
                  if e == Etat.HEAD:
                        self.monde[1 - self.current_world][c.x][c.y].e = Etat.TAIL
                        new_electron.append(c) # Elle doit etre supprimee a l etape suivante : la case va bien etre modifiee.
                  elif e == Etat.TAIL:
                        self.monde[1 - self.current_world][c.x][c.y].e = Etat.WIRE
                        new_electron.append(c) # C est un cable a cette etape, mais une queue d electron a la precedente : il faudra enlever la queue dans la suivante/precedente.
                  elif e == Etat.WIRE:
                        n = nb_neighbour(self.monde[self.current_world], self.monde[self.current_world][c.x][c.y], self.x, self.y)
                        if n > 0 and n <= 2:
                              self.monde[1 - self.current_world][c.x][c.y].e = Etat.HEAD
                              new_electron.append(c)
                              for neighb in self.monde[self.current_world][c.x][c.y].neighbour:
                                    
                                    new_electron.append(neighb)
                        else:
                              self.monde[1 - self.current_world][c.x][c.y].e = Etat.WIRE
            return new_electron
      

      def iter_step(self):
            self.electron = self.iter_part(self.electron)
            self.current_world = 1 - self.current_world
            self.electron = erase_pairs(self.electron) # On supprime les doublons, pour optimiser.

      def print_world(self):
            for y in range(self.y):

                  for x in range(self.x):

                        e = self.monde[self.current_world][x][y].e
                        if e == Etat.EMPTY:
                              print ' ',
                        if e == Etat.WIRE:
                              print '=',
                        if e == Etat.HEAD:
                              print 'O',
                        if e == Etat.TAIL:
                              print '*',
                  print '\n',

      def set_elec(self, x, y):
            if x >= 0 and y >= 0 and x < self.x and y < self.y:
                  if self.monde[self.current_world][x][y].e == Etat.EMPTY:
                        self.set_wire(x, y)
                  self.monde[self.current_world][x][y].e = Etat.HEAD
                  self.electron.append(Point(x, y))
                  for neighb in self.monde[self.current_world][x][y].neighbour:
                          
                          self.electron.append(neighb)

      def get_size(self):

            return (self.x, self.y)

      def get_orig(self):

            return (self.pos.x, self.pos.y)

      def set_tail(self, x, y):
            if x >= 0 and y >= 0 and x < self.x and y < self.y:
                  self.set_wire(x, y)
                  self.monde[self.current_world][x][y].e = Etat.TAIL
                  self.monde[1 - self.current_world][x][y].e = Etat.TAIL
		  self.electron.append(Point(x, y))

      def set_wire(self, x, y):
            if x >= 0 and y >= 0 and x < self.x and y < self.y:
                  self.monde[self.current_world][x][y].e = Etat.WIRE
                  self.monde[1 - self.current_world][x][y].e = Etat.WIRE
                  for i in [-1, 0, 1]:

                        for j in [-1, 0, 1]:
                  
                              if is_in(x + i, y + j, self.x, self.y):
                                    self.monde[self.current_world][x + i][y + j].neighbour = get_neighbour(self.monde[self.current_world], x + i, y + j, self.x, self.y) # On reactualise les cellules sur le cote.
                                    self.monde[1 - self.current_world][x + i][y + j].neighbour = get_neighbour(self.monde[1 - self.current_world], x + i, y + j, self.x, self.y)

      def get_state(self, x, y):

		return self.monde[self.current_world][x][y].e
	
      def resize(self, x, y): 	# resize the map (warning : all the cases out of the bounds are erased)
				# Pas utilise en pratique.
            if(x > self.x):
                  for i in range(x - self.x):

                        self.monde[self.current_world].append([])
                        self.monde[1 - self.current_world].append([])
                        for j in range(self.y):

                              self.monde[self.current_world][self.x + i].append(Cell(Etat.EMPTY, []))
                              self.monde[1 - self.current_world][self.x + i].append(Cell(Etat.EMPTY, []))
                  self.x = x
            else:
                  self.x = x
                  self.monde[self.current_world] = self.monde[self.current_world][:x]
                  self.monde[1 - self.current_world] = self.monde[1 - self.current_world][:x]

            if(y > self.y):
                  for i in range(self.x):

                        for j in range(y - self.y):

                              self.monde[self.current_world][i].append(Cell(Etat.EMPTY, []))
                              self.monde[1 - self.current_world][i].append(Cell(Etat.EMPTY, []))
                  self.y = y
            else:
                  self.y = y
                  for i in range(self.x):

                        self.monde[self.current_world][i] = self.monde[self.current_world][i][:y]
                        self.monde[1 - self.current_world][i] = self.monde[1 - self.current_world][i][:y]

            new_electron = []
            for e in self.electron:
                  
                  if is_in(e.x, e.y, self.x, self.y):
                        new_electron.append(e)
            self.electron = new_electron

