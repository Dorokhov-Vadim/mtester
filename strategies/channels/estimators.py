from strategies.channels.channel import Channel, Line


class HoldChannelEstimator:
    def __init__(self, channel: Channel):
        self.min_lows_count = 2
        self.min_highs_count = 2
        self.min_bounce = 0
        self.on_line_interval = 0
        self.min_start_lag = 0
        self.channel: Channel = channel

    def is_low_channel(self) -> bool:
        low_line: Line = self.channel.low_line
        ch: Channel = self.channel
        start_low = ch.data[0].low
        model_low = low_line.coef * ch.start_candle_index + low_line.intercept
        lag = start_low - model_low
        if lag < self.min_start_lag:
            return False
        i = ch.start_candle_index
        bounces = 0
        bounced = False
        for candle in ch.data:
            if abs(candle.low - (low_line.coef * i + low_line.intercept)) < self.on_line_interval and not bounced:
                bounced = True
                # print(i)
            if candle.high - (low_line.coef * i + low_line.intercept) > self.min_bounce and bounced:
                bounces = bounces + 1
                bounced = False
            i = i + 1
        # print(bounces)
        if self.min_lows_count <= bounces:
            return True
        else:
            return False

    def is_high_channel(self) -> bool:
        high_line: Line = self.channel.high_line
        ch: Channel = self.channel
        start_high = ch.data[0].high
        model_high = high_line.coef * ch.start_candle_index + high_line.intercept
        lag = model_high - start_high
        if lag < self.min_start_lag:
            return False
        i = ch.start_candle_index
        bounces = 0
        bounced = False
        for candle in ch.data:
            if abs((high_line.coef * i + high_line.intercept) - candle.high) < self.on_line_interval and not bounced:
                bounced = True
                # print(i)
            if (high_line.coef * i + high_line.intercept) - candle.low > self.min_bounce and bounced:
                bounces = bounces + 1
                bounced = False
            i = i + 1
        # print(bounces)
        if self.min_highs_count <= bounces:
            return True
        else:
            return False
