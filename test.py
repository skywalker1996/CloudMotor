import gym_electric_motor as gem
from gym_electric_motor.reference_generators import ConstReferenceGenerator
from utils import *
from gym_electric_motor.visualization import MotorDashboard
import matplotlib.pylab as plt
from simple_pid import PID
from gym_electric_motor.physical_systems.mechanical_loads import PolynomialStaticLoad

u_supply = 220
nominal_rpm = 4000
nominal_i = 200

nominal_omega = (nominal_rpm * 2 * math.pi) / 60

limit_factor = 3
limit_rpm = limit_factor * nominal_rpm
limit_omega = (limit_rpm * 2 * math.pi) / 60
limit_i = limit_factor * nominal_i

print(f"Create a pid controller with target omega = {nominal_omega}")
controller = PID(1, 0.1, 0.05, setpoint=nominal_omega)
controller.output_limits = (0, 1)

# nominal and absolute state limitations
nominal_values = dict(
    omega=nominal_omega,
    i=nominal_i,
    u=u_supply
)
limit_values = dict(
    omega=limit_omega,
    i=limit_i,
    u=u_supply
)

# sampling interval
tau = 1e-5

# define maximal episode steps
max_eps_steps = 10000000000

motor_initializer = {'random_init': 'uniform', 'interval': [[0, 230], [0, 230], [-math.pi, math.pi]]}

state_filter = ['omega', 'i']
motor_dashboard = MotorDashboard(state_plots=['i', 'omega'], reward_plot=True)

my_poly_static_load = PolynomialStaticLoad(
    load_parameter=dict(a=1e-3, b=1e-4, c=0.0, j_load=1e-3),
    limits=dict(omega=limit_omega),  # rad / s
)

# creating gem environment
env = gem.make(  # define a PMSM with discrete action space
    "Finite-SC-SeriesDc-v0",
    # visualize the results
    visualization=motor_dashboard,

    # parameterize the PMSM and update limitations
    motor=dict(
        # motor_parameter=motor_parameter,
        limit_values=limit_values,
        nominal_values=nominal_values,
        # motor_initializer=motor_initializer,
    ),
    # define the random initialisation for load and motor
    # load=dict(
    #     load_initializer={'random_init': 'uniform'},
    # ),
    # reward_function=reward_function,
    supply=dict(u_nominal=u_supply),
    # define the duration of one sampling step
    # supply = 'IdealVoltageSupply',
    tau=tau,

    # load=my_poly_static_load,

    converter='Finite-2QC',

    ode_solver='euler',

    state_filter=state_filter,
    reference_generator=ConstReferenceGenerator(reference_state='omega', reference_value=nominal_omega / limit_omega)
)

print(env.physical_system.state_names)
done = True
for _ in range(1000000):
    if done:
        # Reset the environment
        # This is required initally or after an episode end due to a constraint violation in the env.
        states, references = env.reset()
    # visualize environment. Red vertical lines indicate a constraint violation and therefore, a reset environment.
    env.render()
    # pick random control actions
    # action = env.action_space.sample()

    # action = round(controller(states[state_filter.index(OMEGA_PARAM)] * limit_omega))
    action = 0
    print(f"the action is {action}")
    # Execute one control cycle on the environment
    (states, references), rewards, done, _ = env.step(action)
    print_state(state_filter, states, limit_values)

plt.pause(0)
