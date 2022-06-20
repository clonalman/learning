from crontab import CronTab
import os


def job_mootdx_remove(comment):
    for job in cron.find_comment(comment):
        cron.remove(job)


def job_mootdx_quotes(cron: CronTab):
    job_mootdx_remove('mootdx_quotes')
    job = cron.new(command='sleep 3; python ' + os.getcwd() + '/mootdx_quotes.py', comment='mootdx_quotes')
    job.setall("15 9 */1 * *")


def job_mootdx_stocks(cron: CronTab):
    job_mootdx_remove('mootdx_stocks')
    job = cron.new(command='python ' + os.getcwd() + '/mootdx_stocks.py', comment='mootdx_stocks')
    job.setall("30 15 */1 * *")


if __name__ == '__main__':
    with CronTab(user='root') as cron:
        job_mootdx_stocks(cron)
        job_mootdx_quotes(cron)
