from preprocessing import Space_data

event_path = '/data_pool_1/FIFA_WC_2022/Event Data'
tracking_path = '/data_pool_1/FIFA_WC_2022/Tracking Data'
out_path = '/home/c_yeung/workspace6/python/openstarlab/PreProcessing/test/sports/space_data'

Space_data(data_provider='fifa_wc_2022',
           event_data_path=event_path,
           tracking_data_path=tracking_path,
           testing_mode=True,
           out_path=out_path
           ).preprocessing()