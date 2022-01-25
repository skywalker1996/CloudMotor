import math
import gym_electric_motor as gem
from gym_electric_motor.reference_generators import ConstReferenceGenerator
from utils import *
from gym_electric_motor.visualization import MotorDashboard
import matplotlib.pylab as plt
from simple_pid import PID
from gym_electric_motor.physical_systems.mechanical_loads import PolynomialStaticLoad
import math
from threading import Thread



class Motor:
    def __init__(self, id, rpm=4000):
        self._id = id

        self._u_supply = 220
        self._nominal_rpm = rpm
        self._nominal_i = 200

        self._nominal_omega = round((self._nominal_rpm * 2 * math.pi) / 60, 2)

        self._limit_factor = 3
        self._limit_rpm = self._limit_factor * self._nominal_rpm
        self._limit_omega = round((self._limit_rpm * 2 * math.pi) / 60, 2)
        self._limit_i = self._limit_factor * self._nominal_i

        # nominal and absolute state limitations
        self._nominal_values = dict(
            omega=self._nominal_omega,
            i=self._nominal_i,
            u=self._u_supply
        )

        self._limit_values = dict(
            omega=self._limit_omega,
            i=self._limit_i,
            u=self._u_supply
        )

        # sampling interval
        self._tau = 1e-5

        # define maximal episode steps
        self._max_eps_steps = 10000000000

        self._motor_initializer = {'random_init': 'uniform', 'interval': [[0, 230], [0, 230], [-math.pi, math.pi]]}

        self._state_filter = ['omega', 'i']
        self._motor_dashboard = MotorDashboard(state_plots=['i', 'omega'], reward_plot=True)

        self._my_poly_static_load = PolynomialStaticLoad(
            load_parameter=dict(a=1e-3, b=1e-4, c=0.0, j_load=1e-3),
            limits=dict(omega=self._limit_omega),  # rad / s
        )

        self._env = gem.make(  # define a PMSM with discrete action space
            "Finite-SC-SeriesDc-v0",
            # visualize the results
            visualization=self._motor_dashboard,

            # parameterize the PMSM and update limitations
            motor=dict(
                # motor_parameter=motor_parameter,
                limit_values=self._limit_values,
                nominal_values=self._nominal_values,
                # motor_initializer=motor_initializer,
            ),
            # define the random initialisation for load and motor
            # load=dict(
            #     load_initializer={'random_init': 'uniform'},
            # ),
            # reward_function=reward_function,
            supply=dict(u_nominal=self._u_supply),

            # define the duration of one sampling step
            # supply = 'IdealVoltageSupply',
            tau=self._tau,

            # load=my_poly_static_load,

            converter='Finite-2QC',

            ode_solver='euler',

            state_filter=self._state_filter,
            reference_generator=ConstReferenceGenerator(reference_state='omega',
                                                        reference_value=self._nominal_omega / self._limit_omega)
        )

        self._states = None
        self._references = None
        self._processed_states = None

        self._action = 0

        self.worker = Thread(target=self.motor_simulation, args=())
        self.worker.daemon = True

    def start(self):
        self.worker.start()

    def motor_simulation(self):

        done = True
        while (True):
            if done:
                # Reset the environment
                # This is required initally or after an episode end due to a constraint violation in the env.
                self._states, self._references = self._env.reset()

            # visualize environment. Red vertical lines indicate a constraint violation and therefore, a reset environment.
            # self._env.render()

            # action = env.action_space.sample()
            action = self._action


            (self._states, self._references), rewards, done, _ = self._env.step(action)
            self._processed_states = self.process_states(self._states)
            # print_state(self.state_filter, states, self.limit_values)

    def get_states(self):
        return self._processed_states

    def get_nominal_values(self):
        return self._nominal_values

    def get_limit_values(self):
        return self._limit_values

    def update_action(self, action):
        self._action = action

    def process_states(self, states):
        result = {}
        for i in range(len(self._state_filter)):
            value = states[i]
            value *= self._limit_values[self._state_filter[i]]
            result[self._state_filter[i]] = value

            if self._state_filter[i] == KEY_OMEGA:
                result[KEY_SPEED] = omega_to_speed(value)

        return result
