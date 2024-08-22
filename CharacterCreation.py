from Utils.Math import game_math

# There will be a sort of convention to follow when creating a custom character or even an AliveEntity in the first place

# From now on the word "players" and such variations will be an alias for humanoid living entities in the general_manager

# first of all players need some sort of head
# secondly they all need a sort of body and appendages
# everything will be centered around the middle point of the body
# so the body will always be coordinate <0,0>
# making an example as a sort of sanity check:
# Player:
# - Body:
#    - Parent: None
#    - Position: <0,0>
#    - Rotation: 0 Radians
#    - Image path is ...\Images\...\.png
# - Head:
#    - Parent: Body
#    - Position: <0,3>
#    - Rotation: 0 Radians
#    - Image path : ....
# - Left Thigh:
#    - Parent: Body
#    - Position: <-2,-3>
#    - Rotation: 0 Radians
#    - Image Path :  ....png
# - Right Thigh:
#    - Parent: Body
#    - Position: <2,-3>
#    - Rotation: 0 Radians
#    - Image Path: ...png
