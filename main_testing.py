import simpy
import sys
sys.path #sometimes need this to refresh the path
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

import Asset_machine as Machine
import Event_job_creation
import Event_breakdown_creation
import heterogeneity_creation
import validation

class shopfloor:
    def __init__(self,env,span,m_no,**kwargs):
        # STEP 1: create environment for simulation and control parameters
        self.env=env
        self.span = span
        self.m_no = m_no
        self.m_list = []

        # STEP 2: create instances of machines
        for i in range(m_no):
            expr1 = '''self.m_{} = Machine.machine(env, {}, print = 0)'''.format(i,i) # create machines
            exec(expr1)
            expr2 = '''self.m_list.append(self.m_{})'''.format(i) # add to machine list
            exec(expr2)

        # STEP 3: initialize the initial jobs, distribute jobs to workcenters
        # env, span, machine_list, workcenter_list, number_of_jobs, pt_range, due_tightness, E_utliz, print
        self.job_creator = Event_job_creation.creation\
        (self.env, self.span, self.m_list, [1,50], 3, 0.9, print = 0)
        self.job_creator.initial_output()

        # STEP 4: initialize all machines
        for i in range(m_no):
            expr3 = '''self.m_{}.initialization(self.m_list,self.job_creator)'''.format(i) # initialize all machines
            exec(expr3)

        # STEP 5: check if need to reset sequencing rule
        if 'sequencing_rule' in kwargs:
            print("Taking over: machines use {} sequencing rule".format(kwargs['sequencing_rule']))
            for m in self.m_list:
                sqc_expr = "m.job_sequencing = sequencing." + kwargs['sequencing_rule']
                try:
                    exec(sqc_expr)
                except:
                    print("WARNING: Rule assigned is invalid !")
                    raise Exception

    # FINAL STEP: start the simulaiton
    def simulation(self):
        self.env.run()

# create the environment instance for simulation
env = simpy.Environment()
# create the shop floor instance
# the command of startig the simulation is included in shopfllor instance, run till there's no more events
span = 2000
spf = shopfloor(env, span, 10, sequencing_rule="FIFO")
spf.simulation()
# information of job sequence, processing time, creation, due and tardiness
spf.job_creator.final_output()
for m in spf.m_list:
    print(m.cumulative_run_time/span)
