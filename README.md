# Wumpus-World-Project
## CS 171 Project (11-week project)

Note: Code written by me is in the MyAI.py file. All the other files are provided by the course to standardize testing conditions when applicable. All code was written in one file, as instructed by my course professor.

Also to note: Code was written and tested on Python 3.5.2. The AI scored in the top 10% of the class in the final tournament near the end of the course. 

### Purpose of the Project
This was project given by Professor Richard H. Lathrop (UC Irvine Professor) to do that spanned through the entire academic quarter. The course was an Introduction to Articial Intelligence that explored concepts of AI. The task here is to utilize those concepts to develop an AI to interact with the unknown environment (to the AI, of course). One notable feature that made this AI robust was the way it adapted to the knowledge gained from every interation after an action. From this knowledge, the AI is then able to make smart decisions on how to traverse through the cave to acheive the best performance metric it can possibly get. 

### What is Wumpus World?
The Wumpus World is a game consisting of a cave. Inside the cave, there are rooms connected by passageways. Lurking inside the cave is a terrible monster called Wumpus, a beast that eats anything that enters its room. The Wumpus can be killed by an agent (the AI that is coded) by shooting an arrow, but the agent only has one arrow (so make it count!). Additionally, some rooms contain bottomless pits that traps anyone that enters those particular rooms. The goal of this game is to find a heap of gold, which is randomly located in some room in the cave. Sometimes the heap of gold is unreachable, and thus the agent must know when to leave the cave once it has determined it's impossible obtain the gold. The game is defined by these four descriptions:

Performance Mesaure:
  The performance measure of an agent is an integer score calculated based on the following:
  1. Start at 0 points.
  2. -1 point for each action taken. 
  3. -1 for using the arrow (additional to the -1 point).
  4. -1000 points for falling into a pit or being eaten by the Wumpus.
  5. +1000 for climbing out of the cave with gold.
  
  Note: The game ends either when the agent dies, when the agent climbs out of the cave, or when the agent's score goes below -1000.
  
Environment:
  The environment is classified as partially observable, determininstic, sequuential, static, discrete, and single agent.
  1. Cave will be an N by M grid of rooms, where N <= 3 and M <= 7.
  2. Agent starts at the bottom left square (1, 1) and faces right.
  3. Locations of gold and Wumpus are chosen randomly with a uniform distribution, from squares other than the start square.
  4. Each square other than the start can be a pit, with a 20% probability

Actuators:
  Actuators refers to the agent's possible moves, which includes the following:
  1. Forward
  2. Turn left (90 degrees)
  3. Turn right (also 90 degrees)
  4. Grab
  5. Shoot
  6. Climb
  
Sensors:
  The agent can also perceive clues about its environment through it's "sensors."
  These clues include:
  1) Stench - means there is an adjacent square contains Wumpus
  2) Breeze - means there is/are adjacent square(s) that have bottomless pits
  3) Glitter - means that gold is in some adjacent square
  4) Bump - Agent walked into a wall
  5) Scream - Wumpus is killed (which can be perceived anywhere in the cave)
 
For a more thorough explanation and overview, please refer to the <a href="WumpusWorldStudentManual.pdf" target="_blank">Wumpus World Student Manual</a>.
