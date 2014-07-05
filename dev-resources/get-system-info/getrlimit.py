#!/usr/bin/python3.4

# getting rtprio requires python3.4 or greater
import resource

rtprio_limit=resource.getrlimit(resource.RLIMIT_RTPRIO)
memlock_limit=resource.getrlimit(resource.RLIMIT_MEMLOCK)

print(rtprio_limit)
print(memlock_limit)
