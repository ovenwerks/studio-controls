#include <sys/time.h>
#include <sys/resource.h>
#include <unistd.h>
#include <stdio.h>

int main ()
{
	struct rlimit rl;
	getrlimit (RLIMIT_RTPRIO, &rl);
	printf("%lld\n", (long long int)rl.rlim_cur);
	return 0;
}
