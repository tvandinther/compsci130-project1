### COMPSCI 130, Semester 01 2019
### Project One - Virus
### Tom van Dinther

import turtle
import random
import math

## Global Constants
viruses = {"virus_1":
               {"colour": "red",
                "duration": 100
                },
           "virus_2":
               {"colour": "yellow",
                "duration": 200
                }
           }
current_virus = "virus_1"
healthy_colour = "green"

class Virus:
    '''
    colour: A string denoting the colour of the specefied virus
    duration: An integer denoting the number of ticks a virus is valid for until removed
    '''
    def __init__(self, parameters):
        self.colour = parameters["colour"]
        self.duration = parameters["duration"]
        
class Person:
    '''
    world_size: A pass-through tuple (x, y) of the World canvas size.
    virus: Stores a Virus instance if infected. Initialises to None for healthy.
    radius: An integer or float of the radius of the representative dot on the canvas.
    colour: A string denoting the colour of the dot. Initialises to global constant for healthy.
    location: Tuple of (x, y) coordinates.
    destination: Tuple of (x, y) coordinates.
    speed: An integer or float of the distance a Person moves each tick.
    unit_vector: A tuple of delta (x, y) coordinates a Person moves each tick (factors in the speed attribute).
    '''
    def __init__(self, world_size):
        self.world_size = world_size
        self.virus = None
        self.radius = 7
        self.colour = healthy_colour
        self.location = self._get_random_location()
        self.destination = self._get_random_location()
        self.speed = self.radius / 2
        self.unit_vector = self._get_unit_vector()
        
        self.draw()
         
    def _get_random_location(self):
        '''This method returns a tuple of (x, y) coordinates of random values within 1 radius less of the world_size.'''
        
        return tuple([round(((coordinate - 2 * self.radius)* random.random()) - (coordinate // 2 - self.radius)) for coordinate in self.world_size])
    
    def _get_unit_vector(self):
        '''This method returns the unit vector of the Person multiplied by its speed attribute.'''
        
        dx = self.destination[0] - self.location[0]
        dy = self.destination[1] - self.location[1]
        magnitude = math.hypot(dx, dy) #math.hypot is about 2x faster than verbose pythagoras theorem as per timeit module
        if magnitude == 0: #deals with unlikely edge case where new random destination is the same as the current location
            return (0, 0)
        return (self.speed * dx / magnitude, self.speed * dy / magnitude)
    
    def draw(self):
        '''This method commands the turtle to draw a dot at the current location of the Person.'''
        
        turtle.goto(self.location)
        turtle.dot(self.radius * 2, self.colour)

    def collides(self, other):
        '''This method returns a boolean where True defines a collision between self and other.
        
        Arguments:
            other: This argument is expected to be an instance of the Person class.
            
        Opting for execution efficiency over readability as this method is called multiple times each tick.'''
        
        magnitude_squared = (self.location[0] - other.location[0]) * (self.location[0] - other.location[0]) + (self.location[1] - other.location[1]) * (self.location[1] - other.location[1])
        #x * x is faster than x ** 2
        return  magnitude_squared < (self.radius + other.radius) * (self.radius + other.radius)
        #squaring the sum of the radii prevents the usage of math.sqrt which slows down the simulation 

    def collision_list(self, list_of_others):
        '''This method returns a list of Person instances the current Person is colliding with.'''
        
        return [person for person in list_of_others if self.collides(person)]

    def infect(self, virus):
        '''This method passes a Virus instance into the virus attribute if there is no other virus present
        and changes the colour attribute to that of the virus.
            
        Arguments:
            virus: This argument is expected to be an instance of the Virus class.'''
        
        if not self.virus:
            self.virus = virus
            self.colour = virus.colour #setting the colour as an attribute in the infect() method instead of the draw() method ensures
            #that this action is only taken once and prevents status checks

    def reached_destination(self):
        ''' This method returns a boolean where True defines that the current location is within 1 radius of the set destination.

        Opted for verbose nested conditions as they are faster than evaluating using all([]).'''
        
        if abs(self.destination[0] - self.location[0]) < self.radius: #check x first
            if abs(self.destination[1] - self.location[1]) < self.radius: #then check y
                return True
            return False
        else:
            return False

    def progress_illness(self):
        '''This method reduces the duration of the virus by 1 each tick if the Person is infected. If the duration reaches 0 it calls the cured() method.'''
        
        if self.virus:
            if self.virus.duration == 0:
                self.cured()
            else:
                self.virus.duration -= 1

    def update(self, spatial_hashtable):
        '''This method is called each tick to update the state of the Person.
        
        Arguments:
            spatial_hashtable: The Spatial_Hashtable object created in the World class'''
        
        self.move(spatial_hashtable)
        self.progress_illness()
        
    def move(self, spatial_hashtable):
        '''This method updates the location coordinates of the Person by its speed factored unit vector.
        If the destination has been reached it also updates the destination and unit_vector attributes with new values.
        
        Arguments:
            spatial_hashtable: The Spatial_Hashtable object created in the World class'''
        
        if self.reached_destination():
            self.destination = self._get_random_location()
            self.unit_vector = self._get_unit_vector()
        x = self.location[0] + self.unit_vector[0] #change location by unit vector
        y = self.location[1] + self.unit_vector[1]
        self.location = (x, y) 
        #update spatial hash
        key = (int(x/spatial_hashtable.cell_size), int(y/spatial_hashtable.cell_size))
        spatial_hashtable.update(key, self)
 
    def cured(self):
        '''This method updates the attributes to show a healthy Person.'''
        
        self.virus = None
        self.colour = healthy_colour

class Spatial_Hashtable:
    '''
    data: The dictionary which will store an array of Person classes by grid location
    cells_divisons_width: An integer which determines the number of divisions along the world_size width the spatial grid has
    '''
    def __init__(self, world_size):
        self.data = {}
        self.cells_divisons_width = world_size[0]/14 #more divisons compute faster
        #but ensure that the cell_size is larger than the diameter of the dots for accurate detection
        self.cell_size = math.ceil(world_size[0] / self.cells_divisons_width)
        
        #This code pre-populates a dictionary with all grid keys
        for x in range(int((0 - world_size[0] // 2) // self.cell_size) - 1, int((0 + world_size[0] // 2) // self.cell_size) + 2):
            for y in range(int((0 - world_size[1] // 2) // self.cell_size) - 1, int((0 + world_size[1] // 2) // self.cell_size) + 2):
                self.data[(x, y)] = []
        
    def update(self, key, value):
        '''This method updates the hashtable with a key-value pair
        
        Arguments:
            key: Tuple of detection cell coordinate
            value: The person instance that is being updated'''
        
        self.data[key].append(value)
        #add to adjacent cells
        self.data[(key[0] + 1, key[1])].append(value)
        self.data[(key[0] - 1, key[1])].append(value)
        self.data[(key[0], key[1] + 1)].append(value)
        self.data[(key[0], key[1] - 1)].append(value)
        #and corner cells for good measure
        self.data[(key[0] + 1, key[1] + 1)].append(value)
        self.data[(key[0] + 1, key[1] - 1)].append(value)
        self.data[(key[0] - 1, key[1] + 1)].append(value)
        self.data[(key[0] - 1, key[1] - 1)].append(value)
        #with a cell size the same as the radius of the dot there is a bumper of cells around each dot
        
        
    def clear(self):
        '''This method deletes the contents of all lists in the hashtable. It keeps the keys intact - crucial for preventing KeyError'''
        
        for value in self.data.values():
            del value[:]

class World:
    '''
    size: A tuple of (x, y) lengths denoting the size of the canvas which will contain the simulation
    hours: An integer denoting the lapsed ticks of the current simulation
    population: An integer to determine the amount of Person instances the simulation will run
    people: A list which will contain Person instances with a length of the population attribute
    '''
    def __init__(self, width, height, n):
        self.size = (width, height)
        self.hours = 0
        self.population = n
        self.people = []
        self.spatial_hashtable = Spatial_Hashtable(self.size)
        
        for i in range(self.population):
            self.add_person()
    
    def add_person(self):
        '''This method adds a Person instance to the list of people.'''
        
        self.people.append(Person(self.size))

    def infect_person(self):
        '''This method infects a random Person instance with a Virus instance instantiated with parameters from the viruses global constant
        given by the current_virus global constant.'''
        
        infect_index = random.randrange(0, self.population)
        self.people[infect_index].infect(Virus(viruses[current_virus]))

    def cure_all(self):
        '''This method removes Virus objects from all Persons in the simulation.'''
        
        for person in self.people:
            person.cured()

    def update_infections_slow(self):
        '''This method calls for collision checks between all infected Persons and all other Persons and infects them with a Virus instance
        instantiated with parameters from the viruses global constant given by the current_virus global constant.'''
        
        for person in self.people:
            if person.virus: #only checks collisions for infected people
                for infected in person.collision_list(self.people):
                    infected.infect(Virus(viruses[current_virus]))
                    
    def update_infections_fast(self):
        '''This method is a faster implementation of update_infections_slow. It implements a spatial hashtable to localise collision checks.'''
        
        infected_list = []
        for cell in self.spatial_hashtable.data.values():
            for person in cell:
                if person.virus: #only checks collisions for infected people
                    for infected in person.collision_list(cell):
                        infected_list.append(infected)
        #saving the infected to a list and passing the Virus at the end prevents overlapping dots receiving the infection all at once
        #essentially forcing a tick by tick ripple effect when the frame is crowded
        for item in infected_list:
            item.infect(Virus(viruses[current_virus]))
    
    def simulate(self):
        '''This method is called each tick and updates all simulated variables.'''
        
        self.spatial_hashtable.clear()
        self.hours += 1
        for person in self.people:
            person.update(self.spatial_hashtable)
        self.update_infections_fast()

    def draw(self):
        '''This method calls all GUI methods to update as well as commanding the turtle to update its own GUI elements.'''
        
        width, height = self.size
        turtle.clear()
        
        #Draw People
        for person in self.people:
            person.draw()
        
        #Draw Frame
        turtle.goto(-1 * width // 2, -1 * height // 2)
        turtle.pendown()
        for i in range(2):
            turtle.forward(height)
            turtle.right(90)
            turtle.forward(width)
            turtle.right(90)
        turtle.penup()
        
        #Draw Text
        turtle.goto(-1 * width // 2, height // 2)
        turtle.write("Hours: {}".format(self.hours))
        turtle.goto(0, height // 2)
        turtle.write("Infected: {}".format(self.count_infected()), align="center")
        turtle.penup()
        
    def count_infected(self):
        '''This method counts the number of Person instances with a Virus object.'''
        
        return len([person for person in self.people if person.virus])
    
#---------------------------------------------------------
#Should not need to alter any of the code below this line
#---------------------------------------------------------
class GraphicalWorld:
    """ Handles the user interface for the simulation

    space - starts and stops the simulation
    'z' - resets the application to the initial state
    'x' - infects a random person
    'c' - cures all the people
    """
    def __init__(self):
        self.WIDTH = 800
        self.HEIGHT = 600
        self.TITLE = 'COMPSCI 130 Project One'
        self.MARGIN = 50 #gap around each side
        self.PEOPLE = 200 #number of people in the simulation
        self.framework = AnimationFramework(self.WIDTH, self.HEIGHT, self.TITLE)
        
        self.framework.add_key_action(self.setup, 'z') 
        self.framework.add_key_action(self.infect, 'x')
        self.framework.add_key_action(self.cure, 'c')
        self.framework.add_key_action(self.toggle_simulation, ' ') 
        self.framework.add_tick_action(self.next_turn)
        
        self.world = None

    def setup(self):
        """ Reset the simulation to the initial state """
        print('resetting the world')        
        self.framework.stop_simulation()
        self.world = World(self.WIDTH - self.MARGIN * 2, self.HEIGHT - self.MARGIN * 2, self.PEOPLE)
        self.world.draw()
        
    def infect(self):
        """ Infect a person, and update the drawing """
        print('infecting a person')
        self.world.infect_person()
        self.world.draw()

    def cure(self):
        """ Remove infections from all the people """
        print('cured all people')
        self.world.cure_all()
        self.world.draw()

    def toggle_simulation(self):
        """ Starts and stops the simulation """
        if self.framework.simulation_is_running():
            self.framework.stop_simulation()
        else:
            self.framework.start_simulation()           

    def next_turn(self):
        """ Perform the tasks needed for the next animation cycle """
        self.world.simulate()
        self.world.draw()
        
## This is the animation framework
## Do not edit this framework
class AnimationFramework:
    """This framework is used to provide support for animation of
       interactive applications using the turtle library.  There is
       no need to edit any of the code in this framework.
    """
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.simulation_running = False
        self.tick = None #function to call for each animation cycle
        self.delay = 1 #smallest delay is 1 millisecond      
        turtle.title(title) #title for the window
        turtle.setup(width, height) #set window display
        turtle.hideturtle() #prevent turtle appearance
        turtle.tracer(0, 0) #prevent turtle animation
        turtle.listen() #set window focus to the turtle window
        turtle.mode('logo') #set 0 direction as straight up
        turtle.penup() #don't draw anything
        turtle.setundobuffer(None)
        self.__animation_loop()

    def start_simulation(self):
        self.simulation_running = True
        
    def stop_simulation(self):
        self.simulation_running = False

    def simulation_is_running(self):
        return self.simulation_running
    
    def add_key_action(self, func, key):
        turtle.onkeypress(func, key)

    def add_tick_action(self, func):
        self.tick = func

    def __animation_loop(self):
        try:
            if self.simulation_running:
                self.tick()
            turtle.ontimer(self.__animation_loop, self.delay)
        except turtle.Terminator:
            pass


gw = GraphicalWorld()
gw.setup()
turtle.mainloop() #Need this at the end to ensure events handled properly
