"""
Example that uses the gradient descent and the Newton method for optimization.

The goal is to find an x for which flow.execute returns a given y.
"""

import numpy as np
import bimdp
from newton import NewtonNode

## paramters
n_iterations = 3
show_inspection = True

## create and train the flow
sfa_node = bimdp.nodes.SFA2BiNode(input_dim=4*4, output_dim=5)
switchboard = bimdp.hinet.Rectangular2dBiSwitchboard(
                                          in_channels_xy=8, 
                                          field_channels_xy=4, 
                                          field_spacing_xy=2)
flownode = bimdp.hinet.BiFlowNode(bimdp.BiFlow([sfa_node]))
sfa_layer = bimdp.hinet.CloneBiLayer(flownode,
                                     switchboard.output_channels)
flow = bimdp.BiFlow([switchboard, sfa_layer])
train_data = [np.random.random((10, switchboard.input_dim))
             for _ in range(3)]
flow.train([None, train_data])

## add the Newton optimization to the flow
sender_node = bimdp.nodes.SenderBiNode(node_id="sender", recipient_id="newton")
newton_node = NewtonNode(sender_id="sender", input_dim=sfa_layer.output_dim,
                         node_id="newton")
flow = sender_node + flow + newton_node

## now do the optimization
# pick a random goal y that can actually be generated by the flow
x_goal = np.random.random((2, switchboard.input_dim))
goal_y, msg = flow.execute(x_goal)
# pick a random starting point
x_start = np.random.random((2, switchboard.input_dim))
y_start = flow.execute(x_start)
# do the optimization
msg = {"method": "newton", "n_iterations": n_iterations, "x_start": x_start}
if show_inspection:
    _, (x, msg) = bimdp.show_execution(flow, x=goal_y, msg=msg, target="newton")
else:
    x, msg = flow.execute(goal_y, msg, "newton")

## compare the error values:
y, _ = flow.execute(x)
print ("errors before optimization : " +
       str(np.sum((y_start - goal_y)**2, axis=1)))
print ("errors after optimization  : " +
       str(np.sum((y - goal_y)**2, axis=1)))
