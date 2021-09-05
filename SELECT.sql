SELECT cast(close_time as timestamp) at time zone 'utc' at time zone 'america/caracas' close_time, close_pred
	FROM public."predict_ETHUSDT";