from motor import Motor
import time
import random




motor = Motor(id="001", target_rpm=4000)
motor.start()

for i in range(100):
    # motor.update_action(random.sample([0,1],1)[0])

    # action = [random.random()]

    action = [1]
    print(action)
    motor.update_action(action)

    print(motor.get_states())
    time.sleep(1)


