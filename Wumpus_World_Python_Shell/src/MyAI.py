import queue
from collections import defaultdict

from Agent import Agent

class MyAI ( Agent ):

	def __init__ ( self ):
		# MyAI information about self ( Knowledge Base )
		self.move_counter = 0 # counter for number of actions
		self.current_direction = "right" # initialized as facing "right"
		self.has_gold = False # bool on whether AI has gold on him or not
				# If so, the AI should attempt to find the way back to (0, 0) 
				# (possible values: "left", "right", "up", "down")
		self.has_arrow = True # bool on whether AI has shot the arrow or not
		self.current_location = (0,0) # initialized at (0, 0)
				# Note: (0, 0) refers to the most bottom-left square. 
				# Indices are different on arrays

		self.priority = "Gold" # Initialized as "Gold" to find prioritize finding gold
					# (possible values: �Gold� or �Exit�) // Exit is to prioritize exiting the map

		self.edge_list = []
		self.return_path = queue.Queue()
		self.explore_path = queue.Queue()
		self.fronttrack = (None, None)
		self.backtrack = (None, None)
		self.turning_back = None
		self.turning_front = None

		self.Wumpus_path = queue.Queue()
		self.Wumpus_direction_needed = None
		self.Wumpus_Final_Check = False	
		self.Checking = False	

		# Map information
		self.unknown = [] # list of nodes that have not been visited and possible
		self.visited = [] # locations that have been visited
		self.safe_squares = [] # list of locations (a, b) where it�s safe
		self.max_x = 7 # Rows in map (max is determined by bump)
		self.max_y = 7 # Columns in map (max is determined by bump)

		# Pitfall Information
		self.breeze_squares = [] # list of locations (a, b) where breeze resides
		self.possible_pitfall_locations = [] # list of possible pitfall locations
		self.pitfall_locations = [] # list of pitfalls deduced
		

		# Wumpus information / Hunting Info
		self.is_Wumpus_alive = True # initiated as true at the beginning of world
		self.stench_squares = [] # list of squares (a, b) where stench resides
		self.possible_Wumpus_locations = [] # list of possible Wumpus locations 
							# inferred by stench
		self.Wumpus_location = None # Used to keep track of Wumpus

	def getAction( self, stench, breeze, glitter, bump, scream ):

		# return Agent.Action.CLIMB # Used for Minimal AI turn-in
		
		self.move_counter += 1

		# Given percepts, return a move
		## Possible percepts (input): "stench", "breeze", "scream", "glitter�, "bump"
		## Possible moves (return value): "left", "right", "forward", "climb", "shoot", "grab" 
		
		# Adds our current_location to the visited list
		if (self.current_location not in self.visited) and (bump == False):
			self.visited.append(self.current_location) 
		
		# Update info based on percepts

		if bump == True:
			# Update max_x or max_y if bump found
			if self.current_direction == "up":
				self.max_y = self.current_location[1]
				self.current_location = (self.current_location[0], self.current_location[1] - 1)	# Bump so we didn't move forward (place remains unchanged)
		
			elif self.current_direction == "right":	
				self.max_x = self.current_location[0]
				self.current_location = (self.current_location[0] - 1, self.current_location[1])	# Bump so we didn't move forward (place remains unchanged)				
				
			elif self.current_direction == "left":
				self.current_location = (self.current_location[0] + 1, self.current_location[1])	# Bump so we didn't move forward (place remains unchanged)
	
			elif self.current_direction == "down":
				self.current_location = (self.current_location[0], self.current_location[1] + 1)	# Bump so we didn't move forward (place remains unchanged)
			
			# Update unknown to remove impossible locations
			unknown_list = self.unknown
			for location in unknown_list:
				if (location in self.unknown) and (self.withinBounds(location) == False):
					self.unknown.remove(location)
			
		four_directions = self.returnAllDirections() # List of the four locations (up, down, left, right) of AI
		
		if self.is_Wumpus_alive == True:
			if stench == True:
				if (self.current_location not in self.stench_squares):
					self.stench_squares.append(self.current_location)

				if (len(self.stench_squares) > 1):
					temp = []
					for location in four_directions:
						if (location in self.possible_Wumpus_locations) and (location not in self.visited) and (location not in temp):
							temp.append(location)
					self.possible_Wumpus_locations = temp
				else:		
					self.possible_Wumpus_locations = four_directions
						

			else: # if no stench, it imples that all 4 directions CANNOT have Wumpus
				for location in four_directions:
					if location in self.possible_Wumpus_locations:
						self.possible_Wumpus_locations.remove(location)
						if (location not in self.unknown) and (location not in self.visited) and (location not in self.possible_pitfall_locations):
							self.unknown.append(location)

		if breeze == True:
			# if on breeze square, every square around it can possibly be a pitfall (excluding ones we�ve visited)
			self.breeze_squares.append(self.current_location)

			for location in four_directions:
				if (location not in self.visited) and (location not in self.possible_pitfall_locations):
					self.possible_pitfall_locations.append(location)
		
		else:	# if no breeze it implies that all 4 directions CANNOT have pits
			for location in four_directions:
				if location in self.possible_pitfall_locations:
					self.possible_pitfall_locations.remove(location)
					if (location not in self.unknown) and (location not in self.visited) and (location not in self.possible_Wumpus_locations):
						self.unknown.append(location)
		
		if scream == True:	
			# Wumpus has died
			self.is_Wumpus_alive = False
			# print("Scream came from location(s): " + str(self.possible_Wumpus_locations))
			for location in self.possible_Wumpus_locations:
				if (location not in self.unknown) and (location not in self.possible_pitfall_locations) and (location not in self.visited):
					self.unknown.append(location)
				
			self.possible_Wumpus_locations.clear()


		#Creating edges
		for next in four_directions:
			e1 = (self.current_location, next)
			e2 = (next, self.current_location)
			if (e1 not in self.edge_list):
				self.edge_list.append(e1) # adds (previous, next) as possible edge
			if (e2 not in self.edge_list):
				self.edge_list.append(e2) # adds (next, previous) as possible edge


		### Start of where action can be returned ###

		# Grab Gold
		if glitter == True and self.priority == "Gold": 
			# Check for gold
			if self.has_gold == False:
				self.has_gold = True
				self.priority = "Exit"
				return Agent.Action.GRAB

		# MOVE COUNTER CRITERIA
		if (self.move_counter >= 500): # Could be changed
			self.priority = "Exit"


		# UNKNOWN CRITERIA priority changed to exit if there's no other possible places to explore
		if (self.current_location in self.unknown):
			self.unknown.remove(self.current_location)
		
		for location in four_directions:
			if (self.checkDanger(location) == False) and (location not in self.visited) and (location not in self.unknown):
				self.unknown.append(location)
		
		
		if (len(self.unknown) == 0) or (self.Checking == True):
			if (self.Wumpus_Final_Check == False) and (self.is_Wumpus_alive == True) and (self.has_gold == False):
				possible_spots = []
				self.Wumpus_Final_Check = True
				self.Checking = True
				for location in self.visited:
					for direction in ["up", "down", "left", "right"]:
						if (self.willHitWumpus(location, direction)):
							possible_spots.append((location, direction))
					
				if (len(possible_spots) > 0):
					min_cost_location = None
					min_cost = None
					min_cost_direction = None
					x1, y1 = self.current_location
					for location, direction in possible_spots:
						x2, y2 = location
						cost = ((x2-x1)**2 + (y2-y1)**2)**(1/2)
						if ((min_cost == None) or (cost < min_cost)):
							min_cost_location = location
							min_cost = cost
							min_cost_direction = direction
						
					self.Wumpus_path = self.createPath(self.edge_list, self.current_location, min_cost_location)
					self.Wumpus_direction_needed = min_cost_direction
			
			if (self.Wumpus_path.empty() == True) and (self.Wumpus_direction_needed == None):
				self.Checking = False
			if (self.Checking == True):
				if (self.Wumpus_path.empty() == True) and (self.current_direction == self.Wumpus_direction_needed):
					self.Checking = False
					return Agent.Action.SHOOT
				if (self.Wumpus_path.empty() == False):							
					if (self.turning_back == None):
						self.backtrack = self.Wumpus_path.get()
						self.turning_back = self.backtrack
					
					next_location = self.getFront()

					if (next_location == self.backtrack):
						self.current_location = next_location
						self.turning_back = None
						self.backtrack = (None, None)
						return Agent.Action.FORWARD
					else:
						left = self.getLeft()
						right = self.getRight()
						if (left == self.backtrack):
							return self.turnLeft()
						elif (right == self.backtrack):
							return self.turnRight()
						else:
							return self.turnLeft()
				else:
					return self.turnLeft()

			else:
				self.priority = "Exit"		

		# Explores and finds gold
		if (self.priority == "Gold"):
			
			# Moving Forward

			if (self.has_arrow == True):
				if (self.willHitWumpus(self.current_location, self.current_direction) == True):
					return Agent.Action.SHOOT
			
			if (self.explore_path.empty() == True):
				# Determines shortest unvisited node (based on Eucl. dist.)
				
				self.turning_front = None
				self.fronttrack = None
				
				min_cost_location = None 
				min_cost = None
				
				x1, y1 = self.current_location
				for x2, y2 in self.unknown:
					cost = ((x2-x1)**2 + (y2-y1)**2)**(1/2)
					if ((min_cost == None) or (cost < min_cost)):
						min_cost_location = (x2, y2)
						min_cost = cost
				
				self.explore_path = self.createPath(self.edge_list, self.current_location, min_cost_location)	# Note: this includes the current_location in queue
			
			if (self.turning_front == None):
				self.fronttrack = self.explore_path.get()
				self.turning_front = self.fronttrack
				

			next_location = self.getFront()
			
			if (next_location == self.fronttrack):
				
				self.current_location = next_location
				self.turning_front = None
				self.fronttrack = None
				
				return Agent.Action.FORWARD
			else:
				left = self.getLeft()
				right = self.getRight()
				if (left == self.fronttrack):
					return self.turnLeft()
				elif (right == self.fronttrack):
					return self.turnRight()
				else:
					return self.turnLeft()	

		# Find a way out 
		elif (self.priority == "Exit"):
			if (self.current_location == (0, 0)):
				return self.climbUp()

			if (self.return_path.empty() == True):
				self.turning_back = None
				self.backtrack = (None, None)
				self.return_path = self.createPath(self.edge_list, self.current_location, (0,0))	# Note: this includes the current_location in queue
				
			
			if (self.turning_back == None):
				self.backtrack = self.return_path.get()
				self.turning_back = self.backtrack
			
			next_location = self.getFront()

			if (next_location == self.backtrack):
				self.current_location = next_location
				self.turning_back = None
				self.backtrack = (None, None)
				return Agent.Action.FORWARD
			else:
				left = self.getLeft()
				right = self.getRight()
				if (left == self.backtrack):
					return self.turnLeft()
				elif (right == self.backtrack):
					return self.turnRight()
				else:
					return self.turnLeft()

		else:
			return -1

		# ======================================================================
    
	# Helper Functions

	def getFront(self):
		""" Using current location and direction, return the location in front of the AI """
		agentFrontSide = None
		if (self.current_direction == "left"):
			agentFrontSide = (self.current_location[0] - 1, self.current_location[1])
		elif (self.current_direction == "right"):
			agentFrontSide = (self.current_location[0] + 1, self.current_location[1])
		elif (self.current_direction == "up"):
			agentFrontSide = (self.current_location[0], self.current_location[1] + 1)
		elif (self.current_direction == "down"):
			agentFrontSide = (self.current_location[0], self.current_location[1] - 1)
		return agentFrontSide

	def getLeft(self):
		""" Using AI's current location and direction, return the location LEFT of the AI """
		AgentLeftSide = None
		if (self.current_direction == "left"):
			AgentLeftSide = (self.current_location[0], self.current_location[1] - 1)
		elif (self.current_direction == "right"):
			AgentLeftSide = (self.current_location[0], self.current_location[1] + 1)
		elif (self.current_direction == "up"):
			AgentLeftSide = (self.current_location[0] - 1, self.current_location[1])
		elif (self.current_direction == "down"):
			AgentLeftSide = (self.current_location[0] + 1, self.current_location[1])
		return AgentLeftSide
		
	def getRight(self):
		""" Using AI's current location and direction, return the location RIGHT of the AI """		
		AgentRightSide = None				
		if (self.current_direction == "left"):
			AgentRightSide = (self.current_location[0], self.current_location[1] + 1)
		elif (self.current_direction == "right"):
			AgentRightSide = (self.current_location[0], self.current_location[1] - 1)
		elif (self.current_direction == "up"):
			AgentRightSide = (self.current_location[0] + 1, self.current_location[1])
		elif (self.current_direction == "down"):
			AgentRightSide = (self.current_location[0] - 1, self.current_location[1])
		return AgentRightSide

	def withinBounds(self, location):
		""" Checks if the location is within bounds """
		x, y = location
		return (0 <= x < self.max_x) and (0 <= y < self.max_y)

	def isSafe(self, location):
		""" Given a location, checks to see if it's safe to move there """
		if (location in self.possible_pitfall_locations):
			# print("[{}] is a possible pitfall location".format(str(location)))
			return False
		elif (location in self.possible_Wumpus_locations):
			# print("[{}] is a possible Wumpus location".format(str(location)))
			return False
		return True
	
	def climbUp(self):
		""" Climbs up """
		# print("EXPLORED AREAS: " + str(self.visited))
		return Agent.Action.CLIMB

	def turnLeft(self):
		""" Turns the agent left and updates current_direction """
		if self.current_direction == "right":
			self.current_direction = "up"
		elif self.current_direction == "up":
			self.current_direction = "left"
		elif self.current_direction  == "left":
			self.current_direction = "down"
		elif self.current_direction == "down":
			self.current_direction = "right"
		return Agent.Action.TURN_LEFT

	def turnRight(self):
		""" Turns the agent right and updates current_direction """
		if self.current_direction == "right":
			self.current_direction = "down"
		elif self.current_direction == "down":
			self.current_direction = "left"
		elif self.current_direction == "left":
			self.current_direction = "up"
		elif self. current_direction == "up":
			self.current_direction = "right"
		return Agent.Action.TURN_RIGHT	

	def returnAllDirections(self):
		""" Returns a list of all directions of AI's current position that are within the map """
		x, y = self.current_location
		up = (x, y + 1) 
		down =	(x, y - 1)
		left = (x + 1, y)
		right =	(x - 1, y)
		
		result = []
		if (self.withinBounds(up) == True):
			result.append(up)
		if (self.withinBounds(down) == True):
			result.append(down)
		if (self.withinBounds(left) == True):
			result.append(left)
		if (self.withinBounds(right) == True):
			result.append(right)
				
		return result

	def checkDanger(self, location):
		""" Checks if the location given is a possible danger zone returns true if it's dangerous, else false """
		if (location not in self.possible_Wumpus_locations) and (location not in self.possible_pitfall_locations):
			return False
		return True

	
	def FrontIsSafe(self):
		""" Checks whether the front square is safe to move on """
		temp = self.getFront()		
		if (temp in self.possible_pitfall_locations) or (temp in self.possible_Wumpus_locations):
			return False
		else:	
			return self.withinBounds(temp) # Checks the front location's bounds

	

	def willHitWumpus(self, location, direction):
		""" Determines if you would hit Wumpus based on given direction and location relative to Wumpus """
		if (self.is_Wumpus_alive == True) and (self.has_arrow == True):
			i = len(self.possible_Wumpus_locations)
			if (i > 0):
				counter = 0
				x1, y1 = location
				for x2, y2 in self.possible_Wumpus_locations:
					if (direction == "left"):
						if (x1 > x2) and (y1 == y2):
							counter += 1
					elif (direction == "right"):
						if (x1 < x2) and (y1 == y2):
							counter += 1
					elif (direction == "up"):
						if (x1 == x2) and (y1 < y2):
							counter += 1
					elif (direction == "down"):
						if (x1 == x2) and (y1 > y2):
							counter += 1
				if (counter == i):
					return True
		return False

	
	def createPath(self, edge_list, start, end):
		# Uses BFS to find path from start to end
		# Returns a queue of location(x, y) from (start) to (end)
		
		current = start	
		BFS_queue = queue.Queue() # Queue for BFS
		BFS_queue.put(current) # Add start to visited
		
		already_visited = [current] # Add start to visited
		
		path = dict()
		
		edge_dict = defaultdict(list) #create adjacent list
		for edge in edge_list:
			edge_dict[edge[0]].append(edge[1])	

		while (BFS_queue.empty() == False):
			loc = BFS_queue.get(0) # pops first item on queue
			for v in edge_dict[loc]:
				if v not in already_visited:
					already_visited.append(v) # Adds to visited
					BFS_queue.put(v) # Adds location to queue
					path[v] = loc
					
				if (v  == end): # once it finds the destination, stop algorithm
					break
					
		result = queue.LifoQueue()
		key = end
		result.put(key) # Adds the end destination
		while (key in path):
			result.put(path[key])
			key = path[key]
		result.get() # Removes starting node
		return result
				
				 


		
		
		

		
		
    		