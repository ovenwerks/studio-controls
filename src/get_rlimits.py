#!/usr/bin/python3.4

# getting rtprio requires python3.4 or greater
import resource


rtprio_limit = resource.getrlimit(resource.RLIMIT_RTPRIO)
# this works too..
'''rtprio_limit=resource.getrlimit(14)'''

memlock_limit = resource.getrlimit(resource.RLIMIT_MEMLOCK)
# This works too..
'''memlock_limit=resource.getrlimit(8)'''

# memlock -1 means unlimited
print(rtprio_limit, memlock_limit)
