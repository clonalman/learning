from crontab import CronTab
import os


def job_mootdx_remove(comment):
    for job in cron.find_comment(comment):
        cron.remove(job)


def job_mootdx_quotes(cron: CronTab):
    job_mootdx_remove('mootdx_quotes')
    job = cron.new(command='sleep 3; python ' + os.getcwd() + '/mootdx_quotes.py', comment='mootdx_quotes')
    job.setall("* * * * *")


if __name__ == '__main__':
    with CronTab(user='root') as cron:
        job_mootdx_quotes(cron)
