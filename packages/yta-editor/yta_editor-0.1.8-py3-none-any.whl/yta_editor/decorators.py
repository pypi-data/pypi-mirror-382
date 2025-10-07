from functools import wraps


def with_t_adjusted_to_media(
    method
):
    """
    Get the real 't' time moment based on the
    video 'start' and 'end'. If they were 
    asking for the t=0.5s but our video was
    subclipped to [1.0, 2.0), the 0.5s must be
    actually the 1.5s of the video because of
    the subclipped time range.

    The formula:
    - `t + self.start`
    """
    @wraps(method)
    def wrapper(
        self,
        t,
        *args,
        **kwargs
    ):
        t += self.start
    
        print(f'The video/audio real t is {str(float(t))}')
        if t >= self.end:
            raise Exception(f'The "t" ({str(t)}) provided is out of range. This video/audio lasts from [{str(self.start)}, {str(self.end)}).')
        
        return method(self, t, *args, **kwargs)
    
    return wrapper
