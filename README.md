# Blender_Particle
Package for Blender to represent data from a 3D Numpy Array (Matrix).

The system is made to work with 3D matrix with the following structure:

Matrix[number_of_state][number_of_particle][axis]

number_of_states = The simulation can have multiple states, each of them have their own particle points to place.
number_of_particle= Total amount of particles that had been generated in the data simulation, 
                    could differ from the amout of particles that will be used inside of the blender sampling. 
                    (The example 3dData.3d have 10000 particles for each step)
axis = Each particle has x, y, and z info for being placed in the grid, also have a fourth value with probability that gives more info
      to the render simulation.
      
Example:
Matrix[0][0][0]= x position of the particle 0 of the state 0
Matrix[0][0][1]= y position of the particle 0 of the state 0
Matrix[0][0][2]= z position of the particle 0 of the state 0
Matrix[0][0][3]= probability of the particle 0 of the state 0
