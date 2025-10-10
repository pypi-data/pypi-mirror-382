try:
    # noinspection PyShadowingBuiltins
    from printlog import printlog as print
except ImportError:
    pass

try:
    import CONFIG_CV_SERVER
    is_Server = True
except ImportError:
    is_Server = False

try:
    import CONFIG_CV_LIVE_IMG
    useLiveImg = True
except ImportError:
    useLiveImg = False

try:
    from CONFIG_CV_ROBOT import robot_URL
    is_Robot = True
except ImportError:
    is_Robot = False
    robot_URL = "0.0.0.0"

print("CV Robot version 0.4.3")
if is_Robot:
    print("Running on robot...")
elif is_Server:
    print("Running on server...")
else:
    print("Running in emulation mode...")