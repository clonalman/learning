from crontab import CronTab
import os


def job_mootdx_remove(comment):
    for job in cron.find_comment(comment):
        cron.remove(job)


def job_mootdx_quotes(cron: CronTab):
    job_mootdx_remove('python_mootdx_quotes')
    job = cron.new(command='nohup python ' + os.getcwd() + '/mootdx_quotes.py > ' + os.getcwd() + '/mootdx_quotes.log 2>&1 &', comment='python_mootdx_quotes')
    job.setall("15 9 */1 * *")


def job_mootdx_quotes_kill(cron: CronTab):
    job_mootdx_remove('kill_mootdx_quotes')
    job = cron.new(command='kill `cat ' + os.getcwd() + '/pids/mootdx_quotes.pid`', comment='kill_mootdx_quotes')
    job.setall("30 15 */1 * *")


def job_mootdx_stocks(cron: CronTab):
    job_mootdx_remove('python_mootdx_stocks')
    job = cron.new(command='nohup python ' + os.getcwd() + '/mootdx_stocks.py > ' + os.getcwd() + '/mootdx_stocks.log 2>&1 &', comment='python_mootdx_stocks')
    job.setall("30 15 */1 * *")


if __name__ == '__main__':
    with CronTab(user='root') as cron:
        job_mootdx_stocks(cron)
        job_mootdx_quotes(cron)
        job_mootdx_quotes_kill(cron)
