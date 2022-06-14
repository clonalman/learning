# Simple example
from redistimeseries.client import Client
rts = Client()
rts.create('test', labels={'Time':'Series'})
rts.add('test', 1, 1.12)
rts.add('test', 2, 1.12)
rts.get('test')
rts.incrby('test',1)
rts.range('test', 0, -1)
rts.range('test', 0, -1, aggregation_type='avg', bucket_size_msec=10)
rts.range('test', 0, -1, aggregation_type='sum', bucket_size_msec=10)
rts.info('test').__dict__

# Example with rules
rts.create('source', retention_msecs=40)
rts.create('sumRule')
rts.create('avgRule')
rts.createrule('source', 'sumRule', 'sum', 20)
rts.createrule('source', 'avgRule', 'avg', 15)
rts.add('source', '*', 1)
rts.add('source', '*', 2)
rts.add('source', '*', 3)
rts.get('sumRule')
rts.get('avgRule')
rts.info('sumRule').__dict__