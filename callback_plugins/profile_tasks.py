import datetime
import os
import time


class CallbackModule(object):
    """
    A plugin for timing tasks
    """
    def __init__(self):
        self.stats = {}
        self.previous = None
        self.previous_task_start = time.time()

    def playbook_on_task_start(self, name, is_conditional):
        """
        Logs the start of each task
        """

        if os.getenv("ANSIBLE_PROFILE_DISABLE") is not None:
            return

        current_task_start = time.time()

        if self.previous is not None:
            # Record the running time of the last executed task
            delta_t = current_task_start - self.previous_task_start

            if self.previous not in self.stats:
                self.stats[self.previous] = {
                    'occurences': 1,
                    'time': delta_t
                }
            else:
                self.stats[self.previous]['occurences'] += 1
                self.stats[self.previous]['time'] += delta_t

        # Record the start time of the current task
        self.previous = name
        self.previous_task_start = current_task_start

    def playbook_on_stats(self, stats):
        """
        Prints the timings
        """

        if os.getenv("ANSIBLE_PROFILE_DISABLE") is not None:
            return

        # Record the timing of the very last task
        self.playbook_on_task_start(self.previous, False)

        # Sort the tasks by their running time
        results = sorted(
            self.stats.items(),
            key=lambda value: value[1]['time'],
            reverse=True,
        )

        # Just keep the top 10
        results = results[:10]

        # Print the timings
        for name, stats in results:
            if stats['occurences'] > 1:
                name = '{0} ({1}x)'.format(name, stats['occurences'])

            print(
                "{0:-<70}{1:->9}".format(
                    '{0} '.format(name),
                    ' {0:.02f}s'.format(stats['time']),
                )
            )

        total_seconds = sum([stats['time'] for name, stats in self.stats.items()])
        print("\nPlaybook finished: {0}, {1} total tasks.  {2} elapsed. \n".format(
                time.asctime(),
                len(self.stats.items()),
                datetime.timedelta(seconds=(int(total_seconds)))
                )
          )
