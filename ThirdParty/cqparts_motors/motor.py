# base motor class
#

# 2018 Simon Kirkby obeygiantrobot@gmail.com

import cqparts

# base motor class
# TODO lift all motor things up to here

class Motor(cqparts.Assembly):

    def mount_points(self):
        raise NotImplementedError("mount_points function not implemented")

    def get_shaft(self):
        raise NotImplementedError("get_shaft function not implemented")

